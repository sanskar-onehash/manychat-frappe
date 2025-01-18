from __future__ import unicode_literals

import frappe
from frappe import _
import http.client
import json, re
import string

@frappe.whitelist(allow_guest=True)
def get_manychat_templates():
    try:
        # tt = frappe.db.get_single_value("Manychat API Cloud Settings", "phone_number_id")
        tt = frappe.get_doc("Manychat API Cloud Settings")
        frappe.log_error('tt', tt)
        if not tt:
            return "Manychat API is not enabled"
        # if not frappe.db.get_single_value("Manychat API Cloud Settings", "enabled"):
            # return [False, "ManyChat Service is not Enabled"]
        
        # integrated_number = frappe.db.get_single_value("Manychat API Cloud Settings", "phone_number_id")
        url = frappe.db.get_single_value("Manychat API Cloud Settings", "url")
        # version = frappe.db.get_single_value("Manychat API Cloud Settings", "version")
        get_template_endpoint = frappe.db.get_single_value("Manychat API Cloud Settings", "endpoint")
        
        frappe.log_error("i am heree", get_template_endpoint)
        frappe.log_error("i am heree url", url)

        if not url and not get_template_endpoint:
            return [False, "Manychat  Service is not Configured Properly"]
        
        authKey = frappe.utils.password.get_decrypted_password(
            "Manychat API Cloud Settings", "Manychat API Cloud Settings", "access_token"
        )   
        
        headers = {
            'accept': "application/json",
            'authkey': authKey
        }

        # saved_templates = [x.name for x in frappe.get_list("Manychat  Templates")]
        conn = http.client.HTTPSConnection(url)

        conn.request("GET", f"/fb/page/{get_template_endpoint}", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        frappe.log_error("reposene when fetch", response)
        # parsed_data = parse_templates(response)
        result = create_template_records(response)
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
            doc.insert()
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