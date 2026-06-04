import io
import json

import frappe
from frappe import _
from frappe.utils import cstr
from pypdf import PdfWriter


@frappe.whitelist()
def get_default_pdf_files(doctype: str, docname: str) -> list[dict[str, str]]:
	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("read")
	return _get_attached_pdf_rows(doctype, docname)


@frappe.whitelist()
def merge_pdfs(doctype: str, docname: str, files: str | list[str]) -> None:
	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("read")

	file_names = _parse_file_names(files)
	if not file_names:
		frappe.throw(_("Select at least one PDF to merge."))

	merged_pdf = _merge_file_contents(file_names)

	frappe.local.response.filename = f"{frappe.scrub(doctype)}-{frappe.scrub(docname)}-merged.pdf"
	frappe.local.response.filecontent = merged_pdf
	frappe.local.response.type = "download"


def _get_attached_pdf_rows(doctype: str, docname: str) -> list[dict[str, str]]:
	files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": doctype,
			"attached_to_name": cstr(docname),
			"file_type": "PDF",
		},
		fields=["name", "file_name"],
		order_by="creation asc",
	)
	return [{"file": row.name, "file_name": row.file_name} for row in files]


def _parse_file_names(files: str | list[str]) -> list[str]:
	if isinstance(files, str):
		files = json.loads(files)
	return [name for name in files if name]


def _merge_file_contents(file_names: list[str]) -> bytes:
	merger = PdfWriter()

	for file_name in file_names:
		file_doc = frappe.get_doc("File", file_name)
		file_doc.check_permission("read")

		if file_doc.file_type != "PDF":
			frappe.throw(
				_("File {0} is not a PDF.").format(file_doc.file_name or file_name),
				frappe.ValidationError,
			)

		content = file_doc.get_content()
		if isinstance(content, str):
			content = content.encode("latin-1")

		merger.append(io.BytesIO(content))

	out = io.BytesIO()
	merger.write(out)
	merger.close()
	return out.getvalue()
