import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "etr_data",
                "label": "ETR Data",
                "fieldtype": "Tab Break",
                "insert_after": "timesheets",
                "allow_on_submit": True,
                "translatable": 1
            },
            {
                "fieldname": "etr_serial_number",
                "label": "ETR Serial Number",
                "fieldtype": "Data",
                "collapsible": 0,
                "insert_after": "etr_data",
                "allow_on_submit": True,
                "translatable": 1,
                "no_copy": 1
            },
            {
                "fieldname": "cu_invoice_date",
                "label": "CU Invoice Date",
                "fieldtype": "Date",
                "collapsible": 0,
                "insert_after": "etr_serial_number",
                "allow_on_submit": True,
                "translatable": 1,
                "no_copy": 1
            },
            {
                "fieldname": "etr_column_break",
                "fieldtype": "Column Break",
                "insert_after": "cu_invoice_date",
                "translatable": 1
            },
            {
                "fieldname": "etr_invoice_number",
                "label": "ETR Invoice Number",
                "fieldtype": "Data",
                "collapsible": 0,
                "insert_after": "etr_column_break",
                "allow_on_submit": True,
                "translatable": 1,
                "no_copy": 1
            },
            {
                "fieldname": "cu_link",
                "label": "CU Link",
                "fieldtype": "Data",
                "collapsible": 0,
                "insert_after": "etr_invoice_number",
                "allow_on_submit": True,
                "translatable": 1,
                "no_copy": 1
            },
            {
                "fieldname": "is_filed",
                "label": "Is Filed",
                "fieldtype": "Check",
                "collapsible": 0,
                "insert_after": "cu_link",
                "allow_on_submit": True,
                "translatable": 1,
                "no_copy": 1,
                "read_only": 1
            }
        ]
    }

    create_custom_fields(custom_fields)