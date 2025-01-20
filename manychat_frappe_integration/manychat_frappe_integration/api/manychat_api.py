from __future__ import unicode_literals

import frappe
from frappe import _
import http.client
import json, re
import string

@frappe.whitelist(allow_guest=True)
def get_manychat_templates():
    try:
        tt = frappe.get_all("Manychat API Cloud Settings")
        if tt:
            settings_doc = frappe.get_doc("Manychat API Cloud Settings", tt[0]["name"])

            # Extract values from the document
            url = settings_doc.url
            get_template_endpoint = settings_doc.endpoint
            # Similarly, get other fields if needed
            phone_number_id = settings_doc.phone_number_id
            
        if not url and not get_template_endpoint:
            return [False, "Manychat  Service is not Configured Properly"]
        
        authKey = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings", 
            tt[0]["name"],  
            "access_token"
        )
        
        headers = {
            'accept': "application/json",
            'Authorization': f"Bearer {authKey}"
        }
        
        frappe.log_error("headers are", headers)
        
        frappe.log_error("Request details", {
            'url': url,
            'endpoint': get_template_endpoint,
            'headers': headers
        })
        
        clean_url = url.replace('https://', '').replace('http://', '')

        # saved_templates = [x.name for x in frappe.get_list("Manychat  Templates")]
        conn = http.client.HTTPSConnection(clean_url)
        frappe.log_error("conn", conn)
        
        endpoint = f"/fb/page/{get_template_endpoint}"
        
        conn.request("GET", endpoint, headers=headers)
        
        response = conn.getresponse()
        frappe.log_error("Response status", {
                'status': response.status,
                'reason': response.reason
        })

        # a= conn.request("GET", f"/fb/page/{get_template_endpoint}", headers=headers)
        # frappe.log_error('a', a)
        
        
        # res = conn.getresponse()
        # frappe.log_error('res', res)
        
        data = response.read()
        frappe.log_error('data', data)
        
        response_data = json.loads(data.decode("utf-8"))
        frappe.log_error("reposene when fetch", response_data)
        # parsed_data = parse_templates(response)
        result = create_template_records(response_data)
        return result
    except Exception as e:
        return [False, "Check Manychat Configuration"]
    
    

def create_template_records(data):
    try:
        if not isinstance(data, dict):
            frappe.log_error("Invalid data format", data)
            return [False, "Invalid data format received"]

        if 'status' not in data or 'data' not in data:
            frappe.log_error("Missing required response fields", data)
            return [False, "Invalid response structure"]

        if data['status'] != 'success':
            frappe.log_error("API returned non-success status", data)
            return [False, "API request was not successful"]

        flows = data.get('data', {}).get('flows', [])
        if not flows:
            return [True, "No templates found"]

        template_records = []
        for template in flows:
            template_name = template.get('name')
            template_id = template.get('ns')
            folder_id = template.get('folder_id')
                
            if not all([template_name, template_id is not None, folder_id is not None]):
                frappe.log_error(f"Missing required template fields: {template}")
                continue

            existing_template = frappe.db.exists(
                "Manychat Templates",
                {
                    "name": template_name
                }
            )
            if existing_template:
                continue

            doc = frappe.get_doc({
                'doctype': 'Manychat Templates',
                'enabled': 1,
                'template_name': template_name,
                'template_id': template_id,
                'folder_id': folder_id
            })
            doc.insert(ignore_permissions=True)
            template_records.append({
                'template_name': template_name,
                'template_id': template_id,
                'folder_id': folder_id
            })

        frappe.log_error("templates", template_records)
        return [True, f"Successfully processed {len(template_records)} templates"]  
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Templates Errored")
        return [False, "Failed to Save the Template"]
    
    

