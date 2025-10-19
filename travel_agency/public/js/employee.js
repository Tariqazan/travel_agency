frappe.ui.form.on("Employee", {
	refresh: function (frm) {
		frm.add_custom_button(__("Assign Salary Structure"), () => {
			frm.trigger("assign_salary_structure");
		});
	},

	assign_salary_structure: function (frm) {
		// Check if custom_amount is set
		if (!frm.doc.custom_amount) {
			frappe.msgprint(__("Please set the Amount field before assigning salary structure."));
			return;
		}

		// Save form if it has unsaved changes
		if (frm.doc.__unsaved) {
			frm.save().then(() => {
				frm.trigger("show_salary_structure_dialog");
			});
		} else {
			frm.trigger("show_salary_structure_dialog");
		}
	},

	show_salary_structure_dialog: function (frm) {
		// Show dialog to get salary structure details
		let d = new frappe.ui.Dialog({
			title: __("Assign Salary Structure"),
			fields: [
				{
					label: __("Salary Structure"),
					fieldname: "salary_structure",
					fieldtype: "Link",
					options: "Salary Structure",
					reqd: 1,
					get_query: function () {
						return {
							filters: {
								is_active: "Yes",
								company: frm.doc.company || frappe.defaults.get_default("Company"),
							},
						};
					},
				},
				{
					label: __("From Date"),
					fieldname: "from_date",
					fieldtype: "Date",
					reqd: 1,
					default: frm.doc.date_of_joining,
				},
				{
					label: __("Base Amount"),
					fieldname: "base",
					fieldtype: "Currency",
					reqd: 1,
					default: frm.doc.custom_amount,
					read_only: 1,
				},
				{
					label: __("Variable Amount"),
					fieldname: "variable",
					fieldtype: "Currency",
					default: 0,
				},
			],
			primary_action_label: __("Assign"),
			primary_action: function (values) {
				d.hide();

				frappe.call({
					method: "travel_agency.api.employee.create_salary_structure_assignment",
					args: {
						employee: frm.doc.name,
						salary_structure: values.salary_structure,
						from_date: values.from_date,
						base: values.base,
						variable: values.variable || 0,
						company: frm.doc.company || frappe.defaults.get_default("Company"),
					},
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(__("Salary Structure assigned successfully!"));
							frm.reload_doc();
						} else if (r.exc) {
							frappe.msgprint(__("Error: {0}").format(r.exc));
						}
					},
					error: function (r) {
						console.log("API Error:", r);
						frappe.msgprint(__("Error occurred while assigning salary structure"));
					},
				});
			},
		});

		d.show();
	},
});
