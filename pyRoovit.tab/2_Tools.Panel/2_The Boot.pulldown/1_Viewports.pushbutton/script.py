# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms,revit,DB,UI,script
from roo_worksharing import *

# create custom message class based on sheet object
class ViewSheetToPurge(forms.TemplateListItem):
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

# display primary UI if sheets found
if not allSheets:
    forms.alert("No Sheets found to Purge.", title= "Script complete")
else:
    # ask user for wipe actions
    return_options = \
        forms.SelectFromList.show(
            [ViewSheetToPurge(revit.doc.GetElement(DB.ElementId(s)))
            for s in allSheets],
            title='Select Sheets to Purge',
            width=500,
            button_name='Purge Viewports',
            multiselect=True
            )
    # if user selects sheets, attempt to delete them
    # note: If the active view is a sheet, it may fail to delete
    if return_options:
        with forms.ProgressBar(step=1, title="Purging viewports from sheets") as pb1:
            pbTotal1 = len(return_options)
            pbCount1 = 1
            del_pass = 0
            with revit.Transaction('Purge Viewports'):
                for sht in return_options:
                    sheetVps = sht.GetAllViewports()
                    # Check elements are available
                    if doc.IsWorkshared:
                        checkOut = elements_editable(sheetVps,doc,True)
                        sheetVps = checkOut[1]
                    for vp in sheetVps:
                        try:
                            revit.doc.Delete(vp)
                            del_pass += 1
                        except:
                            pass
                    pb1.update_progress(pbCount1, pbTotal1)
                    pbCount1 += 1
        # display the purging outcome
        form_message = str(del_pass) + " Viewports successfully Purged."
        forms.alert(form_message, title= "Script complete", warn_icon=False)
    # if script is cancelled
    else:
        forms.alert("No Viewports Purged.", title= "Script cancelled", warn_icon=False)