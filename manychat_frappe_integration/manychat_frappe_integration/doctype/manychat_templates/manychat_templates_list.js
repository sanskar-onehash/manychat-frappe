frappe.listview_settings["Manychat Templates"] = {
    onload:function(listview){
        listview.page.add_inner_button("Fetch Templates", function() {
            console.log("i am heree")
            frappe.show_progress('Fetching Manychat Templates...', 70, 100, 'Please wait');
            frappe.call({
                method: "manychat_frappe_integration.manychat_frappe_integration.api.manychat_api.get_manychat_templates",
                callback: function (r) {
                    if(r.message[0] == true){
                        frappe.hide_progress("Fetching Manychat Templates...")
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __(r.message[1])
                        });
                        frappe.ui.toolbar.clear_cache()
                    }else if(r.message[0] == false){
                        frappe.hide_progress("Fetching Manychat Templates...")
                        frappe.msgprint({
                            title: __('Failure'),
                            indicator: 'red',
                            message: __(r.message[1])
                        });
                    }
                }
            })
        })
    }
};