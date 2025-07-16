import json

import frappe
import frappe.defaults
from frappe.model.document import Document

from ..doctype.doctype_names_mapping import (
    COUNTRIES_DOCTYPE_NAME,
    ITEM_CLASSIFICATIONS_DOCTYPE_NAME,
    OPERATION_TYPE_DOCTYPE_NAME,
    PACKAGING_UNIT_DOCTYPE_NAME,
    PAYMENT_TYPE_DOCTYPE_NAME,
    SETTINGS_DOCTYPE_NAME,
    TAXATION_TYPE_DOCTYPE_NAME,
    UNIT_OF_QUANTITY_DOCTYPE_NAME,
    UOM_CATEGORY_DOCTYPE_NAME,
    WORKSTATION_DOCTYPE_NAME,
)
from ..utils import get_link_value


def send_pos_invoices_information() -> None:
    from ..overrides.server.sales_invoice import on_submit

    all_pending_pos_invoices: list[Document] = frappe.get_all(
        "POS Invoice", {"docstatus": 1, "custom_successfully_submitted": 0}, ["name"]
    )

    if all_pending_pos_invoices:
        for pos_invoice in all_pending_pos_invoices:
            doc = frappe.get_doc(
                "POS Invoice", pos_invoice.name, for_update=False
            )  # Refetch to get the document representation of the record

            try:
                on_submit(
                    doc, method=None
                )  # Delegate to the on_submit method for sales invoices

            except TypeError:
                continue


def update_documents(
    data: dict | list,
    doctype_name: str,
    field_mapping: dict,
    filter_field: str = "code",
) -> None:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {data}")

    doc_list = data if isinstance(data, list) else data.get("results", [data])

    for record in doc_list:
        if isinstance(record, str):
            continue

        filter_key = field_mapping.get(filter_field)
        filter_value = record.get(filter_key)
        doc_name = frappe.db.get_value(
            doctype_name, {filter_field: filter_value}, "name"
        )
        if doc_name:
            doc = frappe.get_doc(doctype_name, doc_name)
        else:
            doc = frappe.new_doc(doctype_name)

        for field, value in field_mapping.items():
            if callable(value):
                setattr(doc, field, value(record))
            elif isinstance(value, dict):
                linked_doctype = value.get("doctype")
                link_field = value.get("link_field")
                link_filter_field = value.get("filter_field", "custom_slade_id")
                link_extract_field = value.get("extract_field", "name")
                link_filter_value = record.get(link_field)
                if linked_doctype and link_filter_value:
                    linked_value = frappe.db.get_value(
                        linked_doctype,
                        {link_filter_field: link_filter_value},
                        link_extract_field,
                    )
                    setattr(doc, field, linked_value or "")
            else:
                setattr(doc, field, record.get(value, ""))

        try:
            doc.save(ignore_permissions=True)
        except Exception:
            continue

    frappe.db.commit()


def update_unit_of_quantity(response: dict, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "code": "code",
        "sort_order": "sort_order",
        "code_name": "name",
        "code_description": "description",
    }
    update_documents(response, UNIT_OF_QUANTITY_DOCTYPE_NAME, field_mapping)


def update_packaging_units(response: dict, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "code": "code",
        "code_name": "name",
        "sort_order": "sort_order",
        "code_description": "description",
    }
    update_documents(response, PACKAGING_UNIT_DOCTYPE_NAME, field_mapping)


def update_payment_methods(response: dict, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "account_details": "account_details",
        "mobile_money_type": "mobile_money_type",
        "mobile_money_business_number": "mobile_money_business_number",
        "bank_name": "bank_name",
        "bank_branch": "bank_branch",
        "bank_account_number": "bank_account_number",
        "active": lambda x: 1 if x.get("active") else 0,
        "code_name": "name",
        "description": "description",
        "account": "account",
    }
    update_documents(
        response, PAYMENT_TYPE_DOCTYPE_NAME, field_mapping, filter_field="slade_id"
    )


def update_currencies(response: dict, **kwargs) -> None:
    field_mapping = {
        "custom_slade_id": "id",
        "currency_name": "iso_code",
        "enabled": lambda x: 1 if x.get("active") else 0,
        "custom_conversion_rate": "conversion_rate",
    }
    update_documents(response, "Currency", field_mapping, filter_field="currency_name")


def update_item_classification_codes(response: dict | list, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "itemclscd": "classification_code",
        "itemclslvl": "classification_level",
        "itemclsnm": "classification_name",
        "taxtycd": "tax_type_code",
        "useyn": lambda x: 1 if x.get("is_used") else 0,
        "mjrtgyn": lambda x: 1 if x.get("is_frequently_used") else 0,
    }
    update_documents(
        response,
        ITEM_CLASSIFICATIONS_DOCTYPE_NAME,
        field_mapping,
        filter_field="itemclscd",
    )


