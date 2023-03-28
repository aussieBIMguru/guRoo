# Prepare for converters
from pyrevit import revit,DB,forms,script

# function for getting element from string
def delUtils_getFromKey(s):
	splitName = s.rsplit("[")[-1]
	strId = splitName.replace("]","")
	eleId = DB.ElementId(int(strId))
	return eleId

# function for pb length
def delUtils_pbStep(lst, divs = 10):
	try:
		stepRound = int(len(lst)/divs)
		if stepRound < 1:
			return 1
		else:
			return stepRound
	except:
		return 1

def delUtils_pbCancelled(pb,pbMsg="Script cancelled.",pbTitle="Script cancelled."):
	if pb.cancelled:
		forms.alert(pbMsg, title= pbTitle)
		script.exit()

# function for deletion
def delUtils_delEle(e,myDoc=revit.doc):
	try:
		myDoc.Delete(e.Id)
		return 1
	except:
		try:
			myDoc.Delete(e)
			return 1
		except:
			return 0

# delete elements with reporting
def delUtils_delEles(eles,myDoc=revit.doc,pbTitle="Deleting elements..."):
	with forms.ProgressBar(step=1, title=pbTitle + '{value} of {max_value}', cancellable=True) as pb:
		pbCount = 1
		pbTotal = len(eles)
		del_pass = 0
		with revit.Transaction('Delete elements'):
			for e in eles:
				if not pb.cancelled:
					del_pass += delUtils_delEle(e)
				else:
					break
				pb.update_progress(pbCount, pbTotal)
				pbCount += 1
		# display the purging outcome
		if pb.cancelled:
			form_extra = " (script cancelled partway through deletion)."
		else:
			form_extra = "."
		form_message = str(del_pass) + "/" + str(pbTotal) + " elements successfully deleted"
		forms.alert(form_message+form_extra, title= "Deletion completed", warn_icon=False)