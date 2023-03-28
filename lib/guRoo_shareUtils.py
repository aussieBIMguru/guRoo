# Prepare for converters
import clr
import os
import csv
from pyrevit import revit,DB,forms,script

# verify if settings exist
def shareUtils_workshared(myDoc):
	return myDoc.IsWorkshared

# verify element worksets
def shareUtils_getWorkset(elements):
	curDoc = revit.doc
	wsid = e.WorksetId
	ws   = revit.curDoc.GetWorksetTable().GetWorkset(wsid)
	return ws

# Verify if an element is editable
def shareUtils_isEditable(e,curDoc):
	if curDoc.IsWorkshared:
		cs = DB.WorksharingUtils.GetCheckoutStatus(curDoc,e.Id).ToString()
		return cs != "OwnedByOtherUser"
	else:
		return True

# Verify element worksets with optional break point, filter and report
def shareUtils_getEditable(elements,curDoc,report = False):
	# if document is workshared
	if curDoc.IsWorkshared:
		isEditable,eleIn,eleOut = [],[],[]
		# For each element, get it's checkout status
		for e in elements:
			# Split elements by if they are editable
			if shareUtils_isEditable(e,curDoc):
				eleIn.append(e)
			else:
				eleOut.append(e)
	# If not workshared, we just proceed onward
	else:
		isEditable, = [True for e in elements]
		eleIn = [e for e in elements]
		eleOut = []
	# Report and option to stop
	opt = "None"
	if report and eleOut:
		items = ["Proceed with what is editable","Proceed with what is editable, report what was not","Cancel the script (at this point)"]
		opt = forms.ask_for_one_item(items, default=None, prompt="How would you like to proceed? If you cancel this dialogue, the script will proceed with all editable elements.", title="Non-editable items found")
	# Use the option chosen
	if opt != "None" and "Cancel" in opt:
		forms.alert("Script cancelled by user.", title= "Option chosen")
		script.exit()
	elif opt != "None" and "report" in opt:
		output = script.get_output()
		print("NON-EDITABLE ELEMENT IDS")
		print("These items have been ignored when running this script.")
		print("You can select the Ids in this list to inspect them")
		print("---")
		for e in eleOut:
			print('Element Id {}'.format(output.linkify(e.Id)))
	# Return the outcomes
	return [isEditable,eleIn,eleOut]