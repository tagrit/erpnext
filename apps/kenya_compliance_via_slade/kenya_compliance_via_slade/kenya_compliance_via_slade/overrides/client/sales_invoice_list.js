const doctypeName = "Sales Invoice";
const settingsDoctypeName = "Navari KRA eTims Settings";

frappe.listview_settings[doctypeName].onload = async function (listview) {
  const { message: activeSetting } = await frappe.call({
    method:
      "kenya_compliance_via_slade.kenya_compliance_via_slade.utils.get_active_setting",
    args: {
      doctype: settingsDoctypeName,
    },
  });

  if (activeSetting?.message?.name) {
    listview.page.add_action_item(__("Bulk Submit to eTims"), function () {
      bulkSubmitInvoices(listview, doctypeName);
    });
  }
};

function bulkSubmitInvoices(listview, doctype) {
  const itemsToSubmit = listview.get_checked_items().map((item) => item.name);

  frappe.call({
    method:
      "kenya_compliance_via_slade.kenya_compliance_via_slade.apis.apis.bulk_submit_sales_invoices",
    args: {
      docs_list: itemsToSubmit,
    },
    callback: (response) => {
      frappe.msgprint("Bulk submission queued.");
    },
    error: (r) => {
      // Error Handling is Defered to the Server
    },
  });
}
