frappe.ui.form.on("Customer", {
	custom_date_of_birth: function (frm) {
		if (frm.doc.custom_date_of_birth) {
			const dob = new Date(frm.doc.custom_date_of_birth);
			const today = new Date();
			let age = today.getFullYear() - dob.getFullYear();
			const m = today.getMonth() - dob.getMonth();
			if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
				age--;
			}

			let category = "";
			if (age >= 12) {
				category = "Adult 12+";
			} else if (age >= 2) {
				category = "Child 2-11";
			} else {
				category = "Infant 0-1";
			}

			frm.set_value("custom_category", category);
		} else {
			frm.set_value("custom_category", "");
		}
	},
});
