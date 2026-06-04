from pdf_merger.settings import get_enabled_doctypes


def boot_session(bootinfo):
	bootinfo.pdf_merger_enabled_doctypes = get_enabled_doctypes()
