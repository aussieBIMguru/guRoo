# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms,revit, DB, UI, script

# create custom message class based on view object
class ViewsToPurge(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.Name

# get document
doc = revit.doc

# get all views in document
views   = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
filters = DB.FilteredElementCollector(revit.doc).OfClass(DB.FilterElement).ToElements()

# Create empty lists
Filter_used, Filter_all, Filter_unused = [],[],[]

# Get filter Ids
Filter_all = [f.Id for f in filters]

# Find filters used on legends, templates and views
with forms.ProgressBar(step=10, title="Checking filters assigned to views") as pb1:
	pb1Count = 1
	pb1Length = len(views)
	for v in views:
		vType = v.ViewType
		if vType == DB.ViewType.Schedule or vType == DB.ViewType.DrawingSheet or v.Name == "System Browser" or v.Name == "Project View":
			pass
		else:
			vfs = v.GetFilters()
			for f in vfs:
				if f not in Filter_used:
					Filter_used.append(f)
		pb1.update_progress(pb1Count, pb1Length)
		pb1Count += 1

# Check if filters are used
with forms.ProgressBar(step=1, title="Checking if filters are in use") as pb2:
	pb2Count = 1
	pb2Length = len(Filter_all)
	for f in Filter_all:
		if f not in Filter_used:
			Filter_unused.append(f)
		pb2.update_progress(pb2Count, pb2Length)
		pb2Count += 1

# display primary UI if views found
if not Filter_unused:
    forms.alert("No unused View filters found.", title= "Script complete")
else:
    # Check elements are available
    if doc.IsWorkshared:
        from roo_worksharing import *
        checkOut = elements_editable(Filter_unused,doc,True)
        Filter_unused = checkOut[1]
    # ask user for wipe actions
    return_options = \
        forms.SelectFromList.show(
            [ViewsToPurge(revit.doc.GetElement(vf))
            for vf in Filter_unused],
            title='Select Unused View filters to Purge',
            width=500,
            button_name='Purge',
            multiselect=True
            )
    # if user selects view filters, attempt to delete them
    if return_options:
        with forms.ProgressBar(step=1, title="Deleting unused view filters") as pb3:
            pb3Count = 1
            pb3Length = len(return_options)
            del_fail = 0
            with revit.Transaction('Purge Views filters'):
                for vt in return_options:
                    try:
                        revit.doc.Delete(vt.Id)
                    except:
                        del_fail += 1
                    pb3.update_progress(pb3Count, pb3Length)
                    pb3Count += 1
        # display the purging outcome
        count_views = len(return_options)
        form_message = str(count_views-del_fail) + "/" + str(count_views) + " View filters successfully Purged."
        forms.alert(form_message, title= "Script complete", warn_icon=False)
        
    # if script is cancelled
    else:
        forms.alert("No View filters Purged.", title= "Script cancelled", warn_icon=False)