frappe.provide('frappe.ui.form');
frappe.provide('frappe.model.docinfo');

$(document).ready(function () {
    frappe.ui.form.Controller = Class.extend({
        init: function (opts) {
            $.extend(this, opts);
            let ignored_doctype_list = ["DocType", "Customize Form"]
            frappe.ui.form.on(this.frm.doctype, {
                refresh(frm) {
                    if (!ignored_doctype_list.includes(frm.doc.doctype)) {
                        frm.page.add_menu_item(__('Send via WhatsApp 1'), function () { send_sms(frm); });
                    }
                }
            });
        }
    });
});

function send_sms(frm) {
    if (frm.is_dirty()) {
        frappe.throw(__('You have unsaved changes. Save before send.'))
    }
    else {
        create_recipients_dialog(frm);
    }
}

function create_recipients_dialog(frm) {
    // Get all possible numbers from the current form
    let numbers = [];

    // Add WhatsApp number if exists
    if (frm.doc.whatsapp_no) {
        if (Array.isArray(frm.doc.whatsapp_no)) {
            numbers = numbers.concat(frm.doc.whatsapp_no);
        } else {
            numbers.push(frm.doc.whatsapp_no);
        }
    }

    // Add phone if exists
    if (frm.doc.phone) {
        if (Array.isArray(frm.doc.phone)) {
            numbers = numbers.concat(frm.doc.phone);
        } else {
            numbers.push(frm.doc.phone);
        }
    }

    if (frm.doc.mobile_no) {
        if (Array.isArray(frm.doc.mobile_no)) {
            numbers = numbers.concat(frm.doc.mobile_no);
        } else {
            numbers.push(frm.doc.mobile_no);
        }
    }

    // Remove duplicates and filter out empty values
    numbers = [...new Set(numbers)].filter(number => number);

    let d = new frappe.ui.Dialog({
        title: frm.doc.doctype + " : " + frm.doc.name,
        fields: [
            {
                label: __("To"),
                fieldtype: "MultiSelect",
                reqd: 1,
                fieldname: "recipients",
                options: numbers,
                description: __("Select one or more numbers")
            },
            {
                label: __("Select Template"),
                fieldtype: "Link",
                fieldname: "manychat_templates",
                options: "Manychat Templates",
                get_query: function () {
                    return {
                        filters: {
                            'enabled': 1
                        }
                    }
                }
            }
        ],
        primary_action_label: __("Send"),
        primary_action(values) {
            dialog_primary_action(frm, values)
            d.hide();
        },
        secondary_action_label: __("Discard"),
        secondary_action() {
            d.hide();
        },
        size: 'large',
        minimizable: true
    });
    d.show();
}

function dialog_primary_action(frm, values) {
    if (!values.manychat_templates) {
        frappe.throw(__('Please select a template'));
        return;
    }

    if (!values.recipients || values.recipients.length === 0) {
        frappe.throw(__('Please select at least one recipient'));
        return;
    }

    frappe.call({
        method: "manychat_frappe_integration.manychat_frappe_integration.api.manychat_api.send_template",
        args: {
            "doctype": frm.doc.doctype,
            "docname": frm.doc.name,
            "args": {
                "doctype": frm.doc.doctype,
                "docname": frm.doc.name,
                "manychat_templates": values.manychat_templates
            }
        },
        freeze: true,
        freeze_message: __('Sending Template...'),
        callback: function (r) {
            if (r.message && r.message.status === "success") {
                frappe.show_alert({
                    message: __(r.message.message || "Template sent successfully"),
                    indicator: 'green'
                }, 5);
            } else {
                frappe.show_alert({
                    message: __(r.message.message || "Failed to send Template"),
                    indicator: 'red'
                }, 7);

                console.error("Template Sending Error:", r.message);
            }
        }
    });
}