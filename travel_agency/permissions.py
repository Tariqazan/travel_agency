import frappe


# -------------------------------------------------------------------
# 🔹 Utility functions (shared)
# -------------------------------------------------------------------
def get_user_branch(user):
    """Return the branch for a user based on their linked Employee record."""
    return frappe.db.get_value("Employee", {"user_id": user}, "branch")


def get_employee_id(user):
    """Return the Employee ID linked to the given user."""
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def user_roles(user):
    """Return roles for the user."""
    return frappe.get_roles(user)


# -------------------------------------------------------------------
# 🔹 EMPLOYEE permissions
# -------------------------------------------------------------------
def get_permission_query_conditions_employee(user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return ""

    # Branch Manager: employees in same branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch:
            return f"`tabEmployee`.branch = '{branch}'"
        return "1=0"

    # Branch User: only their own employee record
    if "Branch User" in roles:
        return f"`tabEmployee`.user_id = '{user}'"

    return "1=0"


def has_permission_employee(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return True

    # Branch Manager: employees in same branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        return branch and doc.branch == branch

    # Branch User: only their own record
    if "Branch User" in roles:
        return doc.user_id == user

    return False


def get_permission_query_conditions_employee_field(doctype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return ""

    # Branch Manager: records for employees in their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch:
            employee_ids = frappe.db.get_all(
                "Employee", filters={"branch": branch}, pluck="name"
            )
            if employee_ids:
                employees_str = "', '".join(employee_ids)
                return f"`tab{doctype}`.employee IN ('{employees_str}')"
        return "1=0"

    # Branch User: only their own records
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        if employee_id:
            return f"`tab{doctype}`.employee = '{employee_id}'"
        return "1=0"

    return "1=0"


def has_permission_employee_field(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return True

    # Branch Manager: only records within their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if not branch:
            return False
        applicant_branch = frappe.db.get_value("Employee", doc.employee, "branch")
        return applicant_branch == branch

    # Branch User: only their own
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        return doc.employee == employee_id

    return False


# -------------------------------------------------------------------
# 🔹 Generic permission logic for Loan, Loan Application,
#    Loan Disbursement, Loan Repayment
# -------------------------------------------------------------------
def get_permission_query_conditions_for_loan_related(doctype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return ""

    # Branch Manager: records for employees in their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch:
            employee_ids = frappe.db.get_all(
                "Employee", filters={"branch": branch}, pluck="name"
            )
            if employee_ids:
                field = "applicant"
                employees_str = "', '".join(employee_ids)
                return f"`tab{doctype}`.{field} IN ('{employees_str}')"
        return "1=0"

    # Branch User: only their own records
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        if employee_id:
            field = "applicant"
            return f"`tab{doctype}`.{field} = '{employee_id}'"
        return "1=0"

    return "1=0"


def has_permission_for_loan_related(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return True

    # Branch Manager: only records within their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if not branch:
            return False
        
        field = "applicant" if doc.doctype in ["Loan", "Loan Request"] else "employee"
        applicant_branch = frappe.db.get_value("Employee", doc.get(field), "branch")
        return applicant_branch == branch

    # Branch User: only their own
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        field = "applicant" if doc.doctype == "Loan" else "employee"
        return doc.get(field) == employee_id

    return False


# -------------------------------------------------------------------
# 🔹 Doctype-specific wrappers
# -------------------------------------------------------------------
def get_permission_query_conditions_loan_request(user):
    return get_permission_query_conditions_for_loan_related("Loan Request", user)


def get_permission_query_conditions_loan(user):
    return get_permission_query_conditions_for_loan_related("Loan", user)


def has_permission_loan_request(doc, ptype, user):
    return has_permission_for_loan_related(doc, ptype, user)


def has_permission_loan(doc, ptype, user):
    return has_permission_for_loan_related(doc, ptype, user)


def get_permission_query_conditions_loan_application(user):
    return get_permission_query_conditions_for_loan_related("Loan Application", user)


def has_permission_loan_application(doc, ptype, user):
    return has_permission_for_loan_related(doc, ptype, user)


def get_permission_query_conditions_loan_disbursement(user):
    return get_permission_query_conditions_for_loan_related("Loan Disbursement", user)


def has_permission_loan_disbursement(doc, ptype, user):
    return has_permission_for_loan_related(doc, ptype, user)


def get_permission_query_conditions_loan_repayment(user):
    return get_permission_query_conditions_for_loan_related("Loan Repayment", user)


def has_permission_loan_repayment(doc, ptype, user):
    return has_permission_for_loan_related(doc, ptype, user)


def get_permission_query_conditions_leave_application(user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return ""

    # Branch Manager: records for employees in their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch:
            employee_ids = frappe.db.get_all(
                "Employee", filters={"branch": branch}, pluck="name"
            )
            if employee_ids:
                employees_str = "', '".join(employee_ids)
                return f"`tabLeave Application`.employee IN ('{employees_str}')"
        return "1=0"

    # Branch User: only their own records
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        if employee_id:
            return f"`tabLeave Application`.employee = '{employee_id}'"
        return "1=0"

    return "1=0"


def has_permission_leave_application(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    # Central Branch Manager: access all
    if "Central Branch Manager" in roles:
        return True

    # Branch Manager: only records within their branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if not branch:
            return False
        applicant_branch = frappe.db.get_value("Employee", doc.employee, "branch")
        return applicant_branch == branch

    # Branch User: only their own
    if "Branch User" in roles:
        employee_id = get_employee_id(user)
        return doc.employee == employee_id

    return False


# Wrappers for each doctype
def get_permission_query_conditions_leave_allocation(user):
    return get_permission_query_conditions_employee_field("Leave Allocation", user)


def has_permission_leave_allocation(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_attendance(user):
    return get_permission_query_conditions_employee_field("Attendance", user)


def has_permission_attendance(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_employee_checkin(user):
    return get_permission_query_conditions_employee_field("Employee Checkin", user)


def has_permission_employee_checkin(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_expense_claim(user):
    return get_permission_query_conditions_employee_field("Expense Claim", user)


def has_permission_expense_claim(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_salary_slip(user):
    return get_permission_query_conditions_employee_field("Salary Slip", user)


def has_permission_salary_slip(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_sales_person(user):
    return get_permission_query_conditions_employee_field("Sales Person", user)


def has_permission_sales_person(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)

def get_permission_query_conditions_sales_invoice(user=None):
    """
    Permission Query for Sales Invoice.
    Limits invoices based on linked customer(s) in `tabCustomer List` child table.
    """

    if not user:
        user = frappe.session.user

    # Admin can see all
    if user == "Administrator":
        return ""

    roles = user_roles(user)

    # Central Branch Manager can see all
    if "Central Branch Manager" in roles:
        return ""

    # Customer / Portal User: see only invoices linked to their customer(s)
    if "Customer" in roles or "Portal User" in roles:
        # Get all customers linked to this user via portal_users child table
        customer_list = frappe.db.sql_list("""
            SELECT parent
            FROM `tabPortal User`
            WHERE user = %s
        """, (user,))

        # If no customers, return a condition that matches nothing
        if not customer_list:
            return "1=0"

        # Build safe SQL condition
        customer_conditions = ", ".join([f"'{c}'" for c in customer_list])
        return f"""
            EXISTS (
                SELECT 1
                FROM `tabCustomer List`
                WHERE `tabCustomer List`.parent = `tabSales Invoice`.name
                AND `tabCustomer List`.customer IN ({customer_conditions})
            )
        """

    # Branch Manager: invoices limited to their branch via custom_branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch:
            return f"`tabSales Invoice`.custom_branch = '{branch}'"
        return "1=0"

    # Branch User: only their own invoices (owner)
    if "Branch User" in roles:
        return f"`tabSales Invoice`.owner = '{user}'"

    # Default: no access
    return "1=0"


def has_permission_sales_invoice(doc, ptype, user=None):
    if not user:
        user = frappe.session.user

    roles = user_roles(user)

    if user == "Administrator":
        return True

    if "Central Branch Manager" in roles:
        return ptype == "read"
    
    if "Branch Manager" in roles or "Branch User" in roles:
        return True

    if "Customer" in roles or "Portal User" in roles:
        # Check if any row in Customer List matches a customer linked to this user
        linked_customers = frappe.db.sql_list("""
            SELECT parent
            FROM `tabPortal User`
            WHERE user = %s
        """, (user,))

        if not linked_customers:
            return False

        # Check if this invoice has at least one customer in linked_customers
        invoice_customers = frappe.db.sql_list("""
            SELECT customer
            FROM `tabCustomer List`
            WHERE parent = %s
        """, doc.name)

        return any(cust in linked_customers for cust in invoice_customers)

    return False


# -------------------------------------------------------------------
# 🔹 Shift related permissions
# -------------------------------------------------------------------


# Employee-based shift doctypes
def get_permission_query_conditions_shift_assignment(user):
    return get_permission_query_conditions_employee_field("Shift Assignment", user)


def has_permission_shift_assignment(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_shift_request(user):
    return get_permission_query_conditions_employee_field("Shift Request", user)


def has_permission_shift_request(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


def get_permission_query_conditions_shift_schedule(user):
    return get_permission_query_conditions_employee_field("Shift Schedule", user)


def has_permission_shift_schedule(doc, ptype, user):
    return has_permission_employee_field(doc, ptype, user)


# Master/Tool doctypes (no employee link) — allow managers full access, branch users read-only
def get_permission_query_conditions_shift_type(user):
    # No row-level restriction; enforce via has_permission
    return ""


def has_permission_shift_type(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    if "Central Branch Manager" in roles or "Branch Manager" in roles:
        return True

    if "Branch User" in roles:
        return ptype == "read"

    return False


def get_permission_query_conditions_shift_location(user):
    # No row-level restriction; enforce via has_permission
    return ""


def has_permission_shift_location(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    if "Central Branch Manager" in roles or "Branch Manager" in roles:
        return True

    if "Branch User" in roles:
        return ptype == "read"

    return False


def get_permission_query_conditions_shift_assignment_tool(user):
    # No row-level restriction; enforce via has_permission
    return ""


def has_permission_shift_assignment_tool(doc, ptype, user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = user_roles(user)

    if "Central Branch Manager" in roles or "Branch Manager" in roles:
        return True

    if "Branch User" in roles:
        return ptype == "read"

    return False


# -------------------------------------------------------------------
# 🔹 BRANCH permissions
# -------------------------------------------------------------------
def get_permission_query_conditions_branch(user):
    """Return query conditions for Branch doctype based on user role."""
    if not user:
        user = frappe.session.user
        
    if user == "Administrator" or user == "Guest":
        return ""

    roles = user_roles(user)

    # Central Branch Manager: access all branches
    if "Central Branch Manager" in roles:
        return ""

    # Branch Manager and Branch User: only their own branch
    if "Branch Manager" in roles or "Branch User" in roles:
        branch = get_user_branch(user)
        if branch:
            return f"`tabBranch`.name = '{branch}'"
        return "1=0"

    return "1=0"


def has_permission_branch(doc, ptype, user):
    """Check if user has permission for Branch doctype based on role."""
    if not user:
        user = frappe.session.user
        
    if user == "Administrator" or user == "Guest":
        return True

    roles = user_roles(user)

    # Central Branch Manager: full access to all branches
    if "Central Branch Manager" in roles:
        return True

    # Branch Manager: read-only access to their own branch
    if "Branch Manager" in roles:
        branch = get_user_branch(user)
        if branch and doc.name == branch:
            return ptype == "read"
        return False

    # Branch User: read-only access to their own branch
    if "Branch User" in roles:
        branch = get_user_branch(user)
        if branch and doc.name == branch:
            return ptype == "read"
        return False

    return False
