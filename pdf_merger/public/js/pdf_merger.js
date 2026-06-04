const MERGE_PDFS_LABEL = __("Merge PDFs");

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
		fields: [
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
						in_list_view: 1,
						get_query() {
							return {
								filters: {
									file_type: "PDF",
								},
							};
						},
						onchange() {
							const file_id = this.doc.file;
							if (!file_id) {
								this.doc.file_name = "";
								dialog.fields_dict.pdf_files.grid.refresh();
								return;
							}

							frappe.db.get_value("File", file_id, "file_name", (r) => {
								this.doc.file_name = r.message.file_name;
								dialog.fields_dict.pdf_files.grid.refresh();
							});
						},
					},
					{
						fieldtype: "Data",
						fieldname: "file_name",
						label: __("File Name"),
						read_only: 1,
						in_list_view: 1,
					},
				],
			},
		],
		primary_action_label: __("Merge"),
		primary_action() {
			const rows = dialog.get_values().pdf_files || [];
			const files = rows.map((row) => row.file).filter(Boolean);

			if (!files.length) {
				frappe.msgprint(__("Select at least one PDF to merge."));
				return;
			}

			open_url_post(frappe.request.url, {
				cmd: "pdf_merger.api.merge.merge_pdfs",
				doctype: frm.doctype,
				docname: frm.docname,
				files: JSON.stringify(files),
			});
			dialog.hide();
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
