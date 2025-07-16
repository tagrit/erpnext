const doctypeName = "Customer";
const settingsDoctypeName = "Navari KRA eTims Settings";

frappe.listview_settings[doctypeName] = {
  onload: async function (listview) {
    const companyName = frappe.boot.sysdefaults.company;
    const { message: activeSetting } = await frappe.call({
      method:
        "kenya_compliance_via_slade.kenya_compliance_via_slade.utils.get_active_setting",
      args: {
        doctype: settingsDoctypeName,
      },
    });

    if (activeSetting?.message?.name) {
      listview.page.add_inner_button(
        __("Get Customers"),
        function (listview) {
          frappe.call({
            method:
              "kenya_compliance_via_slade.kenya_compliance_via_slade.apis.apis.search_customers_request",
            args: {
              request_data: {
                company_name: companyName,
              },
            },
            callback: (response) => {
              console.log("Request queued. Please check in later");
            },
            error: (error) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );

      listview.page.add_inner_button(
        __("Submit all Customers to eTims"),
        function () {
          frappe.call({
            method:
              "kenya_compliance_via_slade.kenya_compliance_via_slade.apis.apis.submit_all_customers",

            callback: (response) => {},
            error: (r) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );
    }
  },
};
