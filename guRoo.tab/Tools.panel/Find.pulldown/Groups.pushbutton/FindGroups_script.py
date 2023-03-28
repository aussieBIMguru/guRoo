# import pyrevit libraries
from pyrevit import script,revit,DB,forms

# Get active revit document
doc = revit.doc

# Get output for later linkifying
output = script.get_output()

# Get all images and their views
coll_grp = DB.FilteredElementCollector(doc).OfClass(DB.Group).ToElements()

grp_ids, grp_names, actual_names, view_ids = [],[],[],[]

# Get CAD Type names
for grp in coll_grp:
	grp_ids.append(grp.Id)
	actual_names.append(grp.Name)
	n = grp.Name.replace(" (members excluded)", "")
	grp_names.append(n)
	if grp.ViewSpecific:
		vid = grp.OwnerViewId
		view_ids.append(vid)
	else:
		view_ids.append("")

# Sorted names
set_name = list(set(grp_names))
set_name.sort

# Group CAD by their names
lstIds,lstViews,lstNames = [],[],[]

for n in set_name:
	slstIds   = []
	slstViews = []
	slstNames = []
	for i,v,na,an in zip(grp_ids,view_ids,grp_names,actual_names):
		if na == n:
			slstIds.append(i)
			slstViews.append(v)
			slstNames.append(an)
	lstIds.append(slstIds)
	lstViews.append(slstViews)
	lstNames.append(slstNames)

# Report header
output.print_md("REPORT OF GROUP INSTANCES")
print('\n' + str(len(set_name)) + ' Total group types found in model.')
print('Click on the Id to select an object in Revit.' + '\n\n')

# Report contents
for t,ids,names,views in zip(set_name,lstIds,lstNames,lstViews):
	print('\n' + t + ':')
	for i,n,v in zip(ids,names,views):
		if v == "":
			print('id {} Model group '.format(output.linkify(i)) + n)
		else:
			print('id {} Detail group '.format(output.linkify(i)) + n + ", specific to view " + 'id {}'.format(output.linkify(v)))
	print('\n')