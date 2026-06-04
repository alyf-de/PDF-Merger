# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from pdf_merger.settings import clear_enabled_doctypes_cache


class PDFMergerSettings(Document):
	def on_update(self):
		clear_enabled_doctypes_cache()
