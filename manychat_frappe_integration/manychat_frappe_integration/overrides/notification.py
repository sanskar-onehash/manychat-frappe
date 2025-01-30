import frappe
from frappe import _
import urllib
import json
import http.client
from frappe.email.doctype.notification.notification import Notification, get_context

class SendNotification(Notification):
    def send(self, doc):
        """
        Override the send method to handle WhatsApp templates via Manychat
        """
        context = get_context(doc)
        context = {"doc": doc, "alert": self, "comments": None}
        if doc.get("_comments"):
            context["comments"] = json.loads(doc.get("_comments"))

        if self.is_standard:
            self.load_standard_properties(context)

        try:
            if self.channel == 'WhatsApp':
                self.send_whatsapp_template(doc, context)
        except:
            frappe.log_error(title='Failed to send notification', message=frappe.get_traceback())

        super(SendNotification, self).send(doc)
        
    def get_subscriber_id(self, doc):
        try:
            if self.document_type == "Lead":
                lead_doc = frappe.get_doc("Lead", doc.name)
                return lead_doc.subscriber_id
            
        except Exception as e:
            frappe.log_error(
                "Subscriber ID Error",
                f"Failed to get subscriber_id for {self.document_type} {doc.name}: {str(e)}"
            )
            return None

    def send_whatsapp_template(self, doc, context):
        """
        Send WhatsApp template through Manychat
        """
        try:
            settings = frappe.get_all("Manychat API Cloud Settings")
            if not settings:
                frappe.log_error("Manychat Error", "ManyChat Service is not configured")
                return
                
            settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
            url = settings_doc.url
            
            if not url:
                frappe.log_error("Manychat Error", "ManyChat Service URL is not configured")
                return
            
            auth_token = frappe.utils.password.get_decrypted_password(
                "Manychat API Cloud Settings",
                settings[0]["name"],
                "access_token"
            )
            
            # Get template from the notification document
            if not self.template:
                frappe.log_error("Manychat Error", "Template not selected in notification")
                return template
                
            template = frappe.get_doc("Manychat Templates", self.template)
            if not template:
                frappe.log_error("Manychat Error", "Template not found")
                return
                
            # Get subscriber_id from the document
            subscriber_id = self.get_subscriber_id(doc)
            if not subscriber_id:
                frappe.log_error("Manychat Error", 
                    f"Subscriber ID not found for {self.document_type} {doc.name}")
                return
                
            headers = {
                'accept': "application/json",
                'Authorization': f"Bearer {auth_token}",
                'content-type': "application/json"
            }

            conn = http.client.HTTPSConnection(url)
            
            payload = {
                "subscriber_id": subscriber_id,
                "flow_ns": template.template_id
            }
            
            # # Add dynamic variables if configured in notification
            # if hasattr(self, 'template_variables') and self.template_variables:
            #     variables = json.loads(self.template_variables)
            #     payload["variables"] = variables
            
            conn.request(
                "POST", 
                f"/fb/sending/sendFlow", 
                body=json.dumps(payload), 
                headers=headers
            )
            
            res = conn.getresponse()
            data = res.read()
            response = json.loads(data.decode("utf-8"))
            
            if res.status != 200:
                frappe.log_error(
                    "Manychat Template Send Error",
                    f"Failed to send template: {response.get('message', 'Unknown error')}"
                )
            else:
                frappe.logger().debug(f"Successfully sent Manychat template to {doc.subscriber_id}")
                
        except Exception as e:
            frappe.log_error("Manychat Template Send Error", str(e))