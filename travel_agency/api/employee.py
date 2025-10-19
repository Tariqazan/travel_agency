import frappe
from frappe import _
from frappe.utils import getdate, today
import erpnext

@frappe.whitelist()
def create_salary_structure_assignment(employee, salary_structure, from_date, base, variable=0, company=None):
	"""
	Create a salary structure assignment for an employee with basic component
	using the custom_amount field as the base amount
	"""
	try:
		# Validate inputs
		if not employee:
			frappe.throw(_("Employee is required"))
		
		if not salary_structure:
			frappe.throw(_("Salary Structure is required"))
		
		if not from_date:
			frappe.throw(_("From Date is required"))
		
		if not base:
			frappe.throw(_("Base amount is required"))
		
		# Get company if not provided
		if not company:
			company = frappe.get_cached_value("Employee", employee, "company")
			if not company:
				company = frappe.defaults.get_default("Company")
		
		# Get currency
		currency = frappe.get_cached_value("Company", company, "default_currency")
		if not currency:
			currency = erpnext.get_default_currency()
		
		# Check if assignment already exists for this employee and date
		existing_assignment = frappe.db.exists("Salary Structure Assignment", {
			"employee": employee,
			"from_date": from_date,
			"docstatus": 1
		})
		
		if existing_assignment:
			frappe.throw(_("Salary Structure Assignment already exists for this employee on {0}").format(from_date))
		
		# Get payroll payable account
		payroll_payable_account = frappe.get_cached_value("Company", company, "default_payroll_payable_account")
		if not payroll_payable_account:
			frappe.throw(_('Please set "Default Payroll Payable Account" in Company Defaults'))
		
		# Validate payroll payable account currency
		payroll_payable_account_currency = frappe.get_cached_value("Account", payroll_payable_account, "account_currency")
		company_currency = erpnext.get_company_currency(company)
		
		if payroll_payable_account_currency != currency and payroll_payable_account_currency != company_currency:
			frappe.throw(
				_("Invalid Payroll Payable Account. The account currency must be {0} or {1}").format(
					currency, company_currency
				)
			)
		
		# Create salary structure assignment
		assignment = frappe.new_doc("Salary Structure Assignment")
		assignment.employee = employee
		assignment.salary_structure = salary_structure
		assignment.company = company
		assignment.currency = currency
		assignment.payroll_payable_account = payroll_payable_account
		assignment.from_date = from_date
		assignment.base = float(base)
		assignment.variable = float(variable) if variable else 0
		
		# Save and submit
		assignment.save(ignore_permissions=True)
		assignment.submit()
		
		frappe.msgprint(_("Salary Structure Assignment created successfully: {0}").format(
			frappe.get_desk_link("Salary Structure Assignment", assignment.name)
		))
		
		return assignment.name
		
	except Exception as e:
		frappe.log_error(f"Error creating salary structure assignment: {str(e)}")
		frappe.throw(_("Error creating salary structure assignment: {0}").format(str(e)))
