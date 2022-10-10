# check if family document
from pyrevit import revit

# get document
doc = revit.doc

if doc.IsFamilyDocument:
	pass
else:
	# import libraries
	from pyrevit import EXEC_PARAMS, forms

	# prevent the tool, await input
	mip = forms.alert("Import CAD should be used sparingly in project models, are you sure?", options = ["Yes", "No"], title = "Modelling in place", footer = "pyRarch")

	# process the outcome
	if mip == "Yes":
		EXEC_PARAMS.event_args.Cancel = False
	else:
		EXEC_PARAMS.event_args.Cancel = True