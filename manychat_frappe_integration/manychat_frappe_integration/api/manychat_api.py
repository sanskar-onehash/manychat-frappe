from __future__ import unicode_literals

import frappe
from frappe import _
import http.client
import json, re
import string

@frappe.whitelist()
def get_manychat_templates():
    try:
        tt = frappe.get_all("Manychat API Cloud Settings")
        if tt:
            settings_doc = frappe.get_doc("Manychat API Cloud Settings", tt[0]["name"])

            # Extract values from the document
            url = settings_doc.url
            get_template_endpoint = settings_doc.endpoint
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
        
        clean_url = url.replace('https://', '').replace('http://', '')
        conn = http.client.HTTPSConnection(clean_url)
        endpoint = f"/fb/page/{get_template_endpoint}"
        conn.request("GET", endpoint, headers=headers)
        response = conn.getresponse()
        
        data = response.read()
        response_data = json.loads(data.decode("utf-8"))
        result = create_template_records(response_data)
        
        return result
    
    except Exception as e:
        return [False, "Check Manychat Configuration"]
    

def create_template_records(data):
    try:
        TARGET_FOLDER_ID = 27451007
        
        if not isinstance(data, dict):
            return [False, "Invalid data format received"]

        if 'status' not in data or 'data' not in data:
            return [False, "Invalid response structure"]

        if data['status'] != 'success':
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
                continue
            
            if folder_id != TARGET_FOLDER_ID:
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

        return [True, f"Successfully processed {len(template_records)} templates"]  
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Templates Errored")
        return [False, "Failed to Save the Template"]
    

@frappe.whitelist()
def check_contact_exists(docname):
    try:
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            return {"status": "error", "message": "ManyChat Service is not configured"}
        
        settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
        url = settings_doc.url
        
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
            'Authorization': f"Bearer {auth_token}",
            'content-type': "application/json"
        }
        
        # Prepare connection
        clean_url = url.replace('https://', '').replace('http://', '')
        conn = http.client.HTTPSConnection(clean_url)
        
        # Get the lead document
        lead_doc = frappe.get_doc("Lead", docname)
        
        # Get phone number from lead and remove '+' if present
        phone = lead_doc.mobile_no
        if not phone:
            return {"status": "error", "message": "Phone number is not set for this contact"}
        
        phone = phone.replace('+', '').replace(' ', '')
        if not phone.startswith('91'):
            phone = f"91{phone}"
        
        # Use the provided WhatsappID field_id directly
        whatsapp_field_id = 12373759
        
        # Use findByCustomField API to check contact existence
        find_by_custom_field_endpoint = f"/fb/subscriber/findByCustomField?field_id={whatsapp_field_id}&field_value={phone}"
        conn.request("GET", find_by_custom_field_endpoint, headers=headers)
        find_response = conn.getresponse()
        
        find_response_data = json.loads(find_response.read().decode("utf-8"))
        
        if find_response.status == 200 and find_response_data.get("status") == "success":
            subscriber_data = None
            
            if find_response_data.get("data") and len(find_response_data["data"]) > 0:
                subscriber_data = find_response_data["data"][0]

            if subscriber_data and subscriber_data.get("id"):
                subscriber_id = subscriber_data["id"]
                frappe.db.set_value("Lead", docname, {
                    "subscriber_id": subscriber_id,
                })
                frappe.db.commit()
            
            if find_response_data.get("data"):
                return {
                    "status": "success",
                    "message": "Contact exists in ManyChat",
                    "exists": True,
                    "phone": phone,
                    "contact_data": find_response_data.get("data")[0] 
                }
            else:
                return {
                    "status": "success",  
                    "message": "Contact does not exist in ManyChat",
                    "exists": False,
                    "phone": phone
                }
                
        return {"status": "error", "message": "Failed to fetch contact from ManyChat"}
    
    except Exception as e:
        frappe.log_error(title="ManyChat Contact Integration Error", message=str(e))
        return {"status": "error", "message": str(e)}
    

