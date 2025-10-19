frappe.ui.form.on("Expense Claim", {
	refresh: function (frm) {
		if (!frm.doc.employee) {
			frm.trigger("set_employee_from_user");
		}

		// Set default mode of payment to "Cash"
		if (!frm.doc.mode_of_payment) {
			frm.set_value("mode_of_payment", "Cash");
		}

		// Set payable account from company's default_expense_claim_payable_account
		if (frm.doc.company && !frm.doc.payable_account) {
			frappe.db
				.get_value("Company", frm.doc.company, "default_expense_claim_payable_account")
				.then((company_record) => {
					const payable_account =
						company_record?.message?.default_expense_claim_payable_account;
					if (payable_account) {
						frm.set_value("payable_account", payable_account);
					}
				});
		}
	},
	set_employee_from_user: function (frm) {
		// Get employee from current user
		const current_user = frappe.session.user;

		frappe.db
			.get_value("Employee", { user_id: current_user }, ["name", "expense_approver"])
			.then((employee_record) => {
				const session_employee = employee_record?.message?.name;
				const expense_approver = employee_record?.message?.expense_approver;

				if (session_employee) {
					frm.set_value("employee", session_employee);

					// Set expense approver if available
					if (expense_approver) {
						frm.set_value("expense_approver", expense_approver);
					}
				}
			})
			.catch((error) => {
				console.error("Error getting employee:", error);
			});
	},

	employee: function (frm) {
		// When employee changes, update expense approver
		if (frm.doc.employee) {
			frappe.db
				.get_value("Employee", frm.doc.employee, "expense_approver")
				.then((employee_record) => {
					const expense_approver = employee_record?.message?.expense_approver;
					if (expense_approver) {
						frm.set_value("expense_approver", expense_approver);
					}
				})
				.catch((error) => {
					console.error("Error getting expense approver:", error);
				});
		}
	},

	company: function (frm) {
		// When company changes, update payable account
		if (frm.doc.company) {
			frappe.db
				.get_value("Company", frm.doc.company, "default_expense_claim_payable_account")
				.then((company_record) => {
					const payable_account =
						company_record?.message?.default_expense_claim_payable_account;
					if (payable_account) {
						frm.set_value("payable_account", payable_account);
					}
				});
		}
	},
});
