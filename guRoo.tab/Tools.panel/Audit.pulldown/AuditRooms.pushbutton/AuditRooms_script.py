# import pyrevit libraries
from pyrevit import forms,revit,DB,script

# get document
doc = revit.doc

# make room name
def makeName(r):
	rn = DB.Element.Name.__get__(r)
	return r.Number + ": " + rn + " [" + str(r.Id) + "]"

# get all rooms in document
rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms)

# get unplaced rooms
unplaced = [r for r in rooms if r.Location == None]

# display message if no views found
if len(unplaced) == 0:
	forms.alert("No unplaced rooms found.", title= "Script complete", warn_icon=False)
	script.exit()
else:
	# Show unplaced rooms
	ui_opts = [makeName(r) for r in unplaced]
	return_options = forms.SelectFromList.show(ui_opts,title ='Unplaced rooms',width = 500,button_name = 'Delete',multiselect = True)
	
	# Proceed if deletion given
	if return_options:
		
		# Make rooms from keys
		getRooms = [doc.GetElement(delUtils_getFromKey(r)) for r in return_options]
		
		# Check elements are available
		if doc.IsWorkshared:
			from guRoo_shareUtils import *
			checkOut = shareUtils_getEditable(getRooms,doc,True)
			getRooms = checkOut[1]
		
		# Delete rooms
		with forms.ProgressBar(step = 1, title='Deleting rooms... ' + '{value} of {max_value}', cancellable = True) as pb1:
			pbTotal1 = len(getRooms)
			pbCount1 = 1
			del_pass = 0
			with revit.Transaction('Delete rooms'):
				
				from guRoo_delUtils import *
				
				for r in getRooms:
					if not pb1.cancelled:
						del_pass += delUtils_delEle(r, doc)
						pb1.update_progress(pbCount1, pbTotal1)
						pbCount1 += 1
					else:
						forms.alert("Script cancelled partway.", title= "Script cancelled", warn_icon=False)
						break
			
			# display the outcome
			form_message = str(del_pass) + "/" + str(pbTotal1) + " unplaced rooms deleted."
			forms.alert(form_message, title= "Script complete", warn_icon=False)