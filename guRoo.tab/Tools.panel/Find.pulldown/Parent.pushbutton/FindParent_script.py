# import pyrevit libraries
from pyrevit import revit,DB,script,forms

# get document
doc = revit.doc
uidoc = revit.uidoc
curView = revit.active_view

# try to find parent view
try:
	parentViewId = curView.get_Parameter(DB.BuiltInParameter.SECTION_PARENT_VIEW_NAME).AsElementId()
	ownerView = doc.GetElement(parentViewId)
	uidoc.RequestViewChange(ownerView)
except:
	ownerView = None

# try to find primary view
if ownerView == None:
	try:
		primaryViewId = curView.GetPrimaryViewId()
		ownerView = doc.GetElement(primaryViewId)
		uidoc.RequestViewChange(ownerView)
	except:
		forms.alert('View has no parent or primary.', title='Script complete', warn_icon=False)