import frappe
from erpnext.selling.doctype.sales_order.test_sales_order import make_sales_order
from frappe.tests.utils import FrappeTestCase

from .sales_analytics_enhanced import execute


class TestSalesAnalyticsEnhanced(FrappeTestCase):
    def test_sales_analytics_enhanced(self) -> None:
        frappe.db.sql("delete from `tabSales Order` where company='_Test Company 2'")

        create_sales_orders()

        self.compare_result_for_user_by_quantity()
        self.compare_result_for_user_by_value()

    def compare_result_for_user_by_quantity(self):
        filters = {
            "tree_type": "User",
            "doc_type": "Sales Order",
            "company": "_Test Company 2",
            "from_date": "2017-01-01",
            "to_date": "2018-12-31",
            "value_quantity": "Quantity",
            "range": "Monthly",
        }

        report = execute(filters)

        expected_data = [
            {
                "entity": "Administrator",
                "entity_name": "Administrator",
                "jan_2017": 0.0,
                "feb_2017": 0.0,
                "mar_2017": 0.0,
                "apr_2017": 0.0,
                "may_2017": 0.0,
                "jun_2017": 20.0,
                "jul_2017": 10.0,
                "aug_2017": 0.0,
                "sep_2017": 15.0,
                "oct_2017": 10.0,
                "nov_2017": 0.0,
                "dec_2017": 0.0,
                "jan_2018": 0.0,
                "feb_2018": 20.0,
                "mar_2018": 0.0,
                "apr_2018": 0.0,
                "may_2018": 0.0,
                "jun_2018": 0.0,
                "jul_2018": 0.0,
                "aug_2018": 0.0,
                "sep_2018": 0.0,
                "oct_2018": 0.0,
                "nov_2018": 0.0,
                "dec_2018": 0.0,
                "total": 75.0,
            }
        ]

        result = sorted(report[1], key=lambda k: k["entity"])

        self.assertEqual(expected_data, result)

    def compare_result_for_user_by_value(self):
        filters = {
            "tree_type": "User",
            "doc_type": "Sales Order",
            "company": "_Test Company 2",
            "from_date": "2017-01-01",
            "to_date": "2018-12-31",
            "value_quantity": "Value",
            "range": "Monthly",
        }

        report = execute(filters)

        expected_data = [
            {
                "entity": "Administrator",
                "entity_name": "Administrator",
                "jan_2017": 0.0,
                "feb_2017": 0.0,
                "mar_2017": 0.0,
                "apr_2017": 0.0,
                "may_2017": 0.0,
                "jun_2017": 2000.0,
                "jul_2017": 1000.0,
                "aug_2017": 0.0,
                "sep_2017": 1500.0,
                "oct_2017": 1000.0,
                "nov_2017": 0.0,
                "dec_2017": 0.0,
                "jan_2018": 0.0,
                "feb_2018": 2000.0,
                "mar_2018": 0.0,
                "apr_2018": 0.0,
                "may_2018": 0.0,
                "jun_2018": 0.0,
                "jul_2018": 0.0,
                "aug_2018": 0.0,
                "sep_2018": 0.0,
                "oct_2018": 0.0,
                "nov_2018": 0.0,
                "dec_2018": 0.0,
                "total": 7500.0,
            }
        ]

        result = sorted(report[1], key=lambda k: k["entity"])

        self.assertEqual(expected_data, result)


def create_sales_orders():
    frappe.set_user("Administrator")

    make_sales_order(
        company="_Test Company 2",
        qty=10,
        customer="_Test Customer 1",
        transaction_date="2018-02-10",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )

    make_sales_order(
        company="_Test Company 2",
        qty=10,
        customer="_Test Customer 1",
        transaction_date="2018-02-15",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )

    make_sales_order(
        company="_Test Company 2",
        qty=10,
        customer="_Test Customer 2",
        transaction_date="2017-10-10",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )

    make_sales_order(
        company="_Test Company 2",
        qty=15,
        customer="_Test Customer 2",
        transaction_date="2017-09-23",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )

    make_sales_order(
        company="_Test Company 2",
        qty=20,
        customer="_Test Customer 3",
        transaction_date="2017-06-15",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )

    make_sales_order(
        company="_Test Company 2",
        qty=10,
        customer="_Test Customer 3",
        transaction_date="2017-07-10",
        warehouse="Finished Goods - _TC2",
        currency="EUR",
        owner="Administrator",
    )
