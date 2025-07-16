// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medication', {
	generic_name: function(frm) {
		frm.set_value("abbr", frappe.get_abbr(frm.doc.generic_name))
	},
	refresh: function(frm) {
		frm.set_query("medication", "combinations", function() {
			return {
				filters: {
					is_combination: false
				}
			};
		});
		frm.set_query("price_list", function() {
			return {
				filters: {
					selling: true
				}
			};
		});

		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Browse Medication"),
				function () {
					frappe.route_options = {
						medication: frm.doc.name,
					};
					frappe.set_route("Tree", "Medication");
				},
			);
		}
	},
	onload: function (frm) {
		if (frm.is_new() && !frm.doc.price_list) {
			frappe.db.get_single_value("Selling Settings", "selling_price_list").then((price_list) => {
				if (price_list) {
					frm.set_value("price_list", price_list);
				}
			});
		}
	},
	price_list: function (frm) {
		if (!frm.is_new() && frm.doc.price_list && frm.doc.linked_items) {
			frm.doc.linked_items.forEach((row) => {
				mark_change_in_item(frm, row.doctype, row.name);
			});
		}
	}
});

frappe.ui.form.on('Medication Linked Item', {
	rate: function(frm, cdt, cdn) {
		mark_change_in_item(frm, cdt, cdn);
	},

	is_billable: function(frm, cdt, cdn) {
		mark_change_in_item(frm, cdt, cdn);
	},

	item_group: function(frm, cdt, cdn) {
		mark_change_in_item(frm, cdt, cdn);
	},

	description: function(frm, cdt, cdn) {
		mark_change_in_item(frm, cdt, cdn);
	},
})

let mark_change_in_item = function(frm, cdt, cdn) {
	if (!frm.doc.__islocal) {
		frappe.model.set_value(cdt, cdn, 'change_in_item', 1);
	}
};

let change_medication_code = function(doc) {
	let d = new frappe.ui.Dialog({
		title: __('Change Item Code'),
		fields: [
			{
				'fieldtype': 'Data',
				'label': 'Item Code',
				'fieldname': 'item_code',
				reqd: 1
			}
		],
		primary_action: function() {
			let values = d.get_values();

			if (values) {
				frappe.call({
					'method': 'healthcare.healthcare.doctype.medication.medication.change_item_code_from_medication',
					'args': {item_code: values.item_code, doc: doc},
					callback: function () {
						frm.reload_doc();
						frappe.show_alert({
							message: 'Item Code renamed successfully',
							indicator: 'green'
						});
					}
				});
			}
			d.hide();
		},
		primary_action_label: __('Change Item Code')
	});
	d.show();

	d.set_values({
		'item_code': doc.item_code
	});
};
