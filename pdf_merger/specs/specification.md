# General

This app supports users to quickly merge PDFs within an ERPNext or Frappe site.

Overview of the features:
- Enable DocTypes that support the "Merge PDFs" feature.
- The merging feature itself consists of a button "Merge PDFs" & dialog to select the PDFs to merge.


## Enable DocTypes

In the single DocType **PDF Merger Settings** a System Manager can select for which DocType the PDF-merger-feature shall be enabled.

## Button + Dialog

In an enabled DocType the button "Merge PDFs" is displayed.
The button leads to a dialog with a mandatory _PDF Name_ field and a child table with linked files.

The _PDF Name_ field defaults to the document ID. The merged PDF is saved under this name (`.pdf` is appended if omitted).

The User now can:
- change the order of the file rows
- delete file rows
- add file rows (only of type PDF! And by considering the standard permission scheme.)

### Default PDFs

The dialog's child table shall be pre-filled with default PDFs.
These are the PDFs that are currently attached to the document.

### Submitting the dialog
When the dialog is submitted, the PDFs are merged using the provided _PDF Name_.
The newly created PDF (private!) is attached to the respective document under that name.
