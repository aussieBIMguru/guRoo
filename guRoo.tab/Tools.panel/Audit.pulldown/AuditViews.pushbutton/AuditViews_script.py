# import pyrevit libraries
from pyrevit import forms,revit,DB,script

# create custom message class based on view object
class ViewsToPurge(forms.TemplateListItem):
	@property
	def name(self):
		return str(self.item.ViewType) + ' : ' + self.item.Name

# get document
doc = revit.doc

# get all views and view;ports in document
doc_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
viewports = DB.FilteredElementCollector(doc).OfClass(DB.Viewport).WhereElementIsNotElementType().ToElements()

# get actual views only
views,used_views,vp_views,unused_views = [],[],[],[]

with forms.ProgressBar(step=10, title="Getting views", cancellable=True) as pb1:
	pbTotal1 = len(list(doc_views))
	pbCount1 = 1
	for v in doc_views:
		if pb1.cancelled:
			break
		vType = v.ViewType
		if vType == DB.ViewType.Legend or vType == DB.ViewType.Schedule or v.IsTemplate or vType == DB.ViewType.DrawingSheet or v.Name == "System Browser" or v.Name == "Project View":
			pass
		else:
			views.append(v)
		pb1.update_progress(pbCount1, pbTotal1)
		pbCount1 += 1
	if pb1.cancelled:
		script.exit()

# get all views in those viewports, yield to sheet views
with forms.ProgressBar(step=10, title="Reviewing viewports", cancellable=True) as pb2:
	pbTotal2 = len(list(viewports))
	pbCount2 = 1
	for vp in viewports:
		if pb2.cancelled:
			break
		v = doc.GetElement(vp.ViewId)
		vp_views.append(v)
		used_views.append(v)
		pb2.update_progress(pbCount2, pbTotal2)
		pbCount2 += 1
	if pb2.cancelled:
		script.exit()

# get all primary views
with forms.ProgressBar(step=10, title="Reviewing primary views", cancellable=True) as pb3:
	pbTotal3 = len(list(vp_views))
	pbCount3 = 1
	for v in vp_views:
		if pb3.cancelled:
			break
		primary = doc.GetElement(v.GetPrimaryViewId())
		if primary != None:
			used_views.append(primary)
		pb3.update_progress(pbCount3, pbTotal3)
		pbCount3 += 1
	if pb3.cancelled:
		script.exit()

# get all parent views
with forms.ProgressBar(step=10, title="Reviewing parent views", cancellable=True) as pb4:
	pbTotal4 = len(list(vp_views))
	pbCount4 = 1
	for v in vp_views:
		if pb4.cancelled:
			break
		# set the base variable to loop through
		breaker = 0
		checkview = v
		treedepth = 1
		godeeper = True
		# exhaust the parent views
		while godeeper and breaker < 99:
			# uptick the breaker
			breaker += 1
			# try to get a parent
			try:
				parentId  = checkview.get_Parameter(DB.BuiltInParameter.SECTION_PARENT_VIEW_NAME).AsElementId()
				checkview = doc.GetElement(parentId)
				# if a parent is found, append and then check it
				if checkview != None:
					treedepth += 1
					used_views.append(checkview)
				# otherwise, stop
				else:
					godeeper = False
			# if it fails, stop
			except:
				godeeper = False
		pb4.update_progress(pbCount4, pbTotal4)
		pbCount4 += 1
	if pb4.cancelled:
		script.exit()

# get unused views
used_ids = [v.Id for v in used_views]
unsortedViews,unsortedTypes = [],[]

with forms.ProgressBar(step=10, title="Reviewing which views are unused", cancellable=True) as pb5:
	pbTotal5 = len(views)
	pbCount5 = 1
	for v in views:
		if pb5.cancelled:
			break
		if v.Id not in used_ids:
			unsortedViews.append(v.Id.IntegerValue)
			unsortedTypes.append(str(v.ViewType))
		pb5.update_progress(pbCount5, pbTotal5)
		pbCount5 += 1
	if pb5.cancelled:
		script.exit()

# sort the list of views by their type
unused_views = [v for _, v in sorted(zip(unsortedTypes, unsortedViews))]

# display primary UI if views found
if not unused_views:
    forms.alert("No unplaced views found.", title= "Script completed", warn_icon = False)
else:
	# ask user for wipe actions
	return_options = \
		forms.SelectFromList.show(
			[ViewsToPurge(revit.doc.GetElement(DB.ElementId(v)))
			for v in unused_views],
			title='Unplaced views',
			width=500,
			button_name='Delete',
			multiselect=True
			)
	# if user selects views, attempt to delete them
	# note: If the active view is a view, it may fail to delete
	if return_options:
		# Check elements are available
		if doc.IsWorkshared:
			from guRoo_shareUtils import *
			checkOut = shareUtils_getEditable(return_options,doc,True)
			return_options = checkOut[1]
		# Try to delete elements
		from guRoo_delUtils import *
		delUtils_delEles(return_options,doc,pbTitle="Deleting Views...")