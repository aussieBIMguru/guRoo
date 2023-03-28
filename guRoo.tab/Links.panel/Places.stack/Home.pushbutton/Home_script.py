# import pyrevit libraries
from pyrevit import revit,DB,forms

# get document
doc = revit.doc
uidoc = revit.uidoc

# get start view
startView   = DB.StartingViewSettings.GetStartingViewSettings(doc)
try:
	startViewId = startView.ViewId
except:
	startViewId = 0

curView  = doc.ActiveView

# If no ttb found, give up
if startViewId != 0 and curView.Id != startViewId:
	uidoc.RequestViewChange(doc.GetElement(startViewId))
	allViews = uidoc.GetOpenUIViews()
	for v in allViews:
		if v.ViewId != startViewId:
			try:
				v.Close()
			except:
				pass