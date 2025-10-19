frappe.ui.form.on("Branch", {
	refresh: function (frm) {
		render_employee_list(frm);

		// Add custom button for assigning employees
		if (frm.doc.name && !frm.is_new()) {
			frm.add_custom_button(
				__("Assign Employee"),
				function () {
					show_employee_assignment_dialog(frm);
				},
				__("Actions")
			);
		}
	},
	after_save: function (frm) {
		render_employee_list(frm);
	},
});

function render_employee_list(frm) {
	const field = frm.get_field("custom_employee_list");
	if (!field) return;

	const $wrapper = field.$wrapper;
	$wrapper.empty();

	if (!frm.doc.name) {
		$wrapper.html('<div class="text-muted">Save the Branch to see employees.</div>');
		return;
	}

	$wrapper.html('<div class="text-muted">Loading employees…</div>');

	frappe.db
		.get_list("Employee", {
			fields: ["name", "employee_name", "designation", "image", "status", "employee_number"],
			filters: { branch: frm.doc.name, status: "Active" },
			order_by: "employee_name asc",
			limit: 50,
		})
		.then((employees) => {
			if (!employees || employees.length === 0) {
				$wrapper.html(
					'<div class="text-muted">No active employees found for this branch.</div>'
				);
				return;
			}

			const rows = employees
				.map((emp) => {
					const image = emp.image || "/assets/frappe/images/default-avatar.png";
					const empName = frappe.utils.escape_html(emp.employee_name || emp.name);
					const designation = frappe.utils.escape_html(emp.designation || "");
					const empNo = frappe.utils.escape_html(emp.employee_number || "");

					return `<div class="flex items-center gap-3 py-2" style="border-bottom: 1px solid var(--border-color);">
					<img src="${image}" class="avatar avatar-medium" alt="${empName}">
					<div class="flex-1">
						<div><a class="bold" href="/app/employee/${emp.name}">${empName}</a></div>
						<div class="text-muted small">${designation}</div>
					</div>
					<div class="text-muted small">${empNo}</div>
				</div>`;
				})
				.join("");

			$wrapper.html(`<div class="employee-list">${rows}</div>`);
		})
		.catch(() => {
			$wrapper.html('<div class="text-muted">Unable to load employees.</div>');
		});
}

