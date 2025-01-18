import frappe


def get_access_token():
	return frappe.utils.password.get_decrypted_password(
		"Manychat API Cloud Settings", "Manychat API Cloud Settings", "access_token"
	)