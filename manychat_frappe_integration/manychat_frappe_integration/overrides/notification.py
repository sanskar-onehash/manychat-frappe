import frappe
import json
import http.client
from frappe.utils import password
from frappe.email.doctype.notification.notification import get_context
from manychat_frappe_integration.app_config import APP_TITLE


def manhychat_validate(notificaiton_doc):
    pass


def manychat_send(notification_doc, doc):
    """
    Override the send method to handle WhatsApp templates via Manychat
    """
    if (
        notification_doc.channel == "WhatsApp"
        and notification_doc.custom_whatsapp_app == APP_TITLE
    ):
        context = get_context(doc)
        context = {"doc": doc, "alert": notification_doc, "comments": None}
        if doc.get("_comments"):
            context["comments"] = json.loads(doc.get("_comments"))

        if notification_doc.is_standard:
            notification_doc.load_standard_properties(context)

        try:
            if notification_doc.channel == "WhatsApp":
                send_whatsapp_template(notification_doc, doc, context)
        except:
            frappe.log_error(
                title="Failed to send notification", message=frappe.get_traceback()
            )


def get_subscriber_id(notification_doc, doc):
    try:
        if notification_doc.document_type == "Lead":
            lead_doc = frappe.get_doc("Lead", doc.name)
            return lead_doc.subscriber_id

    except Exception as e:
        frappe.log_error(
            "Subscriber ID Error",
            f"Failed to get subscriber_id for {notification_doc.document_type} {doc.name}: {str(e)}",
        )
        return None


def send_whatsapp_template(notification_doc, doc, context):
    """
    Send WhatsApp template through Manychat
    """
    try:
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            frappe.log_error("Manychat Error", "ManyChat Service is not configured")
            return

        settings_doc = frappe.get_doc(
            "Manychat API Cloud Settings", settings[0]["name"]
        )
        url = settings_doc.url

        if not url:
            frappe.log_error("Manychat Error", "ManyChat Service URL is not configured")
            return

        auth_token = password.get_decrypted_password(
            "Manychat API Cloud Settings", settings[0]["name"], "access_token"
        )

        # Get template from the notification document
        if not notification_doc.manychat_whatsapp_template:
            frappe.log_error("Manychat Error", "Template not selected in notification")
            return

        template = frappe.get_doc(
            "Manychat Templates", notification_doc.manychat_whatsapp_template
        )
        if not template:
            frappe.log_error("Manychat Error", "Template not found")
            return

        # Get subscriber_id from the document
        subscriber_id = get_subscriber_id(notification_doc, doc)
        if not subscriber_id:
            frappe.log_error(
                "Manychat Error",
                f"Subscriber ID not found for {notification_doc.document_type} {doc.name}",
            )
            return

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {auth_token}",
            "content-type": "application/json",
        }

        conn = http.client.HTTPSConnection(url)

        payload = {"subscriber_id": subscriber_id, "flow_ns": template.template_id}

        # # Add dynamic variables if configured in notification
        # if hasattr(self, 'template_variables') and self.template_variables:
        #     variables = json.loads(self.template_variables)
        #     payload["variables"] = variables

        conn.request(
            "POST", "/fb/sending/sendFlow", body=json.dumps(payload), headers=headers
        )

        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))

        if res.status != 200:
            frappe.log_error(
                "Manychat Template Send Error",
                f"Failed to send template: {response.get('message', 'Unknown error')}",
            )
        else:
            frappe.logger().debug(
                f"Successfully sent Manychat template to {doc.subscriber_id}"
            )

    except Exception as e:
        frappe.log_error("Manychat Template Send Error", str(e))
