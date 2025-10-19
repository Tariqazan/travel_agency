frappe.ui.form.on("Loan Request", {
    refresh: function (frm) {
        console.log("Loan Request form refreshed");
        if (!frm.doc.applicant) {
            frm.trigger("set_employee_from_user");
        }
    },
    set_employee_from_user: function (frm) {
        const current_user = frappe.session.user;

        frappe.db
            .get_value("Employee", { user_id: current_user }, ["name"])
            .then((employee_record) => {
                const session_employee = employee_record?.message?.name;

                if (session_employee) {
                    console.log("Setting applicant to:", session_employee);
                    frm.set_value("applicant", session_employee);
                }
            })
            .catch((error) => {
                console.error("Error getting employee:", error);
            });
    },
})