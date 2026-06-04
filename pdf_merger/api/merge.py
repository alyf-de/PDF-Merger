import io
import json
import os

import frappe
from frappe import _
from frappe.utils import cstr
from pypdf import PdfWriter
from pypdf.errors import PyPdfError


@frappe.whitelist()
def get_default_pdf_files(doctype: str, docname: str) -> list[dict[str, str]]:
	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("read")
	return _get_attached_pdf_rows(doctype, docname)


@frappe.whitelist()
def merge_pdfs(
	doctype: str, docname: str, pdf_name: str, files: str | list[str]
) -> dict[str, str]:
	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("write")

	file_names = _parse_file_names(files)
	if not file_names:
		frappe.throw(_("Select at least one PDF to merge."))

	output_filename = _normalize_pdf_filename(pdf_name)
	merged_pdf = _merge_file_contents(file_names)
	return _attach_merged_pdf(doctype, docname, merged_pdf, output_filename)


def _attach_merged_pdf(
	doctype: str, docname: str, content: bytes, output_filename: str
) -> dict[str, str]:
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": output_filename,
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"is_private": 1,
			"content": content,
		}
	)
	file_doc.insert()

	return {
		"name": file_doc.name,
		"file_name": file_doc.file_name,
		"file_url": file_doc.file_url,
	}


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


def _normalize_pdf_filename(pdf_name: str) -> str:
	filename = os.path.basename(cstr(pdf_name).strip())
	if not filename:
		frappe.throw(_("PDF Name is required."), frappe.ValidationError)

	if not filename.lower().endswith(".pdf"):
		filename = f"{filename}.pdf"

	return filename


def _merge_file_contents(file_names: list[str]) -> bytes:
	merger = PdfWriter()
	current_file_label = None

	try:
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

			current_file_label = file_doc.file_name or file_name
			merger.append(io.BytesIO(content))

		current_file_label = None
		out = io.BytesIO()
		merger.write(out)
		return out.getvalue()
	except PyPdfError as e:
		if current_file_label:
			frappe.throw(
				_("Could not read PDF {0}: {1}").format(current_file_label, e),
				frappe.ValidationError,
			)
		frappe.throw(_("Could not merge PDFs: {0}").format(e), frappe.ValidationError)
	finally:
		merger.close()
