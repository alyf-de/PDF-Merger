# General

This app supports users to quickly merge PDFs within an ERPNext or Frappe site.

Overview of the features:
- Enable DocTypes that support the "Merge PDFs" feature.
- The merging feature itself consists of a button "Merge PDFs" & dialog to select the PDFs to merge.


## Enable DocTypes

In the single DocType **PDF Merger Settings** a System Manager can select for which DocType the PDF-merger-feature shall be enabled.

## Button + Dialog

In an enabled DocType the button "Merge PDFs" is displayed.
The button leads to a dialog that shows a child table with linked files.

The User now can:
- change the order of the file rows
- delete file rows
- add file rows (only of type PDF! And by considering the standard permission scheme.)

### Default PDFs

The dialog's child table shall be pre-filled with default PDFs.
These are the PDFs that are currently attached to the document.

### Submitting the dialog
When the dialog is submitted, the PDFs are merged. The newly created PDF is attached to the respective document.


# TODO
Ideas:
- Permissions: Consider standard permission (and also "Print" for the relevant doctype)
- Hooks to overwrite the defaults: The Default PDFs can be overwritten by custom apps.
- Add print format: User can also add a print format to the dialog, such that this is also added as PDF.
- Document naming: User can set a default name (either as a naming series per DocType, see PDF merger settings, or an individual per dialog or both)