function show_employee_assignment_dialog(frm) {
	// Get employees from other branches
	frappe.db
		.get_list("Employee", {
			fields: ["name", "employee_name", "designation", "branch", "employee_number", "image"],
			filters: [
				["branch", "!=", frm.doc.name],
				["status", "=", "Active"],
			],
			order_by: "employee_name asc",
			limit: 200,
		})
		.then((employees) => {
			if (!employees || employees.length === 0) {
				frappe.msgprint(__("No employees from other branches found."));
				return;
			}

			// Variables to store selected employees and filtered list
			let selected_employees = new Set();
			let filtered_employees = employees;

			// Create dialog
			const dialog = new frappe.ui.Dialog({
				title: __("Assign Employees to Branch"),
				fields: [
					{
						fieldname: "search_employee",
						fieldtype: "Data",
						label: __("Search Employee"),
						placeholder: __("Search by name, employee number, or designation..."),
					},
					{
						fieldname: "selected_count",
						fieldtype: "HTML",
						label: __("Selected"),
					},
					{
						fieldname: "employee_list",
						fieldtype: "HTML",
						label: __("Available Employees"),
					},
				],
				size: "extra-large",
				primary_action_label: __("Assign Selected"),
				primary_action: function () {
					if (selected_employees.size === 0) {
						frappe.msgprint(__("Please select at least one employee."));
						return;
					}
					assign_employees_to_branch(frm, Array.from(selected_employees), dialog);
				},
			});

			// Function to render employee list
			function renderEmployeeList() {
				const employee_html = filtered_employees
					.map((emp) => {
						const image = emp.image || "/assets/frappe/images/default-avatar.png";
						const empName = frappe.utils.escape_html(emp.employee_name || emp.name);
						const designation = frappe.utils.escape_html(emp.designation || "");
						const empNo = frappe.utils.escape_html(emp.employee_number || "");
						const currentBranch = frappe.utils.escape_html(emp.branch || "");
						const isSelected = selected_employees.has(emp.name);

						return `
					<div class="employee-card ${isSelected ? "selected" : ""}" data-employee="${emp.name}">
						<div class="employee-checkbox">
							<input type="checkbox" ${isSelected ? "checked" : ""} value="${emp.name}">
						</div>
						<div class="employee-avatar">
							<img src="${image}" alt="${empName}">
						</div>
						<div class="employee-details">
							<div class="employee-name">${empName}</div>
							<div class="employee-id">${empNo}</div>
							<div class="employee-designation">${designation}</div>
							<div class="employee-branch">Current: ${currentBranch}</div>
						</div>
					</div>
				`;
					})
					.join("");

				dialog.fields_dict.employee_list.$wrapper.html(`
					<div class="employee-grid">
						${employee_html}
					</div>
				`);

				// Update selected count
				dialog.fields_dict.selected_count.$wrapper.html(`
					<div class="selected-count">
						<span class="count-badge">${selected_employees.size}</span>
						<span class="count-text">employee${selected_employees.size !== 1 ? "s" : ""} selected</span>
					</div>
				`);

				// Add click handlers
				dialog.fields_dict.employee_list.$wrapper
					.find(".employee-card")
					.on("click", function (e) {
						if (e.target.type === "checkbox") return;

						const employee_id = $(this).data("employee");
						const checkbox = $(this).find('input[type="checkbox"]');

						if (selected_employees.has(employee_id)) {
							selected_employees.delete(employee_id);
							checkbox.prop("checked", false);
							$(this).removeClass("selected");
						} else {
							selected_employees.add(employee_id);
							checkbox.prop("checked", true);
							$(this).addClass("selected");
						}

						// Update selected count
						dialog.fields_dict.selected_count.$wrapper.html(`
							<div class="selected-count">
								<span class="count-badge">${selected_employees.size}</span>
								<span class="count-text">employee${selected_employees.size !== 1 ? "s" : ""} selected</span>
							</div>
						`);
					});

				// Handle checkbox clicks
				dialog.fields_dict.employee_list.$wrapper
					.find('input[type="checkbox"]')
					.on("click", function (e) {
						e.stopPropagation();
						const employee_id = $(this).val();
						const card = $(this).closest(".employee-card");

						if ($(this).is(":checked")) {
							selected_employees.add(employee_id);
							card.addClass("selected");
						} else {
							selected_employees.delete(employee_id);
							card.removeClass("selected");
						}

						// Update selected count
						dialog.fields_dict.selected_count.$wrapper.html(`
							<div class="selected-count">
								<span class="count-badge">${selected_employees.size}</span>
								<span class="count-text">employee${selected_employees.size !== 1 ? "s" : ""} selected</span>
							</div>
						`);
					});
			}

			// Search functionality
			dialog.fields_dict.search_employee.$input.on("input", function () {
				const search_term = $(this).val().toLowerCase();
				filtered_employees = employees.filter((emp) => {
					const empName = (emp.employee_name || emp.name || "").toLowerCase();
					const empNo = (emp.employee_number || "").toLowerCase();
					const designation = (emp.designation || "").toLowerCase();
					const branch = (emp.branch || "").toLowerCase();

					return (
						empName.includes(search_term) ||
						empNo.includes(search_term) ||
						designation.includes(search_term) ||
						branch.includes(search_term)
					);
				});
				renderEmployeeList();
			});

			// Add CSS for styling
			dialog.$wrapper.find(".modal-content").append(`
				<style>
					.employee-grid {
						display: grid;
						grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
						gap: 12px;
						max-height: 500px;
						overflow-y: auto;
						padding: 8px;
					}
					
					.employee-card {
						display: flex;
						align-items: center;
						padding: 12px;
						border: 2px solid #e1e5e9;
						border-radius: 8px;
						background: #fff;
						cursor: pointer;
						transition: all 0.2s ease;
						gap: 12px;
					}
					
					.employee-card:hover {
						border-color: #007bff;
						box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
						transform: translateY(-1px);
					}
					
					.employee-card.selected {
						border-color: #007bff;
						background: #f8f9ff;
						box-shadow: 0 2px 8px rgba(0, 123, 255, 0.2);
					}
					
					.employee-checkbox {
						flex-shrink: 0;
					}
					
					.employee-checkbox input[type="checkbox"] {
						width: 18px;
						height: 18px;
						cursor: pointer;
					}
					
					.employee-avatar {
						flex-shrink: 0;
					}
					
					.employee-avatar img {
						width: 40px;
						height: 40px;
						border-radius: 50%;
						object-fit: cover;
					}
					
					.employee-details {
						flex: 1;
						min-width: 0;
					}
					
					.employee-name {
						font-weight: 600;
						font-size: 14px;
						color: #2c3e50;
						margin-bottom: 2px;
					}
					
					.employee-id {
						font-size: 12px;
						color: #6c757d;
						margin-bottom: 2px;
					}
					
					.employee-designation {
						font-size: 12px;
						color: #495057;
						margin-bottom: 2px;
					}
					
					.employee-branch {
						font-size: 11px;
						color: #6c757d;
						font-style: italic;
					}
					
					.selected-count {
						display: flex;
						align-items: center;
						gap: 8px;
						padding: 8px 12px;
						background: #f8f9fa;
						border-radius: 6px;
						border: 1px solid #e9ecef;
					}
					
					.count-badge {
						background: #007bff;
						color: white;
						padding: 4px 8px;
						border-radius: 12px;
						font-size: 12px;
						font-weight: 600;
						min-width: 20px;
						text-align: center;
					}
					
					.count-text {
						font-size: 13px;
						color: #495057;
					}
					
					.employee-grid::-webkit-scrollbar {
						width: 6px;
					}
					
					.employee-grid::-webkit-scrollbar-track {
						background: #f1f1f1;
						border-radius: 3px;
					}
					
					.employee-grid::-webkit-scrollbar-thumb {
						background: #c1c1c1;
						border-radius: 3px;
					}
					
					.employee-grid::-webkit-scrollbar-thumb:hover {
						background: #a8a8a8;
					}
				</style>
			`);

			// Initial render
			renderEmployeeList();
			dialog.show();
		})
		.catch(() => {
			frappe.msgprint(__("Unable to load employees from other branches."));
		});
}

