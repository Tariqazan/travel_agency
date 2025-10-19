frappe.ui.form.on("Leave Allocation", {
	refresh: function (frm) {
		frm.$wrapper.find(".form-dashboard").hide();
	},
});
