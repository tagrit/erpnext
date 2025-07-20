from typing import Any, Dict, List, Optional, Tuple

from pypika.functions import Sum
from pypika.terms import Case

import frappe
from frappe.query_builder import DocType


def execute(
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], None, Dict[str, Any]]:
    return DocumentSubmissionStatusAnalytics(filters).run()


class DocumentSubmissionStatusAnalytics:
    def __init__(self, filters: Optional[Dict[str, Any]] = None) -> None:
        self.filters = frappe._dict(filters or {})
        self.columns = [
            {
                "fieldname": "doctype",
                "label": "Document Type",
                "fieldtype": "Data",
                "width": 300,
            },
            {"fieldname": "sent", "label": "Sent", "fieldtype": "Int", "width": 150},
            {
                "fieldname": "not_sent",
                "label": "Not Sent",
                "fieldtype": "Int",
                "width": 150,
            },
            {
                "fieldname": "failed",
                "label": "Failed",
                "fieldtype": "Int",
                "width": 150,
            },
            {
                "fieldname": "successful",
                "label": "Successful",
                "fieldtype": "Int",
                "width": 150,
            },
            {"fieldname": "total", "label": "Total", "fieldtype": "Int", "width": 150},
        ]
        self.data: List[Dict[str, Any]] = []
        self.chart: Dict[str, Any] = {}
        self.tracked_docs = {
            "Item": DocType("Item"),
            "Invoice": DocType("Sales Invoice"),
            "Credit Note": DocType("Sales Invoice"),
            "Purchase Invoice": DocType("Purchase Invoice"),
            "Stock Ledger Entry": DocType("Stock Ledger Entry"),
        }

    def run(
        self,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], None, Dict[str, Any]]:
        self.fetch_data()
        self.get_chart_data()
        return self.columns, self.data, None, self.chart

    def fetch_data(self) -> None:
        from_date = self.filters.get("from_date")
        to_date = self.filters.get("to_date")

        for doc_name, doctype in self.tracked_docs.items():
            meta = frappe.get_meta(
                "Sales Invoice" if doc_name in ["Invoice", "Credit Note"] else doc_name
            )
            has_fields = {
                "custom_slade_id": meta.has_field("custom_slade_id"),
                "custom_successfully_submitted": meta.has_field(
                    "custom_successfully_submitted"
                ),
                "custom_submitted_successfully": meta.has_field(
                    "custom_submitted_successfully"
                ),
                "custom_sent_to_slade": meta.has_field("custom_sent_to_slade"),
            }

            sent_condition = (
                doctype.custom_slade_id.isnotnull()
                if has_fields["custom_slade_id"]
                else None
            )
            not_sent_condition = (
                doctype.custom_slade_id.isnull()
                if has_fields["custom_slade_id"]
                else None
            )

            success_conditions = []
            if has_fields["custom_sent_to_slade"]:
                success_conditions.append(doctype.custom_sent_to_slade)
            if has_fields["custom_successfully_submitted"]:
                success_conditions.append(doctype.custom_successfully_submitted)
            if has_fields["custom_submitted_successfully"]:
                success_conditions.append(doctype.custom_submitted_successfully)

            success_condition = None
            if success_conditions:
                success_condition = success_conditions[0]
                for cond in success_conditions[1:]:
                    success_condition |= cond

            failed_condition = (
                sent_condition & ~success_condition
                if sent_condition and success_condition
                else None
            )

            query = frappe.qb.from_(doctype).select(
                (
                    Sum(Case().when(success_condition, 1).else_(0)).as_("successful")
                    if success_condition
                    else Sum(0).as_("successful")
                ),
                (
                    Sum(Case().when(sent_condition, 1).else_(0)).as_("sent")
                    if sent_condition
                    else Sum(0).as_("sent")
                ),
                (
                    Sum(Case().when(not_sent_condition, 1).else_(0)).as_("not_sent")
                    if not_sent_condition
                    else Sum(0).as_("not_sent")
                ),
                (
                    Sum(Case().when(failed_condition, 1).else_(0)).as_("failed")
                    if failed_condition
                    else Sum(0).as_("failed")
                ),
                Sum(1).as_("total"),
            )

            if from_date:
                query = query.where(doctype.creation >= from_date)
            if to_date:
                query = query.where(doctype.creation <= to_date)

            if doc_name == "Invoice":
                query = query.where(doctype.is_return == 0)
            elif doc_name == "Credit Note":
                query = query.where(doctype.is_return == 1)

            try:
                row = query.run(as_dict=True)[0]
                row["doctype"] = doc_name
                self.data.append(row)
            except Exception as e:
                frappe.log_error(f"Error fetching data for {doc_name}: {str(e)}")

    def get_chart_data(self) -> None:
        labels = [row["doctype"] for row in self.data]
        datasets = [
            {"name": "Sent", "values": [row.get("sent", 0) for row in self.data]},
            {
                "name": "Not Sent",
                "values": [row.get("not_sent", 0) for row in self.data],
            },
            {"name": "Failed", "values": [row.get("failed", 0) for row in self.data]},
            {
                "name": "Successful",
                "values": [row.get("successful", 0) for row in self.data],
            },
        ]

        self.chart = {
            "data": {"labels": labels, "datasets": datasets},
            "type": "bar",
            "axis_options": {"xIsSeries": True},
        }
