import frappe

CACHE_KEY = "pdf_merger:enabled_doctypes"


def get_enabled_doctypes() -> list[str]:
	return frappe.cache.get_value(CACHE_KEY, _fetch_enabled_doctypes)


def clear_enabled_doctypes_cache() -> None:
	frappe.cache.delete_value(CACHE_KEY)


def _fetch_enabled_doctypes() -> list[str]:
	return frappe.get_all(
		"PDF Merger Settings DocType",
		filters={
			"parent": "PDF Merger Settings",
			"parenttype": "PDF Merger Settings",
			"parentfield": "doctypes",
		},
		pluck="document_type",
	)
