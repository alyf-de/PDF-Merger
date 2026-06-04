# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

import io

import frappe
from frappe.tests.utils import FrappeTestCase
from pypdf import PdfWriter

from pdf_merger.api.merge import get_default_pdf_files, merge_pdfs
from pdf_merger.settings import clear_enabled_doctypes_cache, get_enabled_doctypes


def _minimal_pdf_bytes() -> bytes:
	out = io.BytesIO()
	writer = PdfWriter()
	writer.add_blank_page(width=200, height=200)
	writer.write(out)
	writer.close()
	return out.getvalue()


MINIMAL_PDF = _minimal_pdf_bytes()


class TestPDFMerger(FrappeTestCase):
	def setUp(self):
		clear_enabled_doctypes_cache()
		self.todo = frappe.get_doc({"doctype": "ToDo", "description": "PDF Merger test"}).insert()
		self.pdf_file = _create_attached_file(
			self.todo.doctype,
			self.todo.name,
			"test.pdf",
			MINIMAL_PDF,
		)
		self.image_file = _create_attached_file(
			self.todo.doctype,
			self.todo.name,
			"test.png",
			b"\x89PNG\r\n\x1a\n",
		)

	def tearDown(self):
		clear_enabled_doctypes_cache()
		frappe.delete_doc("ToDo", self.todo.name, force=True)

	def test_get_enabled_doctypes_from_settings(self):
		settings = frappe.get_single("PDF Merger Settings")
		settings.doctypes = []
		settings.append("doctypes", {"document_type": "ToDo"})
		settings.save()
		clear_enabled_doctypes_cache()

		self.assertIn("ToDo", get_enabled_doctypes())

	def test_get_default_pdf_files_returns_only_pdfs(self):
		rows = get_default_pdf_files(self.todo.doctype, self.todo.name)

		file_names = {row["file"] for row in rows}
		self.assertIn(self.pdf_file.name, file_names)
		self.assertNotIn(self.image_file.name, file_names)

	def test_merge_pdfs_rejects_non_pdf_file(self):
		self.assertRaises(
			frappe.ValidationError,
			merge_pdfs,
			self.todo.doctype,
			self.todo.name,
			self.todo.name,
			[self.image_file.name],
		)

	def test_merge_pdfs_rejects_empty_pdf_name(self):
		self.assertRaises(
			frappe.ValidationError,
			merge_pdfs,
			self.todo.doctype,
			self.todo.name,
			"   ",
			[self.pdf_file.name],
		)

	def test_merge_pdfs_keeps_pdf_extension(self):
		result = merge_pdfs(
			self.todo.doctype,
			self.todo.name,
			"report.pdf",
			[self.pdf_file.name],
		)

		self.assertEqual(result["file_name"], "report.pdf")

	def test_merge_pdfs_attaches_merged_file_to_document(self):
		result = merge_pdfs(
			self.todo.doctype,
			self.todo.name,
			self.todo.name,
			[self.pdf_file.name],
		)

		self.assertTrue(result["file_url"])
		self.assertEqual(result["file_name"], f"{self.todo.name}.pdf")
		self.assertTrue(result["file_url"].startswith("/private/files/"))

		file_doc = frappe.get_doc("File", result["name"])
		self.assertEqual(file_doc.is_private, 1)

		attached_files = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": self.todo.doctype,
				"attached_to_name": self.todo.name,
				"file_name": result["file_name"],
			},
		)
		self.assertEqual(len(attached_files), 1)


def _create_attached_file(
	doctype: str,
	docname: str,
	file_name: str,
	content: bytes,
	is_private: int = 0,
):
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": file_name,
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"is_private": is_private,
			"content": content,
		}
	)
	file_doc.insert()
	return file_doc
