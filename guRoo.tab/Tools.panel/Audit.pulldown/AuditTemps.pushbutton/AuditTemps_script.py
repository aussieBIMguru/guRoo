# import pyrevit libraries
from pyrevit import forms,revit,DB,script
from guRoo_delUtils import *

# create custom message class based on view object
class ViewsToPurge(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.Name

# get document
doc = revit.doc

# get all views in document
views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
vfts  = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType).ToElements()

# Get element Ids of view templates in use on views (legends/schedules included)
templates_used, templates_all, templates_unused = [],[],[]

with forms.ProgressBar(step=10, title="Checking templates assigned to views") as pb1:
	pb1Count = 1
	pb1Length = len(views)
	for v in views:
		vType = v.ViewType
		if v.IsTemplate:
			tid = v.Id.IntegerValue
			templates_all.append(tid)
		elif vType == DB.ViewType.DrawingSheet or v.Name == "System Browser" or v.Name == "Project View":
			pass
		else:
			tid = v.ViewTemplateId.IntegerValue
			if tid not in templates_used and tid != -1:
				templates_used.append(tid)
		pb1.update_progress(pb1Count, pb1Length)
		pb1Count += 1

# Get element ids of view family type templates
with forms.ProgressBar(step=1, title="Checking templates assigned to view family types") as pb2:
    pb2Count = 1
    pb2Length = len(vfts)
    for vft in vfts:
        tid = vft.DefaultTemplateId.IntegerValue
        if tid not in templates_used and tid != -1:
            templates_used.append(tid)
        pb2.update_progress(pb2Count, pb2Length)
        pb2Count += 1

# Find the template difference
for vt in templates_all:
    if vt not in templates_used:
        templates_unused.append(DB.ElementId(vt))

# display primary UI if views found
if not templates_unused:
    forms.alert("No unused View templates found.", title= "Script completed", warn_icon=False)
else:
    # ask user for wipe actions
    return_options = \
        forms.SelectFromList.show(
            [ViewsToPurge(revit.doc.GetElement(vt))
            for vt in templates_unused],
            title='Unused View templates',
            width=500,
            button_name='Delete',
            multiselect=True
            )
    # if user selects view templates, attempt to delete them
    # note: If the active view is a view templates, it may fail to delete
    if return_options:
        # Check elements are available
        if doc.IsWorkshared:
            from guRoo_shareUtils import *
            checkOut = elements_editable(return_options,doc,True)
            return_options = checkOut[1]
        # Try to delete elements
        delUtils_delEles(return_options,doc,pbTitle="Deleting View templates...")