const MERGE_PDFS_LABEL = __("Merge PDFs");

function refresh_pdf_files_grid_row(grid, doc) {
	const grid_row = grid.grid_rows?.find(
		(row) => row.doc === doc || row.doc?.name === doc?.name
	);

	if (grid_row) {
		grid_row.refresh();
	} else {
		grid.refresh();
	}
}

function set_row_file_name_from_file(doc, dialog) {
	const grid = dialog.fields_dict.pdf_files.grid;
	const file_id = doc.file;

	if (!file_id) {
		doc.file_name = "";
		refresh_pdf_files_grid_row(grid, doc);
		return;
	}

	frappe.db.get_value("File", file_id, "file_name", (data) => {
		doc.file_name = data?.file_name || "";
		refresh_pdf_files_grid_row(grid, doc);
	});
}

function register_pdf_merger_forms() {
	(frappe.boot.pdf_merger_enabled_doctypes || []).forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			refresh(frm) {
				if (frm.is_new()) {
					return;
				}

				if (frm.custom_buttons[MERGE_PDFS_LABEL]) {
					return;
				}

				frm.add_custom_button(MERGE_PDFS_LABEL, () => show_pdf_merge_dialog(frm));
			},
		});
	});
}

function show_pdf_merge_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: MERGE_PDFS_LABEL,
		size: "large",
		fields: [
			{
				label: __("PDF Name"),
				fieldname: "pdf_name",
				fieldtype: "Data",
				reqd: 1,
				default: frm.docname,
			},
			{
				label: __("PDFs"),
				fieldname: "pdf_files",
				fieldtype: "Table",
				cannot_add_rows: false,
				in_place_edit: true,
				fields: [
					{
						fieldtype: "Link",
						fieldname: "file",
						options: "File",
						label: __("File"),
						reqd: 1,
						columns: 3,
						in_list_view: 1,
						get_query() {
							return {
								filters: {
									file_type: "PDF",
								},
							};
						},
						onchange() {
							set_row_file_name_from_file(this.doc, dialog);
						},
					},
					{
						fieldtype: "Data",
						fieldname: "file_name",
						label: __("File Name"),
						read_only: 1,
						columns: 7,
						in_list_view: 1,
					},
				],
			},
		],
		primary_action_label: __("Merge"),
		primary_action() {
			const values = dialog.get_values();
			const rows = values.pdf_files || [];
			const files = rows.map((row) => row.file).filter(Boolean);

			if (!files.length) {
				frappe.msgprint(__("Select at least one PDF to merge."));
				return;
			}

			frappe.call({
				method: "pdf_merger.api.merge.merge_pdfs",
				args: {
					doctype: frm.doctype,
					docname: frm.docname,
					pdf_name: values.pdf_name,
					files: JSON.stringify(files),
				},
				freeze: true,
				freeze_message: __("Merging PDFs..."),
				btn: dialog.get_primary_btn(),
				callback() {
					dialog.hide();
					frm.refresh();
				},
			});
		},
	});

	frappe.call({
		method: "pdf_merger.api.merge.get_default_pdf_files",
		args: {
			doctype: frm.doctype,
			docname: frm.docname,
		},
		callback(r) {
			dialog.fields_dict.pdf_files.df.data = r.message || [];
			dialog.fields_dict.pdf_files.grid.refresh();
		},
	});

	dialog.show();
}

register_pdf_merger_forms();
