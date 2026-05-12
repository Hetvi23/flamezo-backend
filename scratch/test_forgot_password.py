import frappe

def test_forgot_password_api():
    # We'll try to find a user first
    user = frappe.db.get_value("User", {"email": ["!=", "Guest"]}, "email")
    if not user:
        print("No user found for testing")
        return

    print(f"Testing forgot password for user: {user}")
    
    try:
        # Standard Frappe method to send reset instructions
        from frappe.core.doctype.user.user import reset_password
        reset_password(user)
        print("Successfully called reset_password")
    except Exception as e:
        print(f"Error calling reset_password: {e}")

if __name__ == "__main__":
    frappe.init(site="dine_matters")
    frappe.connect()
    test_forgot_password_api()
