# import pyrevit libraries
from pyrevit import forms,revit,DB,script

# get sheets
selection = revit.get_selection()
doc = revit.doc

# check if sheets in selection
sel_sheets = []

for s in selection:
	try:
		if s.Category.Name == "Sheets":
			sel_sheets.append(s)
	except:
		pass

# if sheets, use these
if len(sel_sheets) > 0:
	pass
else:
	sel_sheets = forms.select_sheets(title='Select Sheets')

# update selection
if sel_sheets:
	sel_ids = [s.Id for s in sel_sheets]
else:
	script.exit()

# get all titleblocks
col_ttbs = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).ToElements()

# build selection ttbs
sel_ttbs = []

for ttb in col_ttbs:
	vid = ttb.OwnerViewId
	if vid in sel_ids:
		sel_ttbs.append(ttb)

# update selection
if len(sel_ttbs)>0:
	selection.set_to(sel_ttbs)