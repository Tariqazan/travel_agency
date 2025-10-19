frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		frm.set_df_property("customer", "read_only", 1);
		frm.refresh_field("customer");
		// Set current employee as sales person if not set
		if (!frm.doc.sales_team || frm.doc.sales_team.length === 0) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					filters: { user_id: frappe.session.user },
					fieldname: ["name", "employee_name"],
				},
				callback: function (r) {
					if (r.message && r.message.name) {
						// Check if this employee is a sales person
						frappe.call({
							method: "frappe.client.get_value",
							args: {
								doctype: "Sales Person",
								filters: { employee: r.message.name },
								fieldname: ["name", "commission_rate"],
							},
							callback: function (sales_r) {
								if (sales_r.message && sales_r.message.name) {
									let sales_team_row = frm.add_child("sales_team");
									sales_team_row.sales_person = sales_r.message.name;
									sales_team_row.allocated_percentage = 100;
									sales_team_row.commission_rate =
										sales_r.message.commission_rate || 0;
									frm.refresh_field("sales_team");
									calculate_sales_team_contributions(frm);
								}
							},
						});
					}
				},
			});
		}

		// Set branch if not set
		if (!frm.doc.custom_branch) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					filters: { user_id: frappe.session.user },
					fieldname: ["branch"],
				},
				callback: function (r) {
					if (r.message && r.message.branch) {
						frm.set_value("custom_branch", r.message.branch);
					}
				},
			});
		}

		// Make sales team contribution fields readonly
		if (frm.doc.sales_team && frm.doc.sales_team.length > 0) {
			frm.doc.sales_team.forEach(function (row) {
				frm.set_df_property("allocated_percentage", "read_only", 1, row.doctype, row.name);
				frm.set_df_property("allocated_amount", "read_only", 1, row.doctype, row.name);
				frm.set_df_property("incentives", "read_only", 1, row.doctype, row.name);
			});
		}
	},

	before_save: function (frm) {
		calculate_sales_commission(frm);
		calculate_sales_team_contributions(frm);
	},

	onload: function (frm) {
		// Recalculate commission for existing items when form loads
		if (frm.doc.items && frm.doc.items.length > 0) {
			frm.doc.items.forEach(function (item) {
				if (item.item_code) {
					calculate_item_commission(frm, "Sales Invoice Item", item.name);
				}
			});
		}

		// Make commission field readonly in items table
		frm.set_df_property("custom_sales_commission", "read_only", 1, "Sales Invoice Item");
	},

	items_add: function (frm, cdt, cdn) {
		calculate_item_commission(frm, cdt, cdn);
	},

	items_remove: function (frm, cdt, cdn) {
		calculate_sales_commission(frm);
		calculate_sales_team_contributions(frm);
	},
});

frappe.ui.form.on("Sales Invoice Item", {
	qty: function (frm, cdt, cdn) {
		calculate_item_commission(frm, cdt, cdn);
	},

	custom_sales_commission: function (frm, cdt, cdn) {
		calculate_item_commission(frm, cdt, cdn);
	},

	item_code: function (frm, cdt, cdn) {
		calculate_item_commission(frm, cdt, cdn);
	},
});

function calculate_item_commission(frm, cdt, cdn) {
	let row = locals[cdt][cdn];

	// Get the base commission from item master
	if (row.item_code) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Item",
				filters: { name: row.item_code },
				fieldname: ["custom_sales_commission"],
			},
			callback: function (r) {
				try {
					if (r.message) {
						let base_commission = flt(r.message.custom_sales_commission || 0);
						let quantity = flt(row.qty) || 1;
						let total_commission = base_commission * quantity;

						frappe.model.set_value(
							cdt,
							cdn,
							"custom_sales_commission",
							total_commission
						);

						calculate_sales_commission(frm);
						calculate_sales_team_contributions(frm);
					}
				} catch (error) {
					console.error("Error calculating commission:", error);
				}
			},
		});
	} else {
		frappe.model.set_value(cdt, cdn, "custom_sales_commission", 0);
		calculate_sales_commission(frm);
		calculate_sales_team_contributions(frm);
	}
}

function calculate_sales_commission(frm) {
	let total_commission = 0;
	(frm.doc.items || []).forEach(function (item) {
		total_commission += flt(item.custom_sales_commission || 0);
	});
	frm.set_value("custom_total_sales_commission", total_commission);
}

function calculate_sales_team_contributions(frm) {
	try {
		if (!frm.doc.sales_team || frm.doc.sales_team.length === 0) return;

		let total_commission = flt(frm.doc.custom_total_sales_commission || 0);
		let total_percentage = 0;

		// Sum allocated percentages
		frm.doc.sales_team.forEach((row) => {
			total_percentage += flt(row.allocated_percentage || 0);
		});

		// Normalize percentages to 100%
		if (total_percentage !== 100 && total_percentage > 0) {
			frm.doc.sales_team.forEach((row) => {
				let adjusted_percentage =
					(flt(row.allocated_percentage || 0) / total_percentage) * 100;
				frappe.model.set_value(
					row.doctype,
					row.name,
					"allocated_percentage",
					adjusted_percentage
				);
			});
		}

		// Calculate incentives (same as allocated_amount)
		frm.doc.sales_team.forEach((row) => {
			let percentage = flt(row.allocated_percentage || 0);
			let allocated_amount = (total_commission * percentage) / 100;

			frappe.model.set_value(row.doctype, row.name, "allocated_amount", allocated_amount);
			frappe.model.set_value(row.doctype, row.name, "incentives", allocated_amount);
		});

		frm.refresh_field("sales_team");
	} catch (error) {
		console.error("Error calculating sales team contributions:", error);
	}
}

frappe.ui.form.on("Sales Team", {
	sales_person: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.sales_person) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Sales Person",
					filters: { name: row.sales_person },
					fieldname: ["commission_rate"],
				},
				callback: function (r) {
					if (r.message && r.message.commission_rate) {
						frappe.model.set_value(
							cdt,
							cdn,
							"commission_rate",
							r.message.commission_rate
						);
						calculate_sales_team_contributions(frm);
					}
				},
			});
		}
	},

	allocated_percentage: function (frm, cdt, cdn) {
		calculate_sales_team_contributions(frm);
	},

	sales_team_add: function (frm, cdt, cdn) {
		calculate_sales_team_contributions(frm);
	},

	sales_team_remove: function (frm, cdt, cdn) {
		calculate_sales_team_contributions(frm);
	},
});

frappe.ui.form.on("Customer List", {
	is_primary: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.is_primary) {
			(frm.doc.custom_customers || []).forEach(function (other) {
				if (other.name !== row.name && other.is_primary) {
					frappe.model.set_value(
						other.doctype || "Customer List",
						other.name,
						"is_primary",
						0
					);
				}
			});
			// set parent customer from this primary row
			frm.set_value("customer", row.customer);
		}
	},
});
