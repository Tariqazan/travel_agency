import frappe


def get_next_serial_number():
    """
    Get the next serial number for INV naming series
    Returns the next available serial number starting from 0001
    """
    # Get the highest existing serial number
    existing_invoices = frappe.db.sql(
        """
        SELECT name FROM `tabSales Invoice` 
        WHERE name LIKE 'INV-%-%' 
        ORDER BY name DESC 
        LIMIT 1
    """,
        as_dict=True,
    )

    if existing_invoices:
        # Extract serial number from the last invoice name
        last_name = existing_invoices[0].name
        try:
            # Extract number between INV- and -S/-M
            serial_part = last_name.split("-")[1]
            next_serial = int(serial_part) + 1
        except (IndexError, ValueError):
            next_serial = 1
    else:
        next_serial = 1

    return next_serial


def loan_application_before_submit(doc, method):
    # Only allow submit if status is "Approved" or "Rejected"
    if doc.status not in ["Approved", "Rejected"]:
        from frappe import throw, _

        throw(
            _("You can only submit a Loan Application if it is Approved or Rejected.")
        )


def loan_application_on_submit(doc, method):
    if doc.status == "Approved":
        from frappe import new_doc, msgprint

        loan = new_doc("Loan")
        loan.applicant = getattr(doc, "applicant", None)
        loan.loan_application = doc.name
        loan.loan_type = getattr(doc, "loan_type", None) or getattr(doc, "type", None)
        loan.posting_date = getattr(doc, "posting_date", None)
        loan.company = getattr(doc, "company", None)
        loan.loan_amount = getattr(doc, "loan_amount", None)
        loan.status = "Sanctioned"
        # Set loan_product from Loan Application or set a default
        loan.loan_product = getattr(doc, "loan_product", None)
        if not loan.loan_product:
            # Set a default or raise an error if required
            msgprint(
                "Please select Loan Product in the Loan Application.", indicator="red"
            )
            return

        loan.insert(ignore_permissions=True)
        # loan.submit()

        msgprint(
            f'Loan created: <a href="/app/loan/{loan.name}" target="_blank">{loan.name}</a>',
            indicator="green",
        )


def employee_after_insert(doc, method):
    """
    Automatically create a Sales Person when an Employee is inserted
    """
    try:
        from frappe import new_doc, msgprint

        # Check if a Sales Person already exists for this employee
        existing_sales_person = frappe.db.exists("Sales Person", {"employee": doc.name})

        if existing_sales_person:
            return  # Sales Person already exists, no need to create

        # Create new Sales Person
        sales_person = new_doc("Sales Person")
        sales_person.sales_person_name = doc.employee_name or doc.name
        sales_person.employee = doc.name
        sales_person.department = doc.department
        sales_person.is_group = 0  # Individual sales person, not a group
        sales_person.enabled = 1

        # Insert the Sales Person
        sales_person.insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(
            f"Error creating Sales Person for Employee {doc.name}: {str(e)}"
        )
        # Don't raise the error to avoid breaking the employee creation process


def sales_invoice_after_insert(doc, method):
    """
    Custom naming series for Sales Invoice based on custom_customers field
    - If Service quantity 1: Add 'S' with SL (Serial)
    - If Service quantity > 1: Add 'M' with Sales Order Number
    - Serial will generate in ascending order
    """
    try:
        # Check if custom_customers field exists and has data
        if not hasattr(doc, "custom_customers") or not doc.custom_customers:
            return

        # Get the count of customers
        customer_count = len(doc.custom_customers)

        # Generate next serial number
        serial_number = get_next_serial_number()

        if customer_count == 1:
            # Single customer: Add 'S' to serial name
            new_name = f"INV-{serial_number:04d}-S"
        elif customer_count > 1:
            # Multiple customers: Add 'M' to sales invoice name
            new_name = f"INV-{serial_number:04d}-M"
        else:
            # No customers, no change needed
            return

        # Rename the document
        frappe.rename_doc("Sales Invoice", doc.name, new_name, force=True)

        # Show dialog with link to new sales invoice instead of redirecting
        frappe.msgprint(
            f'<a href="/app/sales-invoice/{new_name}" class="btn btn-primary">'
            f"Open New Sales Invoice</a>",
            indicator="green",
            title="Sales Invoice Created Successfully",
        )

    except Exception as e:
        frappe.log_error(f"Error in sales_invoice_after_insert: {str(e)}")
        frappe.msgprint(f"Error updating Sales Invoice name: {str(e)}", indicator="red")
