# import pyrevit libraries
from pyrevit import forms,revit,DB,script

# get document
doc = revit.doc

# select a revision from the list
findRev = forms.select_revisions(title='Select revision', button_name='Select', width=500, multiple=False)
findRevId = findRev.Id

# no revision picked
if not findRev:
	forms.alert("Revision not selected.", title= "Script cancelled")

# get all clouds and their revision Ids
allSheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
revSheets = []

for s in allSheets:
	allRevIds = s.GetAllRevisionIds()
	if findRevId in allRevIds:
		revSheets.append(s)

# no clouds found
if len(revSheets) == 0:
	forms.alert("No sheets found with chosen revision.", title= "Script cancelled")
	script.exit()

# make a sheet set for that revision
proposedName = findRev.RevisionDate + " - " + findRev.Description

# get all sheet set names
allSheetSets     = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheetSet).WhereElementIsNotElementType().ToElements()
allSheetSetNames = [s.Name for s in allSheetSets]

# check if exists, allow ovewrite if so
if proposedName in allSheetSetNames:
	checkDelete = forms.alert("Sheet set exists, overwrite?", title= "Set exists", ok=False, cancel=False, yes=True, no=True)
	if checkDelete:
		ind = allSheetSetNames.index(proposedName)
		del_sheetSet = allSheetSets[ind]
		try:
			with revit.Transaction('Delete sheet set for overwrite'):
				doc.Delete(del_sheetSet.Id)
		except:
			forms.alert("Sheet set could not be overwritten.", title= "Script cancelled")
			script.exit()
	else:
		script.exit()

# make new sheet set
newSet = DB.ViewSet()

# add sheets to sheet set
for s in revSheets:
	newSet.Insert(s)

# configure print manager and sheet settings
printMan = doc.PrintManager
printMan.PrintRange = DB.PrintRange.Select
viewSS   = printMan.ViewSheetSetting

# make the new sheet set
with revit.Transaction('Make sheet set'):
	viewSS.CurrentViewSheetSet.Views = newSet
	viewSS.SaveAs(proposedName)
	forms.alert("New sheet set created.", title= "Script completed", warn_icon = False)