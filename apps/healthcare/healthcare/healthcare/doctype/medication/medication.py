# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.rename_doc import rename_doc
from frappe.utils import get_link_to_form


class Medication(Document):
	def after_insert(self):
		create_item_from_medication(self)

	def on_update(self):
		if self.linked_items:
			self.update_item_and_item_price()

	def validate(self):
		if not self.price_list and self.linked_items:
			price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
			if price_list:
				self.price_list = price_list
			else:
				frappe.throw(
					_(
						f"Please select a Price List for adding Item Price or set the Default Selling Price List in {get_link_to_form('Selling Settings', 'Selling Settings')}"
					)
				)

		if self.linked_items:
			for item in self.linked_items:
				exist_medication = frappe.db.get_value(
					"Medication Linked Item",
					{"item": item.item_code, "parent": ("!=", self.name)},
					"parent",
				)
				if exist_medication:
					frappe.throw(
						_(
							"Item <b>{}</b> has been already used in <b><a href='/app/medication/{}'>Medication</a></b>"
						).format(item.item_code, exist_medication)
					)

	def update_item_and_item_price(self):
		for item in self.linked_items:
			if not item.item:
				insert_item(self, item)
			else:
				if item.is_billable:
					if item.change_in_item:
						item_doc = frappe.get_doc("Item", {"name": item.item_code})
						item_doc.item_name = item.item_code
						item_doc.item_group = item.item_group
						item_doc.description = item.description
						item_doc.stock_uom = item.stock_uom
						item_doc.manufacturer = item.manufacturer
						item_doc.brand = item.brand
						item_doc.disabled = 0
						item_doc.save(ignore_permissions=True)
						if item.rate:
							item_price = frappe.db.exists(
								"Item Price", {"item_code": item.item_code, "price_list": self.price_list}
							)
							if not item_price:
								if item.item_code:
									make_item_price(item.item_code, item.rate, self.price_list)
							else:
								item_price = frappe.get_doc("Item Price", item_price)
								item_price.item_name = item.item_code
								item_price.price_list_rate = item.rate
								item_price.price_list = self.price_list
								item_price.save()

				else:
					frappe.db.set_value("Item", item.item_code, "disabled", 1)

				frappe.db.set_value("Medication Linked Item", item.name, "change_in_item", 0)
		self.reload()


def create_item_from_medication(doc):
	for item in doc.linked_items:
		insert_item(doc, item)
	doc.reload()


def insert_item(doc, item):
	if not frappe.db.exists("Item", item.item_code):
		item_doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item.item_code,
				"item_name": item.item_code,
				"item_group": item.item_group,
				"description": item.item_code,
				"is_sales_item": 1,
				"is_stock_item": 1,
				"disabled": 0 if item.is_billable and not doc.disabled else 1,
				"stock_uom": item.stock_uom or frappe.db.get_single_value("Stock Settings", "stock_uom"),
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)
	else:
		item_doc = frappe.get_doc("Item", item.item_code)
		if item_doc.stock_uom != item.stock_uom:
			frappe.throw(
				_("Cannot link existing Item Code {}, UOM {} does not match with Item Stock UOM").format(
					item.item_code, item.stock_uom, item_doc.stock_uom
				)
			)
		item_doc.item_name = item.item_code  # also update the name and description of existing item
		item_doc.description = item.description

	make_item_price(item_doc.name, item.rate, doc.price_list)
	frappe.db.set_value("Medication Linked Item", item.name, "item", item.item_code)


def make_item_price(item, item_price, price_list):
	frappe.get_doc(
		{
			"doctype": "Item Price",
			"price_list": price_list,
			"item_code": item,
			"price_list_rate": item_price,
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)


@frappe.whitelist()
def change_item_code_from_medication(item_code, doc):
	doc = frappe._dict(json.loads(doc))

	if frappe.db.exists("Item", {"item_code": item_code}):
		frappe.throw(_("Item with Item Code {0} already exists").format(item_code))
	else:
		rename_doc("Item", doc.item_code, item_code, ignore_permissions=True)
		frappe.db.set_value("Medication", doc.name, "item_code", item_code)
	return


@frappe.whitelist()
def get_children(parent=None, is_root=False, **filters):
	if not parent or parent == "Medication":
		frappe.msgprint(_("Please select a Medication"))
		return

	if parent:
		frappe.form_dict.parent = parent

	if frappe.form_dict.parent:
		medication_doc = frappe.get_cached_doc("Medication", frappe.form_dict.parent)
		frappe.has_permission("Medication", doc=medication_doc, throw=True)

		medication_items = frappe.get_all(
			"Medication Linked Item",
			fields=["item as item_code", "rate"],
			filters=[["parent", "=", frappe.form_dict.parent]],
			order_by="idx",
		)

		item_names = tuple(d.get("item_code") for d in medication_items)

		items = frappe.get_list(
			"Item",
			fields=["image", "description", "name", "stock_uom", "item_name"],
			filters=[["name", "in", item_names]],
		)  # to get only required item dicts

		for medication_item in medication_items:
			# extend medication_item dict with respective item dict
			medication_item.update(
				# returns an item dict from items list which matches with item_code
				next(item for item in items if item.get("name") == medication_item.get("item_code"))
			)
			medication_item.image = frappe.db.escape(medication_item.image)
			medication_item.currency = frappe.db.get_single_value("Global Defaults", "default_currency")

		return medication_items
