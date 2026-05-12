import frappe

def verify():
	tz = frappe.db.get_single_value("System Settings", "time_zone")
	df = frappe.db.get_single_value("System Settings", "date_format")
	nf = frappe.db.get_single_value("System Settings", "number_format")
	now = frappe.utils.now()
	
	print(f"Timezone: {tz}")
	print(f"Date Format: {df}")
	print(f"Number Format: {nf}")
	print(f"Current Time (IST): {now}")

if __name__ == "__main__":
	verify()
