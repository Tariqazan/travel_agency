frappe.pages['customer-portal'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Customer Portal',
		single_column: true
	});

	$(frappe.render_template(`
		<div class="customer-portal-wrapper p-4">
			<div class="summary-cards row g-3 mb-4"></div>
			<div class="customer-invoices card shadow-sm p-3"></div>
		</div>
	`)).appendTo(page.body);

	const $container = $(wrapper).find('.customer-invoices');
	const $summary = $(wrapper).find('.summary-cards');

	function render_summary(totals) {
		const summary_html = `
			<div class="col-md-4">
				<div class="card border-0 shadow-sm rounded-lg text-center p-3 bg-light">
					<h6 class="text-muted mb-1">Total Amount</h6>
					<h4 class="fw-bold text-primary">${format_currency(totals.total_amount)}</h4>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card border-0 shadow-sm rounded-lg text-center p-3 bg-light">
					<h6 class="text-muted mb-1">Paid Amount</h6>
					<h4 class="fw-bold text-success">${format_currency(totals.paid_amount)}</h4>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card border-0 shadow-sm rounded-lg text-center p-3 bg-light">
					<h6 class="text-muted mb-1">Due Amount</h6>
					<h4 class="fw-bold text-danger">${format_currency(totals.due_amount)}</h4>
				</div>
			</div>
		`;
		$summary.html(summary_html);
	}

	function render_table(rows, is_admin) {
		if (!rows || !rows.length) {
			$container.html('<div class="text-muted text-center py-4">No Sales Invoices found.</div>');
			$summary.empty();
			return;
		}

		// Calculate totals
		const totals = rows.reduce((acc, r) => {
			acc.total_amount += r.total_amount || 0;
			acc.paid_amount += r.paid_amount || 0;
			acc.due_amount += r.due_amount || 0;
			return acc;
		}, { total_amount: 0, paid_amount: 0, due_amount: 0 });

		render_summary(totals);

		const html = `
			<div class="table-responsive">
				<table class="table table-hover align-middle">
					<thead class="table-light">
						<tr>
							${is_admin ? '<th>Customer</th>' : ''}
							<th>Invoice</th>
							<th>Date</th>
							<th>Status</th>
							<th>Process Status</th>
							<th class="text-end">Total</th>
							<th class="text-end">Paid</th>
							<th class="text-end">Due</th>
						</tr>
					</thead>
					<tbody>
						${rows.map(r => `
							<tr>
								${is_admin ? `<td>${frappe.utils.escape_html(r.customer || '')}</td>` : ''}
								<td>
									<a href="/app/sales-invoice/${r.name}" target="_blank" class="fw-semibold text-primary">
										${frappe.utils.escape_html(r.name)}
									</a>
								</td>
								<td>${frappe.datetime.str_to_user(r.posting_date)}</td>
								<td>${status_badge(r.status)}</td>
								<td>${frappe.utils.escape_html(r.custom_process_status || '')}</td>
								<td class="text-end">${format_currency(r.total_amount)}</td>
								<td class="text-end text-success">${format_currency(r.paid_amount)}</td>
								<td class="text-end text-danger">${format_currency(r.due_amount)}</td>
							</tr>
						`).join('')}
					</tbody>
				</table>
			</div>
		`;
		$container.html(html);
	}

	function format_currency(value) {
		return frappe.format(value || 0, { fieldtype: 'Currency' });
	}

	function get_status_color(status) {
		status = (status || '').toLowerCase();
		if (status === 'paid') return 'green';
		if (status === 'unpaid') return 'orange';
		if (status === 'overdue') return 'red';
		if (status === 'cancelled' || status === 'canceled') return 'red';
		if (status === 'partly paid' || status === 'partially paid') return 'orange';
		if (status === 'draft') return 'gray';
		return 'blue';
	}

	function status_badge(status) {
		const color = get_status_color(status);
		const label = frappe.utils.escape_html(status || '');
		return `<span class="badge bg-${color === 'gray' ? 'secondary' : color} text-capitalize">${label}</span>`;
	}

	function load_invoices() {
		$container.html('<div class="text-muted text-center py-4">Loading...</div>');
		$summary.empty();
		frappe.xcall('travel_agency.travel_agency.page.customer_portal.customer_portal.get_customer_sales_invoices', {
			start: 0,
			limit: 100
		}).then(res => {
			render_table(res && res.invoices ? res.invoices : [], res && res.is_admin);
		}).catch(() => {
			$container.html('<div class="text-danger text-center py-4">Failed to load invoices.</div>');
		});
	}

	load_invoices();
};