@frappe.whitelist()
def send_template(doctype, docname, args):
    try:
        # Get ManyChat settings
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            return {"status": "error", "message": "ManyChat Service is not configured"}
            
        settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
        
        # Extract required settings
        url = settings_doc.url
        phone_number_id = settings_doc.phone_number_id
        
        if not url:
            return {"status": "error", "message": "ManyChat Service is not configured properly"}
        
        # Get decrypted auth token
        auth_token = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings",
            settings[0]["name"],
            "access_token"
        )
        
        # Prepare headers
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'Authorization': f"Bearer {auth_token}"
        }
        
        # Log headers for debugging
        frappe.log_error("Send template headers", headers)
        
        # Get template details
        template = frappe.get_doc("Manychat Templates", args.get("manychat_templates"))
        if not template:
            return {"status": "error", "message": "Template not found"}
            
        # Get document details
        doc = frappe.get_doc(doctype, docname)
        if not doc:
            return {"status": "error", "message": "Document not found"}
            
        # Prepare payload
        payload = {
            "subscriber_id": doc.subscriber_id,
            "flow_ns": template.template_id
        }
        
        # Log request details
        frappe.log_error("Send template request details", {
            'url': url,
            'endpoint': '/fb/sending/sendFlow',
            'payload': payload
        })
        
        # Prepare connection
        clean_url = url.replace('https://', '').replace('http://', '')
        conn = http.client.HTTPSConnection(clean_url)
        
        # Make request
        endpoint = "/fb/sending/sendFlow"
        conn.request("POST", endpoint, body=json.dumps(payload), headers=headers)
        
        # Get response
        response = conn.getresponse()
        
        # Log response status
        frappe.log_error("Send template response status", {
            'status': response.status,
            'reason': response.reason
        })
        
        # Read and parse response
        data = response.read()
        response_data = json.loads(data.decode("utf-8"))
        
        # Log response data
        frappe.log_error("Send template response", response_data)
        
        # Check response status
        if response.status == 200:
            return {"status": "success", "message": "WhatsApp message sent successfully"}
        else:
            error_message = response_data.get('message', 'Unknown error occurred')
            return {"status": "error", "message": error_message}
            
    except Exception as e:
        frappe.log_error(title="ManyChat Send Template Error", message=str(e))
        return {"status": "error", "message": "Error sending WhatsApp message"}
    
    

@frappe.whitelist()
def create_subscriber(first_name, last_name, phone, gender, email, has_opt_in_sms, has_opt_in_email, consent_phrase, whatsapp_number=None):
    try:
        # Get ManyChat settings
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            return "ManyChat Service is not configured"
            
        settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
        
        # Extract required settings
        url = settings_doc.url
        
        if not url:
            return "ManyChat Service is not configured properly"
        
        # Get decrypted auth token
        auth_token = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings",
            settings[0]["name"],
            "access_token"
        )
        
        frappe.log_error("auth_token", auth_token)
        
        # Prepare headers
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'Authorization': f"Bearer {auth_token}"
        }
        
        # Prepare payload
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "whatsapp_phone": whatsapp_number if whatsapp_number else phone,
            "gender": gender,
            "email": email,
            "has_opt_in_sms": has_opt_in_sms,
            "has_opt_in_email": has_opt_in_email,
            "consent_phrase": consent_phrase
        }
        
        
        # Log request details
        frappe.log_error("Create subscriber request details", {
            'url': url,
            'endpoint': '/fb/subscriber/createSubscriber',
            'payload': payload
        })
        
        # Prepare connection
        clean_url = url.replace('https://', '').replace('http://', '')
        conn = http.client.HTTPSConnection(clean_url)
        
        # Make request
        endpoint = "/fb/subscriber/createSubscriber"
        conn.request("POST", endpoint, body=json.dumps(payload), headers=headers)
        
        # Get response
        response = conn.getresponse()
        response_data = json.loads(response.read().decode("utf-8"))
        
        # Log response
        frappe.log_error("Create subscriber response", response_data)
        
        if response.status == 200 and response_data.get("status") == "success":
            # Create new subscriber document
            subscriber = frappe.get_doc({
                "doctype": "Subscriber",
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "whatsapp_number": whatsapp_number if whatsapp_number else phone,
                "subscriber_id": response_data["data"].get("id"),
                "gender": response_data["data"].get("gender"),
                "email": email
                # "page_id": response_data["data"].get("page_id"),
                # "profile_pic": response_data["data"].get("profile_pic"),
                # "locale": response_data["data"].get("locale"),
                # "language": response_data["data"].get("language"),
                # "timezone": response_data["data"].get("timezone"),
                # "optin_phone": response_data["data"].get("optin_phone", 0),
                # "optin_whatsapp": response_data["data"].get("optin_whatsapp", 0),
                # "subscribed_date": datetime.now(),
                # "last_interaction": response_data["data"].get("last_interaction"),
                # "last_seen": response_data["data"].get("last_seen"),
                # "is_followup_enabled": response_data["data"].get("is_followup_enabled", 0)
            })
            
            subscriber.insert(ignore_permissions=True)
            frappe.db.commit()
            
            return "success"
        else:
            error_message = response_data.get('message', 'Unknown error occurred')
            return error_message
            
    except Exception as e:
        frappe.log_error(title="ManyChat Create Subscriber Error", message=str(e))
        return str(e)
    

