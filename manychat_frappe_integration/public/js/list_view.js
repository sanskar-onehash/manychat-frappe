function ButtonFunction(listview) {
    console.log("ButtonFunction");
    frappe.msgprint("ButtonFunction");
}

frappe.listview_settings['Lead'] = {
   refresh: function(listview) {
       listview.page.add_inner_button("Button Name", function() {
            frappe.msgprint("hello")
           ButtonFunction(listview);
       });;
   },
};