def update_taxation_type(response: dict, **kwargs) -> None:
    doc: Document | None = None
    tax_list = response.get("results", [])

    for taxation_type in tax_list:
        code = (
            taxation_type["tax_code"]
            if taxation_type["tax_code"]
            else taxation_type["name"]
        )
        try:
            doc_name = frappe.db.get_value(
                TAXATION_TYPE_DOCTYPE_NAME, {"cd": code}, "name"
            )
            doc = frappe.get_doc(TAXATION_TYPE_DOCTYPE_NAME, doc_name)

        except Exception:
            doc = frappe.new_doc(TAXATION_TYPE_DOCTYPE_NAME)

        finally:
            doc.cd = code
            doc.cdnm = taxation_type["name"]
            doc.slade_id = taxation_type["id"]
            doc.cddesc = taxation_type["description"]
            doc.useyn = 1 if taxation_type["active"] else 0
            doc.srtord = taxation_type["percentage"]

            doc.save(ignore_permissions=True)

    frappe.db.commit()


def update_countries(response: list, **kwargs) -> None:
    doc: Document | None = None
    for code, details in response.items():
        country_name = details.get("name", "").strip().lower()
        existing_doc = frappe.get_value(
            COUNTRIES_DOCTYPE_NAME, {"name": ["like", country_name]}
        )

        if existing_doc:
            doc = frappe.get_doc(COUNTRIES_DOCTYPE_NAME, existing_doc)
        else:
            doc = frappe.new_doc(COUNTRIES_DOCTYPE_NAME)

        doc.code = code
        doc.code_name = details.get("name")
        doc.currency_code = details.get("currency_code")
        doc.sort_order = details.get("sort_order", 0)
        doc.code_description = details.get("description", "")

        doc.save(ignore_permissions=True)

    frappe.db.commit()


def update_organisations(response: dict, **kwargs) -> None:
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    record = (
        response if isinstance(response, list) else response.get("results", response)
    )[0]

    company_name = frappe.defaults.get_user_default("Company") or frappe.get_value(
        "Company", {}, "name"
    )

    doc = frappe.get_doc("Company", company_name)

    if record.get("default_currency"):
        doc.default_currency = (
            get_link_value(
                "Currency", "custom_slade_id", record.get("default_currency")
            )
            or "KES"
        )
    if record.get("web_address"):
        doc.website = record.get("web_address", "")
    if record.get("phone_number"):
        doc.phone_no = record.get("phone_number", "")
    if record.get("description"):
        doc.company_description = record.get("description", "")
    if record.get("id"):
        doc.custom_slade_id = record.get("id", "")
    if record.get("email_address"):
        doc.email = record.get("email_address", "")
    if record.get("tax_payer_pin"):
        doc.tax_id = record.get("tax_payer_pin", "")
    doc.is_etims_verified = 1 if record.get("is_etims_verified") else 0

    doc.save(ignore_permissions=True)

    frappe.db.commit()


def update_branches(response: dict, **kwargs) -> None:
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    doc_list = (
        response if isinstance(response, list) else response.get("results", response)
    )
    if len(doc_list) == 1:
        branches = frappe.get_all("Branch")
        if branches:
            for branch in branches:
                frappe.set_value(
                    "Branch",
                    branch.get("name"),
                    {"slade_id": doc_list[0].get("id"), "is_etims_branch": 1},
                )
        else:
            branch_name = "eTims Branch"
            existing_branch = frappe.db.get_value(
                "Branch", {"branch": branch_name}, "name"
            )

            if existing_branch:
                doc = frappe.get_doc("Branch", existing_branch)
            else:
                doc = frappe.new_doc("Branch")
                doc.branch = branch_name

            doc.slade_id = doc_list[0].get("id")
            doc.is_etims_verified = 1 if doc_list[0].get("is_etims_verified") else 0
            doc.is_head_office = 1 if doc_list[0].get("is_headquater") else 0
            doc.custom_company = get_link_value(
                "Company", "custom_slade_id", doc_list[0].get("organisation")
            )
            doc.custom_etims_device_serial_no = doc_list[0].get(
                "etims_device_serial_no"
            )
            doc.custom_branch_code = doc_list[0].get("etims_branch_id")
            doc.custom_pin = doc_list[0].get("organisation_tax_pin")
            doc.is_etims_branch = 1
            doc.flags.ignore_permissions = True
            doc.save(ignore_permissions=True)
    else:
        field_mapping = {
            "slade_id": "id",
            "tax_id": "organisation_tax_pin",
            "branch": "name",
            "custom_etims_device_serial_no": "etims_device_serial_no",
            "custom_branch_code": "etims_branch_id",
            "custom_pin": "organisation_tax_pin",
            "custom_branch_name": "name",
            "custom_county_name": "county_name",
            "custom_tax_locality_name": "tax_locality_name",
            "custom_sub_county_name": "sub_county_name",
            "custom_manager_name": "manager_name",
            "custom_location_description": "location_description",
            "custom_is_head_office": lambda x: 1 if x.get("is_headquater") else 0,
            "custom_company": {
                "doctype": "Company",
                "link_field": "organisation",
                "filter_field": "custom_slade_id",
                "extract_field": "name",
            },
            "custom_is_etims_branch": lambda x: 1 if x.get("branch_status") else 0,
            "custom_is_etims_verified": lambda x: (
                1 if x.get("is_etims_verified") else 0
            ),
        }
        update_documents(response, "Branch", field_mapping, filter_field="branch")


