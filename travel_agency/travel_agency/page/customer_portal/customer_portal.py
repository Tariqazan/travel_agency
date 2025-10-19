import frappe

@frappe.whitelist()
def get_customer_sales_invoices(start: int = 0, limit: int = 100):
    """
    Safe API for portal users to fetch their Sales Invoices.
    Runs with system privileges, but only returns invoices linked to user's customers.
    """
    user = frappe.session.user
    print("User:", user)
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "System Manager" in roles

    customer = None
    filters = {"docstatus": ["<", 2]}  # include Draft + Submitted, exclude Cancelled

    if not is_admin:
        # Find all customers linked to this portal user
        customer_names = frappe.db.sql_list("""
            SELECT parent
            FROM `tabPortal User`
            WHERE user = %s
        """, (user,))

        if not customer_names:
            return {"customer": None, "invoices": [], "is_admin": False}
        print("Customer Names:", customer_names)
        # For simplicity, pick first customer
        customer = customer_names[0]

        # Build full list of customers accessible to this user
        customers_to_show = set([customer])

        # Customers listed under this customer's custom_customers child table
        # child_customers = frappe.db.get_all(
        #     "tabCustomer List",
        #     filters={"parent": customer},
        #     fields=["customer"]
        # )
        # print("Child Customers:", child_customers)
        # for c in child_customers:
        #     customers_to_show.add(c.customer)

        # Parent customers where this customer is listed as a child
        parent_customers = frappe.db.sql_list("""
            SELECT parent FROM `tabCustomer List`
            WHERE customer = %s
        """, (customer,))
        for p in parent_customers:
            customers_to_show.add(p)

        filters["customer"] = ["in", list(customers_to_show)]

    # Fetch invoices **as Administrator** to bypass portal restrictions
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=[
            "name", "customer", "posting_date", "status", 
            "grand_total", "rounded_total", "outstanding_amount",
            "custom_process_status", "due_date", "docstatus"
        ],
        order_by="posting_date desc, creation desc",
        start=start,
        page_length=limit,
        as_list=False,
        ignore_permissions=True  # bypass ERPNext permissions
    )

    # Compute paid/due amounts
    for inv in invoices:
        total = inv.get("rounded_total") or inv.get("grand_total") or 0
        outstanding = inv.get("outstanding_amount") or 0
        inv["total_amount"] = total
        inv["paid_amount"] = max(total - outstanding, 0)
        inv["due_amount"] = outstanding

    return {"customer": customer, "invoices": invoices, "is_admin": is_admin}
