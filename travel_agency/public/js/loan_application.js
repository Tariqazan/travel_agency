frappe.ui.form.on("Loan Application", {
	refresh: function (frm) {
		frm.$wrapper.find(".form-dashboard").hide();
		if (!frm.doc.company) {
			const default_company = frappe.defaults.get_default("company");
			if (default_company) {
				frm.set_value("company", default_company);
			}
		}
		frm.set_df_property("applicant_type", "hidden", 1);
		frm.set_df_property("company", "hidden", 1);
	},
});
