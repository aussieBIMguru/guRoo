# import pyrevit libraries
from pyrevit import forms,revit,DB,script

# create custom message class based on element
class PatternToPurge(forms.TemplateListItem):
	@property
	def name(self):
		if "Line" in str(self.item):
			return "Line pattern: " + self.item.Name
		else:
			return "Fill pattern: " + self.item.Name

# get document
doc = revit.doc

# get all pattern objects
linePatterns = DB.FilteredElementCollector(revit.doc).OfClass(DB.LinePatternElement).ToElements()
fillPatterns = DB.FilteredElementCollector(revit.doc).OfClass(DB.FillPatternElement).ToElements()
allPatterns  = list(linePatterns) + list(fillPatterns)

# Get imported patterns only
impPatterns = []

for p in allPatterns:
	if "IMPORT" in p.Name.upper():
		impPatterns.append(p)

# Check if any patterns
if len(impPatterns) == 0:
	forms.alert("No imported patterns found.", title= "Script completed", warn_icon=False)

# sort the patterns
sortedPatterns = sorted(impPatterns, key=lambda x: PatternToPurge(x))

# display primary UI if views found
if sortedPatterns:
	# ask user for patterns
	optionPatterns = [PatternToPurge(p) for p in sortedPatterns]
	return_options = forms.SelectFromList.show(optionPatterns,title='Imported patterns',width=500,button_name='Delete',multiselect=True)
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
		delUtils_delEles(return_options,doc,pbTitle="Deleting patterns...")