function assign_employees_to_branch(frm, employee_ids, dialog) {
	frappe.confirm(
		__("Are you sure you want to assign {0} employee{1} to {2}?", [
			employee_ids.length,
			employee_ids.length !== 1 ? "s" : "",
			frm.doc.branch,
		]),
		function () {
			let completed = 0;
			let failed = 0;
			let current_index = 0;

			// Show progress
			const progress_dialog = new frappe.ui.Dialog({
				title: __("Assigning Employees..."),
				fields: [
					{
						fieldname: "progress",
						fieldtype: "HTML",
						label: __("Progress"),
					},
				],
				primary_action_label: __("Close"),
				primary_action: function () {
					progress_dialog.hide();
				},
			});

			progress_dialog.fields_dict.progress.$wrapper.html(`
				<div class="progress-info">
					<div class="progress-text">Assigning employees...</div>
					<div class="progress-bar">
						<div class="progress-fill" style="width: 0%"></div>
					</div>
					<div class="progress-stats">
						<span class="completed">0 completed</span>
						<span class="failed">0 failed</span>
					</div>
					<div class="current-employee">
						<span class="current-text">Processing: </span>
						<span class="current-name">-</span>
					</div>
				</div>
			`);

			progress_dialog.show();

			// Add progress bar CSS
			progress_dialog.$wrapper.find(".modal-content").append(`
				<style>
					.progress-info {
						padding: 20px;
					}
					.progress-text {
						margin-bottom: 10px;
						font-weight: 500;
					}
					.progress-bar {
						width: 100%;
						height: 8px;
						background: #e9ecef;
						border-radius: 4px;
						overflow: hidden;
						margin-bottom: 10px;
					}
					.progress-fill {
						height: 100%;
						background: #007bff;
						transition: width 0.3s ease;
					}
					.progress-stats {
						display: flex;
						justify-content: space-between;
						font-size: 12px;
						color: #6c757d;
						margin-bottom: 8px;
					}
					.completed { color: #28a745; }
					.failed { color: #dc3545; }
					.current-employee {
						font-size: 11px;
						color: #6c757d;
						font-style: italic;
					}
					.current-name {
						font-weight: 500;
					}
				</style>
			`);

			// Function to process employees sequentially with better error handling
			function processNextEmployee() {
				if (current_index >= employee_ids.length) {
					// All employees processed
					progress_dialog.fields_dict.progress.$wrapper
						.find(".progress-text")
						.text("Assignment completed!");
					progress_dialog.primary_action_label = __("Close");

					if (completed > 0) {
						frappe.msgprint(
							__("{0} employee{1} successfully assigned to this branch.", [
								completed,
								completed !== 1 ? "s" : "",
							])
						);
						// Refresh the employee list
						render_employee_list(frm);
					}

					if (failed > 0) {
						frappe.msgprint(
							__("{0} employee{1} failed to assign. Please try again.", [
								failed,
								failed !== 1 ? "s" : "",
							])
						);
					}
					return;
				}

				const employee_id = employee_ids[current_index];
				
				// Update current employee being processed
				frappe.db.get_value("Employee", employee_id, "employee_name").then((result) => {
					const emp_name = result.message?.employee_name || employee_id;
					progress_dialog.fields_dict.progress.$wrapper
						.find(".current-name")
						.text(emp_name);
				});

				// Use frappe.db.set_value instead of frappe.client.set_value for better reliability
				function attemptAssignment(retry_count = 0) {
					frappe.db.set_value("Employee", employee_id, {
						branch: frm.doc.name
					}).then(() => {
						// Success
						completed++;
						updateProgress();
						current_index++;
						setTimeout(processNextEmployee, 800); // Delay between employees
					}).catch((error) => {
						// Handle errors
						if (error.message && error.message.includes("has been modified after you have opened it") && retry_count < 3) {
							// Retry with increasing delay
							const delay = 1000 * (retry_count + 1);
							setTimeout(() => {
								attemptAssignment(retry_count + 1);
							}, delay);
						} else {
							// Final failure
							failed++;
							console.error("Failed to assign employee:", employee_id, error);
							updateProgress();
							current_index++;
							setTimeout(processNextEmployee, 800);
						}
					});
				}

				function updateProgress() {
					const total = employee_ids.length;
					const progress = ((completed + failed) / total) * 100;

					progress_dialog.fields_dict.progress.$wrapper
						.find(".progress-fill")
						.css("width", progress + "%");
					progress_dialog.fields_dict.progress.$wrapper
						.find(".completed")
						.text(`${completed} completed`);
					progress_dialog.fields_dict.progress.$wrapper
						.find(".failed")
						.text(`${failed} failed`);
				}

				attemptAssignment();
			}

			// Start processing
			processNextEmployee();
			dialog.hide();
		}
	);
}
