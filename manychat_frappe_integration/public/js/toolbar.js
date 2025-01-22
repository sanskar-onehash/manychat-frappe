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
                        frm.add_custom_button(__('Send via WhatsApp'), function () { send_sms(frm); });
                    }
                }
            });
        }
    });
});

function send_sms(frm) {
    if (frm.is_dirty()) {
        frappe.throw(__('You have unsaved changes. Save before send.'))
    } else {
        console.log("doctype", frm.doc.doctype)
        if (frm.doc.doctype === 'Lead') {
            console.log("i am heree")
            check_manychat_contact(frm);
        } else {
            create_recipients_dialog(frm);
        }
    }
}

function check_manychat_contact(frm) {
    // Get the primary phone number from the contact
    let phone = frm.doc.phone || frm.doc.mobile_no;

    if (!phone) {
        frappe.throw(__('No phone number found for this contact'));
        return;
    }

    frappe.call({
        method: "manychat_frappe_integration.manychat_frappe_integration.api.manychat_api.check_contact_exists",
        args: {
            "docname": frm.doc.name,
        },
        freeze: true,
        freeze_message: __('Checking contact...'),
        callback: function (r) {
            if (!r.message) {
                frappe.throw(__('Failed to check contact status'));
                return;
            }
            if (r.message.status === "error") {
                frappe.throw(__(r.message.message));
                return;
            }
            if (r.message.exists === true) {
                // Contact exists in ManyChat, proceed with regular flow
                create_recipients_dialog(frm);
            } else {
                // Contact doesn't exist, show dialog to create contact
                show_create_contact_dialog(frm, phone);
            }
        }
    });
}


function show_create_contact_dialog(frm, phone) {
    // Clean the initial phone number
    const cleanInitialPhone = phone.replace(/[^0-9]/g, '');

    let d = new frappe.ui.Dialog({
        title: __('Contact not found in ManyChat. Kindly create a new contact'),
        fields: [
            {
                label: __('First Name'),
                fieldtype: 'Data',
                fieldname: 'first_name',
                reqd: 1,
                default: frm.doc.first_name
            },
            {
                label: __('Last Name'),
                fieldtype: 'Data',
                fieldname: 'last_name',
                default: frm.doc.last_name
            },
            {
                label: __("Country Code"),
                fieldtype: "Select",
                options: "\n+91\n+1\n+44\n+61\n+86\n+81\n+49\n+33\n+7\n+65",
                reqd: 1,
                fieldname: "country_code",
                description: __("Select your country code")
            },
            {
                label: __('Phone'),
                fieldtype: 'Data',
                fieldname: 'phone',
                reqd: 1,
                default: cleanInitialPhone,
                description: __("Enter phone number without country code")
            },
            {
                label: __('WhatsApp Number'),
                fieldtype: 'Data',
                fieldname: 'whatsapp_number',
                description: __("Optional, if different from phone number")
            },
            {
                label: __('Email'),
                fieldtype: 'Data',
                fieldname: 'email',
                default: frm.doc.email_id
            },
            {
                label: __('Gender'),
                fieldtype: 'Select',
                fieldname: 'gender',
                options: ['Male', 'Female', 'Others'],
                reqd: 1,
            },
            {
                label: __('Opt-in for SMS'),
                fieldtype: 'Check',
                fieldname: 'has_opt_in_sms',
                default: 1
            },
            {
                label: __('Opt-in for Email'),
                fieldtype: 'Check',
                fieldname: 'has_opt_in_email',
                default: 1
            },
            {
                label: __("Consent Phrase"),
                fieldtype: "Small Text",
                fieldname: "consent_phrase",
                placeholder: __("Enter consent phrase"),
                default: "I agree to receive communications"
            }
        ],
        primary_action_label: __('Create Contact'),
        primary_action(values) {
            // Validate phone number
            const cleanPhone = values.phone.replace(/[^0-9]/g, '');
            if (cleanPhone.length < 10) {
                frappe.msgprint(__('Please enter a valid phone number with at least 10 digits.'));
                return;
            }

            create_manychat_contact(frm, values);
            d.hide();
        },
        secondary_action_label: __('Cancel'),
        secondary_action() {
            d.hide();
        }
    });
    d.show();
}

function create_manychat_contact(frm, values) {
    // Remove any spaces, hyphens, or other characters from phone numbers
    const cleanPhone = values.phone.replace(/[^0-9]/g, '');
    const cleanWhatsApp = values.whatsapp_number ? values.whatsapp_number.replace(/[^0-9]/g, '') : '';

    // Remove leading zeros from phone numbers
    const trimmedPhone = cleanPhone.replace(/^0+/, '');
    const trimmedWhatsApp = cleanWhatsApp ? cleanWhatsApp.replace(/^0+/, '') : trimmedPhone;

    // Remove the '+' from country code and combine with phone numbers
    const countryCode = values.country_code.replace('+', '');
    const fullPhone = countryCode + trimmedPhone;
    const fullWhatsApp = countryCode + trimmedWhatsApp;

    frappe.call({
        method: "manychat_frappe_integration.manychat_frappe_integration.api.manychat_api.create_subscriber",
        args: {
            "first_name": values.first_name,
            "last_name": values.last_name || '',
            "phone": fullPhone,
            "whatsapp_phone": fullWhatsApp,
            "gender": values.gender,
            "email": values.email || '',
            "has_opt_in_sms": values.has_opt_in_sms ? 'true' : 'false',
            "has_opt_in_email": values.has_opt_in_email ? 'true' : 'false',
            "consent_phrase": values.consent_phrase,
            "docname": frm.doc.name,
            "doctype": frm.doc.doctype
        },
        freeze: true,
        freeze_message: __('Creating contact in ManyChat...'),
        callback: function (r) {
            if (r.message === "success") {
                frappe.show_alert({
                    message: __("Contact created successfully in ManyChat"),
                    indicator: 'green'
                }, 5);
                create_recipients_dialog(frm);
            } else {
                frappe.show_alert({
                    message: __("Failed to create contact in ManyChat: ") + r.message,
                    indicator: 'red'
                }, 7);
            }
        }
    });
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

            }
        }
    });
}