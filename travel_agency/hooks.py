app_name = "travel_agency"
app_title = "Travel Agency"
app_publisher = "ERPLagbe"
app_description = "Travel Agency"
app_email = "contact@erplagbe.top"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "travel_agency",
# 		"logo": "/assets/travel_agency/logo.png",
# 		"title": "Travel Agency",
# 		"route": "/travel_agency",
# 		"has_permission": "travel_agency.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/travel_agency/css/travel_agency.css"
app_include_js = [
    "/assets/travel_agency/js/employee.js",
    "/assets/travel_agency/js/branch.js",
    "/assets/travel_agency/js/sales_invoice.js",
    "/assets/travel_agency/js/holiday_list.js",
    "/assets/travel_agency/js/leave_allocation.js",
    "/assets/travel_agency/js/loan_application.js",
    "/assets/travel_agency/js/customer.js",
    "/assets/travel_agency/js/expense_claim.js",
    "/assets/travel_agency/js/loan.js",
    "/assets/travel_agency/js/loan_request.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/travel_agency/css/travel_agency.css"
# web_include_js = "/assets/travel_agency/js/travel_agency.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "travel_agency/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "travel_agency/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "travel_agency.utils.jinja_methods",
# 	"filters": "travel_agency.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "travel_agency.install.before_install"
# after_install = "travel_agency.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "travel_agency.uninstall.before_uninstall"
# after_uninstall = "travel_agency.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "travel_agency.utils.before_app_install"
# after_app_install = "travel_agency.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "travel_agency.utils.before_app_uninstall"
# after_app_uninstall = "travel_agency.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "travel_agency.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Branch": "travel_agency.permissions.get_permission_query_conditions_branch",
    "Employee": "travel_agency.permissions.get_permission_query_conditions_employee",
    "Loan Request": "travel_agency.permissions.get_permission_query_conditions_loan_request",
    "Loan": "travel_agency.permissions.get_permission_query_conditions_loan",
    "Loan Application": "travel_agency.permissions.get_permission_query_conditions_loan_application",
    "Loan Disbursement": "travel_agency.permissions.get_permission_query_conditions_loan_disbursement",
    "Loan Repayment": "travel_agency.permissions.get_permission_query_conditions_loan_repayment",
    "Leave Application": "travel_agency.permissions.get_permission_query_conditions_leave_application",
    "Leave Allocation": "travel_agency.permissions.get_permission_query_conditions_leave_allocation",
    "Attendance": "travel_agency.permissions.get_permission_query_conditions_attendance",
    "Employee Checkin": "travel_agency.permissions.get_permission_query_conditions_employee_checkin",
    "Expense Claim": "travel_agency.permissions.get_permission_query_conditions_expense_claim",
    "Salary Slip": "travel_agency.permissions.get_permission_query_conditions_salary_slip",
    "Sales Person": "travel_agency.permissions.get_permission_query_conditions_sales_person",
    "Sales Invoice": "travel_agency.permissions.get_permission_query_conditions_sales_invoice",
    "Shift Assignment": "travel_agency.permissions.get_permission_query_conditions_shift_assignment",
    "Shift Request": "travel_agency.permissions.get_permission_query_conditions_shift_request",
    "Shift Schedule": "travel_agency.permissions.get_permission_query_conditions_shift_schedule",
    "Shift Type": "travel_agency.permissions.get_permission_query_conditions_shift_type",
    "Shift Location": "travel_agency.permissions.get_permission_query_conditions_shift_location",
}

has_permission = {
    "Branch": "travel_agency.permissions.has_permission_branch",
    "Employee": "travel_agency.permissions.has_permission_employee",
    "Loan Request": "travel_agency.permissions.has_permission_loan_request",
    "Loan": "travel_agency.permissions.has_permission_loan",
    "Loan Application": "travel_agency.permissions.has_permission_loan_application",
    "Loan Disbursement": "travel_agency.permissions.has_permission_loan_disbursement",
    "Loan Repayment": "travel_agency.permissions.has_permission_loan_repayment",
    "Leave Application": "travel_agency.permissions.has_permission_leave_application",
    "Leave Allocation": "travel_agency.permissions.has_permission_leave_allocation",
    "Attendance": "travel_agency.permissions.has_permission_attendance",
    "Employee Checkin": "travel_agency.permissions.has_permission_employee_checkin",
    "Expense Claim": "travel_agency.permissions.has_permission_expense_claim",
    "Salary Slip": "travel_agency.permissions.has_permission_salary_slip",
    "Sales Person": "travel_agency.permissions.has_permission_sales_person",
    "Sales Invoice": "travel_agency.permissions.has_permission_sales_invoice",
    "Shift Assignment": "travel_agency.permissions.has_permission_shift_assignment",
    "Shift Request": "travel_agency.permissions.has_permission_shift_request",
    "Shift Schedule": "travel_agency.permissions.has_permission_shift_schedule",
    "Shift Type": "travel_agency.permissions.has_permission_shift_type",
    "Shift Location": "travel_agency.permissions.has_permission_shift_location",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Loan Application": {
        "before_submit": "travel_agency.overrides.loan_application_before_submit",
        "on_submit": "travel_agency.overrides.loan_application_on_submit",
    },
    "Employee": {
        "after_insert": "travel_agency.overrides.employee_after_insert",
    },
    "Sales Invoice": {
        "after_insert": "travel_agency.overrides.sales_invoice_after_insert"
    },
}

fixtures = [
    {"dt": "Property Setter", "filters": [["doc_type", "in", ["Loan"]]]},
    {"dt": "Custom DocPerm"},  # include all Custom DocPerm
    {"dt": "Role Profile"},  # include all Role Profiles
    {"dt": "Role"},  # include all Roles
    {"dt": "Sidebar Pages"},
]


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"travel_agency.tasks.all"
# 	],
# 	"daily": [
# 		"travel_agency.tasks.daily"
# 	],
# 	"hourly": [
# 		"travel_agency.tasks.hourly"
# 	],
# 	"weekly": [
# 		"travel_agency.tasks.weekly"
# 	],
# 	"monthly": [
# 		"travel_agency.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "travel_agency.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "travel_agency.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "travel_agency.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["travel_agency.utils.before_request"]
# after_request = ["travel_agency.utils.after_request"]

# Job Events
# ----------
# before_job = ["travel_agency.utils.before_job"]
# after_job = ["travel_agency.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"travel_agency.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