def update_departments(response: dict, **kwargs) -> None:
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    record = (
        response if isinstance(response, list) else response.get("results", [response])
    )[0]

    department_name = "eTims Department"
    existing_department = frappe.db.get_value(
        "Department", {"department_name": department_name}, "name"
    )
    if existing_department:
        doc = frappe.get_doc("Department", existing_department)
    else:
        matching_department = frappe.db.get_value(
            "Department", {"department_name": department_name}, "name"
        )
        if matching_department:
            branch_name = record.get("parent_name", "")
            department_name = (
                f"{department_name} - {branch_name}" if branch_name else department_name
            )

        doc = frappe.new_doc("Department")
        doc.department_name = department_name

    if record.get("organisation"):
        doc.company = (
            get_link_value("Company", "custom_slade_id", record.get("organisation"))
            or frappe.defaults.get_user_default("Company")
            or frappe.get_value("Company", {}, "name")
        )
    if record.get("parent"):
        doc.custom_branch = get_link_value("Branch", "slade_id", record.get("parent"))
    if record.get("id"):
        doc.custom_slade_id = record.get("id")
    doc.is_etims_verified = 1 if record.get("is_etims_verified") else 0
    doc.custom_is_etims_department = 1

    doc.save(ignore_permissions=True)

    frappe.db.commit()


