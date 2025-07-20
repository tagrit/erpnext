# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt


from collections import OrderedDict

import frappe
from erpnext import get_company_currency
from frappe import _, msgprint, qb
from frappe.query_builder import Criterion


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    entries = get_entries(filters)
    item_details = get_item_details()
    data = []

    company_currency = get_company_currency(filters.get("company"))

    grouped = OrderedDict()

    for d in entries:
        row = frappe._dict()
        grouped.setdefault(
            d.duration, [frappe._dict(duration=d.duration, indent=0)]
        ).append(row.update({"indent": 1}))

        if d.stock_qty > 0 or filters.get("show_return_entries", 0):
            row[frappe.scrub(filters["doc_type"])] = d.name
            row.customer = d.customer
            row.territory = d.territory
            row.warehouse = d.warehouse
            row.posting_date = d.posting_date
            row.item_code = d.item_code
            row.item_group = item_details.get(d.item_code, {}).get("item_group")
            row.brand = item_details.get(d.item_code, {}).get("item_group")
            row.stock_qty = d.stock_qty
            row.base_net_amount = d.base_net_amount
            row.sales_person = d.sales_person
            row.allocated_percentage = d.allocated_percentage
            row.contribution = d.stock_qty * d.allocated_percentage / 100
            row.contribution_amt = d.contribution_amt
            row.company_currency = d.company_currency
            row.currency = company_currency

    for _ in grouped.values():
        data.extend(_)

    return columns, data


def get_columns(filters):
    if not filters.get("doc_type"):
        msgprint(_("Please select the document type first"), raise_exception=True)

    columns = [
        {
            "label": _(filters["duration"][:-2]),
            "fieldname": "duration",
            "fieldtype": "Data",
        },
        {
            "label": _(filters["doc_type"]),
            "options": filters["doc_type"],
            "fieldname": frappe.scrub(filters["doc_type"]),
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Customer"),
            "options": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Territory"),
            "options": "Territory",
            "fieldname": "territory",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Warehouse"),
            "options": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Item Code"),
            "options": "Item",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Item Group"),
            "options": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Brand"),
            "options": "Brand",
            "fieldname": "brand",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("SO Total Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Amount"),
            "options": "currency",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Sales Person"),
            "options": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Contribution %"),
            "fieldname": "contribution",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Contribution Qty"),
            "fieldname": "contribution_qty",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Contribution Amount"),
            "options": "currency",
            "fieldname": "contribution_amt",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Currency"),
            "options": "Currency",
            "fieldname": "currency",
            "fieldtype": "Link",
            "hidden": 1,
        },
    ]

    return columns


def get_duration_clause(filters):
    duration_clause = None
    if filters["duration"] == "Monthly":
        duration_clause = "MONTH(dt.{}) as duration"

    elif filters["duration"] == "Quarterly":
        duration_clause = "QUARTER(dt.{}) as duration"

    elif filters["duration"] == "Yearly":
        duration_clause = "YEAR(dt.{}) as duration"

    elif filters["duration"] == "Weekly":
        duration_clause = "WEEK(dt.{}) as duration"

    if duration_clause:
        if filters["doc_type"] in ("Sales Invoice", "Delivery Note"):
            duration_clause = duration_clause.format("posting_date")

        else:
            duration_clause = duration_clause.format("transaction_date")

    return duration_clause


def get_entries(filters):
    date_field = (
        filters["doc_type"] == "Sales Order" and "transaction_date" or "posting_date"
    )
    if filters["doc_type"] == "Sales Order":
        qty_field = "delivered_qty"
    else:
        qty_field = "qty"

    conditions, values = get_conditions(filters, date_field)
    duration_clause = get_duration_clause(filters)

    entries = frappe.db.sql(
        """
        SELECT
            dt.name, dt.customer, dt.territory, dt.{} as posting_date, dt_item.item_code,
            st.sales_person, st.allocated_percentage, dt_item.warehouse, 
        CASE
            WHEN dt.status = "Closed" THEN dt_item.{} * dt_item.conversion_factor
            ELSE dt_item.stock_qty
        END as stock_qty,
        CASE
            WHEN dt.status = "Closed" THEN (dt_item.base_net_rate * dt_item.{} * dt_item.conversion_factor)
            ELSE dt_item.base_net_amount
        END as base_net_amount,
        CASE
            WHEN dt.status = "Closed" THEN ((dt_item.base_net_rate * dt_item.{} * dt_item.conversion_factor) * st.allocated_percentage/100)
            ELSE dt_item.base_net_amount * st.allocated_percentage/100
        END as contriQUARTERution_amt, {}
        FROM
            `tab{}` dt, `tab{} Item` dt_item, `tabSales Team` st
        WHERE
            st.parent = dt.name and dt.name = dt_item.parent and st.parenttype = {}
            and dt.docstatus = 1 {} 
        ORDER BY st.sales_person, dt.name desc
        """.format(
            date_field,
            qty_field,
            qty_field,
            qty_field,
            duration_clause,
            filters["doc_type"],
            filters["doc_type"],
            "%s",
            conditions,
        ),
        tuple([filters["doc_type"], *values]),
        as_dict=1,
    )

    return entries


def get_conditions(filters, date_field):
    conditions = [""]
    values = []

    for field in ["company", "customer", "territory"]:
        if filters.get(field):
            conditions.append(f"dt.{field}=%s")
            values.append(filters[field])

    if filters.get("sales_person"):
        lft, rgt = frappe.get_value(
            "Sales Person", filters.get("sales_person"), ["lft", "rgt"]
        )
        conditions.append(
            f"exists(select name from `tabSales Person` where lft >= {lft} and rgt <= {rgt} and name=st.sales_person)"
        )

    if filters.get("from_date"):
        conditions.append(f"dt.{date_field}>=%s")
        values.append(filters["from_date"])

    if filters.get("to_date"):
        conditions.append(f"dt.{date_field}<=%s")
        values.append(filters["to_date"])

    items = get_items(filters)
    if items:
        conditions.append("dt_item.item_code in (%s)" % ", ".join(["%s"] * len(items)))
        values += items
    else:
        # return empty result, if no items are fetched after filtering on 'item group' and 'brand'
        conditions.append("dt_item.item_code = Null")

    return " and ".join(conditions), values


def get_items(filters):
    item = qb.DocType("Item")

    item_query_conditions = []
    if filters.get("item_group"):
        # Handle 'Parent' nodes as well.
        item_group = qb.DocType("Item Group")
        lft, rgt = frappe.db.get_all(
            "Item Group",
            filters={"name": filters.get("item_group")},
            fields=["lft", "rgt"],
            as_list=True,
        )[0]
        item_group_query = (
            qb.from_(item_group)
            .select(item_group.name)
            .where((item_group.lft >= lft) & (item_group.rgt <= rgt))
        )
        item_query_conditions.append(item.item_group.isin(item_group_query))
    if filters.get("brand"):
        item_query_conditions.append(item.brand == filters.get("brand"))

    items = (
        qb.from_(item)
        .select(item.name)
        .where(Criterion.all(item_query_conditions))
        .run()
    )
    return items


def get_item_details():
    item_details = {}
    for d in frappe.db.sql(
        """SELECT `name`, `item_group`, `brand` FROM `tabItem`""", as_dict=1
    ):
        item_details.setdefault(d.name, d)

    return item_details
