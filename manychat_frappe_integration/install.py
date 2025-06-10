import frappe
from manychat_frappe_integration.app_config import APP_TITLE


def after_install():
    try:
        add_app_to_whatsapp_apps()
        add_custom_fields_to_notification()
    except Exception as e:
        frappe.log_error(f"Error occured after installing {APP_TITLE} app:", e)


def add_app_to_whatsapp_apps():
    try:
        field = frappe.db.get_list(
            "Custom Field",
            ["*"],
            {"dt": "Notification", "fieldname": "custom_whatsapp_app"},
        )[0]

        options = field.get("options", "").split("\n")

        if APP_TITLE not in options:
            options.append(APP_TITLE)
            frappe.db.set_value(
                "Custom Field", field.name, "options", "\n".join(options)
            )
            frappe.db.commit()
    except IndexError:
        raise Exception("Notification field custom_whatsapp_app not present.")


def add_custom_fields_to_notification():
    custom_fields = [
        {
            "depends_on": 'eval: (doc.channel == "WhatsApp") && (doc.custom_whatsapp_app == "ManyChat")',
            "description": "Preffered to use pre-approved template.",
            "dt": "Notification",
            "fieldname": "manychat_whatsapp_template",
            "fieldtype": "Link",
            "insert_after": "custom_whatsapp_app",
            "label": "WhatsApp Template",
            "mandatory_depends_on": 'eval: (doc.channel == "WhatsApp") && (doc.custom_whatsapp_app == "ManyChat")',
            "module": "Manychat Frappe Integration",
            "name": "Notification-manychat_whatsapp_template",
            "options": "Manychat Templates",
        }
    ]

    for field in custom_fields:
        if not frappe.db.exists(
            "Custom Field", {"dt": "Notification", "fieldname": field["fieldname"]}
        ):
            new_field = frappe.get_doc({"doctype": "Custom Field", **field})
            new_field.insert()
            frappe.db.commit()
