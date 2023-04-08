# import pyrevit libraries
from pyrevit import revit,DB

# get document
doc = revit.doc
uidoc = revit.uidoc

# get start view
startView   = DB.StartingViewSettings.GetStartingViewSettings(doc)

# try to get home view
try:
	startViewId = startView.ViewId
	targetView = doc.GetElement(startViewId)
except:
	targetView = None

curView  = doc.ActiveView

# If not active, open the view
if targetView != None:
	uidoc.RequestViewChange(targetView)