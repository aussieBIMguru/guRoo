# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB, UI
from pyrevit import script

# create custom message class based on sheet object
class ViewSheetToDownrev(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.SheetNumber + ' - ' + self.item.Name

# get document
doc = revit.doc

# get all sheets in document
sheets = DB.FilteredElementCollector(revit.doc)\
          .OfCategory(DB.BuiltInCategory.OST_Sheets)\
          .WhereElementIsNotElementType()\
          .ToElements()

unsortedSheets,unsortedNumbers = [],[]

# build set of sheet Ids for sorting and deletion
for s in sheets:
    unsortedSheets.append(s.Id.IntegerValue)
    unsortedNumbers.append(s.SheetNumber)

# sort the list of sheets by their numbers
allSheets = [s for _, s in sorted(zip(unsortedNumbers, unsortedSheets))]

# select a revision from the list
downrev = forms.select_revisions(title='Select a Revision to add...', button_name='Select', width=500, multiple=False)

# display primary UI if revision provided and sheets available
if not allSheets:
    forms.alert("No Sheets available to Downrev.", title= "Script cancelled")
elif not downrev:
    forms.alert("Revision not selected.", title= "Script cancelled")
else:
    # ask user for sheets to down
    return_options = \
        forms.SelectFromList.show(
            [ViewSheetToDownrev(revit.doc.GetElement(DB.ElementId(s)))
            for s in allSheets],
            title='Select Sheets to Downrev',
            width=500,
            button_name='Downrev Sheets',
            multiselect=True
            )
    # Import worksharing utilities
    from roo_worksharing import *
    
    # If workshared document, check if elements are editable
    # Note the user will be able to cancel the process if no-editable elements are found
    if doc.IsWorkshared:
        checkOut = elements_editable(return_options,doc,True)
        return_options = checkOut[1]
    
    # if user selects sheets, attempt to downrev them
    if return_options:
        with forms.ProgressBar(step=1, title='Downreving sheets... ' + '{value} of {max_value}') as pb1:
            pbTotal1 = len(return_options)
            pbCount1 = 1
            rev_pass = 0
            with revit.Transaction('Downrev Sheets'):
                for sht in return_options:
                    pb1.update_progress(pbCount1, pbTotal1)
                    pbCount1 += 1
                    sheetRevs = sht.GetAdditionalRevisionIds()
                    if downrev.Id in sheetRevs:
                        sheetRevs.Remove(downrev.Id)
                    else:
                        continue
                    try:
                        sht.SetAdditionalRevisionIds(sheetRevs)
                        rev_pass += 1
                    except:
                        pass
        # display the purging outcome
        form_message = str(rev_pass) + "/" + str(len(return_options)) + " Sheets successfully de-revisioned."
        forms.alert(form_message, title= "Script complete", warn_icon=False)
        
    # if script is cancelled
    else:
        forms.alert("No Sheets de-revisioned.", title= "Script cancelled", warn_icon=False)