@frappe.whitelist()
def create_subscriber(first_name, last_name, phone, gender, has_opt_in_sms, has_opt_in_email, consent_phrase, doctype=None, docname=None, whatsapp_phone=None, email=None):
    try:
        # Get ManyChat settings
        settings = frappe.get_all("Manychat API Cloud Settings")
        if not settings:
            return "ManyChat Service is not configured"
        
        settings_doc = frappe.get_doc("Manychat API Cloud Settings", settings[0]["name"])
        url = settings_doc.url
        if not url:
            return "ManyChat Service is not configured properly"

        # Get decrypted auth token
        auth_token = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings", settings[0]["name"], "access_token"
        )

        # Prepare headers
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'Authorization': f"Bearer {auth_token}"
        }

        # Prepare payload matching the required format
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "whatsapp_phone": whatsapp_phone if whatsapp_phone else phone,
            "gender": gender,
            "email": email,
            "has_opt_in_sms": has_opt_in_sms,
            "has_opt_in_email": has_opt_in_email,
            "consent_phrase": consent_phrase
        }


        # Make request to ManyChat
        clean_url = url.replace('https://', '').replace('http://', '')
        conn = http.client.HTTPSConnection(clean_url)
        conn.request("POST", "/fb/subscriber/createSubscriber", body=json.dumps(payload), headers=headers)
        
        response = conn.getresponse()
        response_data = json.loads(response.read().decode("utf-8"))

        if response.status == 200 and response_data.get("status") == "success":
            subscriber_id = response_data["data"].get("id")
            
            if doctype == "Lead":
                # For Lead doctype, only update the subscriber_id
                frappe.db.set_value("Lead", docname, {
                    "subscriber_id": subscriber_id,
                })
                frappe.db.commit()
            else:
                # Check for existing subscriber with the same phone number
                existing_subscriber = frappe.get_all(
                    "Subscriber",
                    filters={"whatsapp_number": whatsapp_phone if whatsapp_phone else phone},
                    fields=["name", "subscriber_id"]
                )
                
                if existing_subscriber:
                    frappe.db.set_value("Subscriber", docname, "subscriber_id", existing_subscriber[0].subscriber_id)
                    frappe.db.commit()
                    return "Updated existing subscriber"
    
                # For subscriber doctypes, create new subscriber document
                else:
                    subscriber = frappe.get_doc({
                        "doctype": "Subscriber",
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "whatsapp_number": whatsapp_phone if whatsapp_phone else phone,
                        "subscriber_id": subscriber_id,
                        "gender": response_data["data"].get("gender"),
                        "email": email
                    })
                    subscriber.save(ignore_permissions=True)
                    frappe.db.commit()
            
            return "success"
        else:
            error_details = response_data.get('details', {})
            error_messages = []
            
            if 'messages' in error_details:
                for field, errors in error_details['messages'].items():
                    if isinstance(errors, dict) and 'message' in errors:
                        error_messages.append(f"{field}: {errors['message']}")
                    elif isinstance(errors, list):
                        error_messages.append(f"{field}: {', '.join(errors)}")
            
            error_message = ' | '.join(error_messages) if error_messages else response_data.get('message', 'Unknown error occurred')
            return f"Error: {error_message}"

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
            return {"status": "error", "message": response.get('message', 'Failed to send template')}
            
        return {"status": "success", "message": "Template sent successfully"}
            
    except Exception as e:
        frappe.log_error("Template Send Error", str(e))
        return {"status": "error", "message": str(e)}
    
    

@frappe.whitelist()
def sync_contact():
    try:
        payload = frappe.request.json
        
        first_name = payload.get('first_name')
        last_name = payload.get('last_name')
        email = payload.get('email')
        gender = payload.get('gender')
        phone_number = payload.get('phone')
        subscriber_id = payload.get('id')
        whatsapp_id = payload.get('custom_fields', {}).get('WhatsappID')
        
        existing_lead = frappe.db.exists("Lead", {"subscriber_id": subscriber_id})
        
        if existing_lead:
            doc = frappe.get_doc("Lead", existing_lead)
            doc.update({
                "first_name": first_name,
                "last_name": last_name,
                "subscriber_id": subscriber_id,
                "phone": phone_number,
                "gender": gender,
                "email": email,
                "mobile_no": whatsapp_id,
                "source": "Manychat"
            })
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "status": "success",
                "message": "Lead updated successfully"
            }
        else:
            # Create new subscriber
            doc = frappe.get_doc({
                "doctype": "Lead",
                "first_name": first_name,
                "subscriber_id": subscriber_id,
                "last_name": last_name,
                "phone": phone_number,
                "gender": gender,
                "email": email,
                "mobile_no": whatsapp_id,
                "source": "Manychat"
            })
            
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "status": "success",
                "message": "Lead created successfully"
            }
            
    except Exception as e:
        frappe.log_error(f"Error creating Lead: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }