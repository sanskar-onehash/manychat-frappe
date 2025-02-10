import frappe
from frappe import _

@frappe.whitelist()
def search_lead_by_mobile(mobile_no):
    # Convert to string and clean the number
    mobile_no = str(mobile_no)
    clean_no = ''.join(filter(str.isdigit, mobile_no))
    
    frappe.log_error("clean no is", clean_no)
    
    if not clean_no:
        frappe.throw(_("Please enter a valid mobile number"))
    
    # Prepare the search number
    search_no = clean_no[-10:] if len(clean_no) > 10 else clean_no
    frappe.log_error("search number is", search_no)
    
    # Search with OR conditions for phone or mobile_no fields
    leads = frappe.get_all(
        "Lead",
        filters=[
            ["mobile_no", "like", f"%{search_no}%"]
        ],
        fields=["name"],
        limit=1,
        ignore_permissions=True,
        order_by="creation desc"
    )
    
    frappe.log_error("leads are", leads)
    
    if leads:
        return leads[0].name
        
    return None