@frappe.whitelist()
def send_template(**args):
    try:
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            return "ManyChat Service is not configured"
            
        settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
        
        # Extract required settings
        url = settings_doc.url
        
        if not url:
            return "ManyChat Service is not configured properly"
        
        auth_token = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings",
            settings[0]["name"],
            "access_token"
        )
        
        # Get template_name from args
        if isinstance(args.get('args'), str):
            nested_args = json.loads(args.get('args'))
        else:
            # If args is already a dictionary
            nested_args = args.get('args', {})
            
        template_name = nested_args.get('manychat_templates')
        if not template_name:
            return {"status": "error", "message": "Template not selected"}
            
        template = frappe.get_doc("Manychat Templates", template_name)
        if not template:
            return {"status": "error", "message": "Template not configured"}
            
        doctype = nested_args.get('doctype')
        docname = nested_args.get('docname')
        if not doctype or not docname:
            return {"status": "error", "message": "Document information missing"}
            
        doc = frappe.get_doc(doctype, docname)
        if not doc.subscriber_id:
            return {"status": "error", "message": "Subscriber ID not found in current document"}
            
        headers = {
            'accept': "application/json",
            'Authorization': f"Bearer {auth_token}",
            'content-type': "application/json"
        }

        conn = http.client.HTTPSConnection(url)
        
        payload = {
            "subscriber_id": doc.subscriber_id,
            "flow_ns": template.template_id
        }
        
        frappe.log_error("payload is", payload)
        frappe.log_error("headers is", headers)
        
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
            frappe.log_error("Template Sending Error", response)
            return {"status": "error", "message": response.get('message', 'Failed to send template')}
            
        return {"status": "success", "message": "Flow sent successfully"}
            
    except Exception as e:
        frappe.log_error("ManyChat Flow Send Error", str(e))
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def sync_contact():
    try:
        payload = frappe.request.json
        
        if not payload or 'data' not in payload:
            frappe.log_error("Invalid payload structure")
            return {
                "status": "error",
                "message": "Invalid payload structure"
            }
        
        # Extract data from the payload's data field
        data = payload['data']
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        gender = data.get('gender')
        phone_number = data.get('phone')
        subscriber_id = data.get('id')
        whatsapp_phone = data.get('whatsapp_phone')
        
        # Create new subscriber
        doc = frappe.get_doc({
            "doctype": "Subscriber",
            "name": first_name,
            "subscriber_id": subscriber_id,
            "last_name": last_name,
            "phone": phone_number,
            "gender": gender,
            "email": email,
            "whatsapp_number": whatsapp_phone,
        })
        
        doc.insert()
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": "Subscriber created successfully"
        }
            
    except Exception as e:
        frappe.log_error(f"Error creating subscriber: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }