# Prepare for converters
import clr
from pyrevit import revit,DB,forms,script

# verify if settings exist
def isworkshared(myDoc):
	return myDoc.IsWorkshared

# verify element worksets
def elements_workset(elements):
	ownerset = []
	curDoc = revit.doc
	for e in elements:
		wsid = e.WorksetId
		ws   = revit.curDoc.GetWorksetTable().GetWorkset(wsid)
		ownerset.append(ws)
	return ownerset

# Verify element worksets with optional break point, filter and report
def elements_editable(elements,curDoc,report = False):
	# if document is workshared
	if curDoc.IsWorkshared:
		isEditable,eleIn,eleOut = [],[],[]
		# For each element, get it's checkout status
		for e in elements:
			cs = DB.WorksharingUtils.GetCheckoutStatus(curDoc,e.Id).ToString()
			ie = cs != "OwnedByOtherUser"
			isEditable.append(ie)
			# Split elements by if they are editable
			if ie:
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

# Verify if an element is editable
def element_editable(e,curDoc):
	if curDoc.IsWorkshared:
		cs = DB.WorksharingUtils.GetCheckoutStatus(curDoc,e.Id).ToString()
		return cs != "OwnedByOtherUser"
	else:
		return True

# Verify if an element is editable
def all_editable(elements,curDoc):
	# By default we are set to true
	verify = True
	if curDoc.IsWorkshared:
		# Test each element
		for e in elements:
			cs = DB.WorksharingUtils.GetCheckoutStatus(curDoc,e.Id).ToString()
			# If we find a non-editable element, break and set to False
			if cs == "OwnedByOtherUser":
				verify = False
				break
		return verify
	else:
		return verify