def update_workstations(response: dict, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "active": lambda x: 1 if x.get("active") else 0,
        "workstation": "name",
        "workstation_type_display": "workstation_type_display",
        "workstation_type": "workstation_type",
        "is_billing_point": lambda x: 1 if x.get("is_billing_point") else 0,
        "company": {
            "doctype": "Company",
            "link_field": "organisation",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
        "department": {
            "doctype": "Department",
            "link_field": "org_unit",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
    }
    update_documents(
        response, WORKSTATION_DOCTYPE_NAME, field_mapping, filter_field="slade_id"
    )


def uom_category_search_on_success(response: dict, **kwargs) -> None:
    field_mapping = {
        "slade_id": "id",
        "measure_type": "measure_type",
        "category_name": "name",
        "active": lambda x: 1 if x.get("active") else 0,
    }
    update_documents(
        response, UOM_CATEGORY_DOCTYPE_NAME, field_mapping, filter_field="category_name"
    )


def uom_search_on_success(response: dict, **kwargs) -> None:
    field_mapping = {
        "custom_slade_id": "id",
        "custom_uom_type": "uom_type",
        "custom_factor": "factor",
        "custom_category": {
            "doctype": UOM_CATEGORY_DOCTYPE_NAME,
            "link_field": "category",
            "filter_field": "slade_id",
            "extract_field": "name",
        },
        "uom_name": "name",
        "active": lambda x: 1 if x.get("active") else 0,
    }
    update_documents(response, "UOM", field_mapping, filter_field="uom_name")


def warehouse_search_on_success(response: dict, **kwargs) -> None:
    from ..apis.process_request import process_request
    from ..utils import get_settings

    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    doc_list = (
        response if isinstance(response, list) else response.get("results", [response])
    )

    settings = get_settings()

    bhfid_slade_id = frappe.db.get_value("Branch", settings.bhfid, "slade_id")
    selected_record = (
        next((r for r in doc_list if r.get("branch") == bhfid_slade_id), None)
        or next((r for r in doc_list if "Stock" in r.get("name", "")), None)
        or (doc_list[0] if doc_list else None)
    )
    if selected_record:
        existing_warehouse = frappe.db.get_value(
            "Warehouse", {"company": settings.company, "is_group": 1}, "name"
        )
        if existing_warehouse:
            frappe.db.set_value(
                "Warehouse",
                existing_warehouse,
                {
                    "custom_slade_id": selected_record.get("id", ""),
                },
            )
            frappe.db.set_value(
                SETTINGS_DOCTYPE_NAME,
                settings.name,
                {
                    "warehouse": existing_warehouse,
                },
            )
            frappe.enqueue(
                search_customer_supplier_locations, document_name=settings.name
            )

        bhfid_slade_id = frappe.db.get_value("Branch", settings.bhfid, "slade_id")
        if bhfid_slade_id:
            request_data = {
                "branch": bhfid_slade_id,
                "id": selected_record.get("id"),
            }
            frappe.enqueue(
                process_request,
                queue="default",
                is_async=True,
                doctype="Branch",
                request_data=request_data,
                route_key="LocationSearchReq",
                request_method="PATCH",
            )


def search_customer_supplier_locations(document_name: str) -> None:
    from ..apis.process_request import process_request

    process_request(
        {"location_type": "customer", "document_name": document_name},
        "LocationsSearchReq",
        search_customer_supplier_locations_on_success,
        doctype=SETTINGS_DOCTYPE_NAME,
    )

    process_request(
        {"location_type": "supplier", "document_name": document_name},
        "LocationsSearchReq",
        search_customer_supplier_locations_on_success,
        doctype=SETTINGS_DOCTYPE_NAME,
    )


def search_customer_supplier_locations_on_success(
    response: dict, document_name: str, **kwargs
) -> None:
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    doc_list = (
        response if isinstance(response, list) else response.get("results", [response])
    )
    settings = frappe.get_doc(SETTINGS_DOCTYPE_NAME, document_name)
    bhfid_slade_id = frappe.db.get_value("Branch", settings.bhfid, "slade_id")
    selected_record = next(
        (r for r in doc_list if r.get("branch") == bhfid_slade_id), None
    ) or (doc_list[0] if doc_list else None)

    if selected_record:
        location_type = selected_record.get("location_type", "").lower()
        if location_type == "supplier":
            frappe.db.set_value(
                "Warehouse",
                settings.warehouse,
                "custom_slade_supplier_warehouse",
                selected_record.get("id"),
            )
        elif location_type == "customer":
            frappe.db.set_value(
                "Warehouse",
                settings.warehouse,
                "custom_slade_customer_warehouse",
                selected_record.get("id"),
            )


def pricelist_search_on_success(response: dict, **kwargs) -> None:
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string: {response}")

    doc_list = (
        response if isinstance(response, list) else response.get("results", [response])
    )

    for record in doc_list:
        if isinstance(record, str):
            continue

        existing_pricelist = frappe.db.get_value(
            "Price List", {"price_list_name": record.get("name")}, "name"
        )
        if existing_pricelist:
            doc = frappe.get_doc("Price List", existing_pricelist)
        else:
            doc = frappe.new_doc("Price List")

        doc.custom_slade_id = record.get("id")
        doc.custom_pricelist_status = record.get("pricelist_status")

        doc.custom_company = get_link_value(
            "Company", "custom_slade_id", record.get("organisation")
        )

        doc.custom_warehouse = get_link_value(
            "Warehouse", "custom_slade_id", record.get("location")
        )

        doc.price_list_name = record.get("name")

        if record.get("effective_from"):
            doc.custom_effective_from = frappe.utils.getdate(
                record.get("effective_from")
            )

        if record.get("effective_to"):
            doc.custom_effective_to = frappe.utils.getdate(record.get("effective_to"))

        doc.enabled = 1 if record.get("active") else 0
        doc.buying = 1 if record.get("pricelist_type") == "sales" else 0
        doc.selling = 1 if record.get("pricelist_type") == "purchases" else 0

        doc.save(ignore_permissions=True)

    frappe.db.commit()


def itemprice_search_on_success(response: dict, **kwargs) -> None:
    field_mapping = {
        "custom_slade_id": "id",
        "price_list_rate": "price_inclusive_tax",
        "custom_factor": "factor",
        "item_code": {
            "doctype": "Item",
            "link_field": "product",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
        "custom_company": {
            "doctype": "Company",
            "link_field": "organisation",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
        "currency": {
            "doctype": "Currency",
            "link_field": "currency",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
        "price_list": {
            "doctype": "Price List",
            "link_field": "pricelist",
            "filter_field": "custom_slade_id",
            "extract_field": "name",
        },
        "enabled": lambda x: 1 if x.get("active") else 0,
    }
    update_documents(
        response, "Item Price", field_mapping, filter_field="custom_slade_id"
    )


def operation_types_search_on_success(
    response: dict, document_name: str, **kwargs
) -> None:
    frappe.db.set_value(
        OPERATION_TYPE_DOCTYPE_NAME,
        document_name,
        {
            "slade_id": response.get("id"),
            "operation_name": response.get("operation_name"),
            "source_location": response.get("source_location"),
            "destination_location": response.get("destination_location"),
            "operation_type": response.get("operation_type"),
        },
    )
