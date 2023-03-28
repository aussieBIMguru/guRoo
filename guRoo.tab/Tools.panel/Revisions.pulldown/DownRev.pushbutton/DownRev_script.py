# import pyrevit libraries
from pyrevit import forms, revit, DB, script

# get document
doc = revit.doc

# function to rev sheets
def downRev(sht,rev):
	sheetRevs = sht.GetAdditionalRevisionIds()
	rev_id = rev.Id
	if rev_id in sheetRevs:
		sheetRevs.Remove(rev_id)
	try:
		sht.SetAdditionalRevisionIds(sheetRevs)
		return 1
	except:
		return 0

# select a revision from the list
downrev = forms.select_revisions(title='Select revision', button_name='Select', width=500, multiple=False)

# display primary UI if revision provided and sheets available
if downrev:
	# ask user for sheets to down
	return_options = forms.select_sheets(title='Select Sheets', include_placeholder = False, use_selection = True)
	
	# If workshared document, check if elements are editable
	# Note the user will be able to cancel the process if no-editable elements are found
	if doc.IsWorkshared:
		from guRoo_shareUtils import *
		checkOut = shareUtils_getEditable(return_options,doc,True)
		return_options = checkOut[1]
	
	# if user selects sheets, attempt to downrev them
	if return_options:
		# Run revisioning task
		with forms.ProgressBar(step = 1, title='Revising sheets... ' + '{value} of {max_value}', cancellable = True) as pb1:
			pbTotal1 = len(return_options)
			pbCount1 = 1
			rev_pass = 0
			with revit.Transaction('Downrev Sheets'):
				for sht in return_options:
					if not pb1.cancelled:
						rev_pass += downRev(sht,downrev)
						pb1.update_progress(pbCount1, pbTotal1)
						pbCount1 += 1
					else:
						forms.alert("Script cancelled.", title= "Script cancelled", warn_icon=False)
						break
		
		# display the outcome
		form_message = str(rev_pass) + "/" + str(pbTotal1) + " Sheets updated."
		forms.alert(form_message, title= "Script complete", warn_icon=False)