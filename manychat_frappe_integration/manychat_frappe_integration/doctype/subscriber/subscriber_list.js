frappe.listview_settings["Subscriber"] = {
    onload: function (listview) {
        // Hide the "Add Subscriber" button
        listview.page.wrapper
            .find('.primary-action')
            .hide();

        // Add your custom "Fetch Subscribers" button
        listview.page.add_inner_button("+ Add Subscriber", function () {
            // Show the dialog when the button is clicked
            let d = new frappe.ui.Dialog({
                title: "Add New Subscriber",
                fields: [
                    {
                        label: __("First Name"),
                        fieldtype: "Data",
                        reqd: 1,
                        fieldname: "first_name",
                        placeholder: __("Enter first name")
                    },
                    {
                        label: __("Last Name"),
                        fieldtype: "Data",
                        reqd: 1,
                        fieldname: "last_name",
                        placeholder: __("Enter last name")
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
                        label: __("Phone"),
                        fieldtype: "Data",
                        reqd: 1,
                        fieldname: "phone",
                        placeholder: __("Enter phone number"),
                    },
                    {
                        label: __("WhatsApp Number"),
                        fieldtype: "Data",
                        fieldname: "whatsapp_number",
                        placeholder: __("Enter WhatsApp number"),
                        description: __("Optional, if different from phone number")
                    },
                    {
                        label: __("Email"),
                        fieldtype: "Data",
                        fieldname: "email",
                        placeholder: __("Enter email")
                    },
                    {
                        label: __("Gender"),
                        fieldtype: "Select",
                        options: "Male\nFemale",
                        reqd: 1,
                        fieldname: "gender",
                        placeholder: __("Select gender")
                    },
                    {
                        label: __("SMS Opt-in"),
                        fieldtype: "Check",
                        fieldname: "has_opt_in_sms",
                        default: 1
                    },
                    {
                        label: __("Email Opt-in"),
                        fieldtype: "Check",
                        fieldname: "has_opt_in_email",
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
                primary_action_label: __("Create"),
                primary_action: function (values) {
                    if (!values.first_name || !values.last_name || !values.phone || !values.consent_phrase) {
                        frappe.msgprint(__('Please fill all required fields.'));
                        return;
                    }

                    // Remove any spaces, hyphens, or other characters from phone numbers
                    const cleanPhone = values.phone.replace(/[^0-9]/g, '');
                    const cleanWhatsApp = values.whatsapp_number ? values.whatsapp_number.replace(/[^0-9]/g, '') : '';

                    // Combine country code with phone numbers
                    const fullPhone = values.country_code + cleanPhone;
                    const fullWhatsApp = cleanWhatsApp ? values.country_code + cleanWhatsApp : null;

                    // Basic phone number validation
                    if (cleanPhone.length < 10) {
                        frappe.msgprint(__('Please enter a valid phone number with at least 10 digits.'));
                        return;
                    }

                    frappe.call({
                        method: "manychat_frappe_integration.manychat_frappe_integration.api.manychat_api.create_subscriber",
                        args: {
                            first_name: values.first_name,
                            last_name: values.last_name,
                            phone: fullPhone,
                            whatsapp_number: fullWhatsApp,
                            email: values.email,
                            gender: values.gender,
                            has_opt_in_sms: values.has_opt_in_sms,
                            has_opt_in_email: values.has_opt_in_email,
                            consent_phrase: values.consent_phrase,
                        },
                        callback: function (r) {
                            d.hide(); // Close the dialog
                            if (r.message === "success") {
                                frappe.msgprint({
                                    title: __('Success'),
                                    indicator: 'green',
                                    message: __('Subscriber added successfully')
                                });
                                listview.refresh(); // Refresh the list view to show the new subscriber
                            } else {
                                frappe.msgprint({
                                    title: __('Error'),
                                    indicator: 'red',
                                    message: __('Failed to add subscriber: ' + r.message)
                                });
                            }
                        }
                    });
                }
            });

            d.show();
        });
    }
};