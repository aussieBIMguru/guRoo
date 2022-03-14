# import libraries
import clr
import os
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB, UI
from pyrevit import script

# create custom message class based on sheet object
class ViewSheetToUprev(forms.TemplateListItem):
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
uprev = forms.select_revisions(title='Select a Revision to add...', button_name='Select', width=500, multiple=False)

# display primary UI if revision provided and sheets available
if not allSheets:
    forms.alert("No Sheets available to Uprev.", title= "Script cancelled")
elif not uprev:
    forms.alert("Revision not selected.", title= "Script cancelled")
else:
    # ask user for sheets to uprev
    return_options = \
        forms.SelectFromList.show(
            [ViewSheetToUprev(revit.doc.GetElement(DB.ElementId(s)))
            for s in allSheets],
            title='Select Sheets to Uprev',
            width=500,
            button_name='Uprev Sheets',
            multiselect=True
            )
            
    # if user selects sheets, attempt to uprev them
    # note: Sheets that are rev'd already remain rev'd
    if return_options:
        rev_pass = 0
        
        with revit.Transaction('Uprev Sheets'):
            for sht in return_options:
                sheetRevs = sht.GetAdditionalRevisionIds()
                
                if uprev.Id not in sheetRevs:
                    sheetRevs.Add(uprev.Id)
                else:
                    continue
                
                try:
                    sht.SetAdditionalRevisionIds(sheetRevs)
                    rev_pass += 1
                except:
                    pass
                    
        # display the purging outcome
        form_message = str(rev_pass) + "/" + str(len(return_options)) + " Sheets successfully Revisioned."
        forms.alert(form_message, title= "Script complete", warn_icon=False)
        
    # if script is cancelled
    else:
        forms.alert("No Sheets Revisioned.", title= "Script cancelled", warn_icon=False)