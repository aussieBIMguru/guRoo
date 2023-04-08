# import pyrevit libraries
from pyrevit import forms,revit,DB,script
# print utility library
from guRoo_expUtils import *

# make sure you can print, construct print path and make directory
expUtils_canPrint()
dirPath = expUtils_getDir() + "\\" + expUtils_getFolder("_DWG Views")
expUtils_ensureDir(dirPath)

# get document
doc = revit.doc
uidoc = revit.uidoc

# get all views in document
views = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()

unsortedViews,unsortedTypes = [],[]

# build set of view Ids for sorting and deletion
with forms.ProgressBar(step=10, title="Collecting views") as pb2:
	pbTotal2 = len(list(views))
	pbCount2 = 1
	for v in views:
		if v.IsTemplate == False and v.ViewType != DB.ViewType.Legend:
			unsortedViews.append(v.Id.IntegerValue)
			unsortedTypes.append(str(v.ViewType))
		pb2.update_progress(pbCount2, pbTotal2)
		pbCount2 += 1

# sort the list of views by their type
allViews = [v for _, v in sorted(zip(unsortedTypes, unsortedViews))]

# create custom message class based on view object
class ViewsToShow(forms.TemplateListItem):
	@property
	def name(self):
		return str(self.item.ViewType) + ' : ' + self.item.Name

# If no sheets, stop
if allViews:
	# ask user for sheets to export
	return_options = \
		forms.SelectFromList.show(
			[ViewsToShow(revit.doc.GetElement(DB.ElementId(v)))
			for v in allViews],
			title='Select Views to Export',
			width=500,
			button_name='Export',
			multiselect=True
			)
	if return_options:
		with forms.ProgressBar(step=1, title='Exporting views... ' + '{value} of {max_value}', cancellable=True) as pb1:
			# open the directory
			expUtils_openDir(dirPath)
			pbTotal1 = len(return_options)
			pbCount1 = 1
			# Make print options
			opts = expUtils_dwgOpts()
			# Export each sheet selected by user
			for v in return_options:
				if pb1.cancelled:
					break
				else:
					# Export sheet to PDF
					expUtils_exportViewDwg(dirPath,v,opts,doc,uidoc)
					# Update progress bar
					pb1.update_progress(pbCount1, pbTotal1)
					pbCount1 += 1
		# Cancel check
		if pb1.cancelled:
			forms.alert("Export process cancelled.", title= "Script cancelled")
		else:
			forms.alert("Export process complete.", title= "Script finished", warn_icon=False)