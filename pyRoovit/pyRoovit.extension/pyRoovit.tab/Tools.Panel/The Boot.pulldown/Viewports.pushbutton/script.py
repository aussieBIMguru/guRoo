# import libraries
import clr
import os
import datetime
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB, UI
from pyrevit import script

# create custom message class based on sheet object
class ViewSheetToPurge(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.SheetNumber + ' - ' + self.item.Name

# get document
doc = revit.doc

# -- ARCHILOGGER START --
toolName = 'Purge Viewports'
docTitle = doc.Title
dateStamp   = datetime.datetime.today().strftime("%d/%m/%y")
timeStamp   = datetime.datetime.today().strftime("%H:%M:%S")
userName    = os.environ.get("USERNAME")
userProfile = os.environ.get("USERPROFILE")
myPath = r"\\architectus.local\dfs\Resources\DesignTechnology\CAD and BIM\Revit\pyRevit Logging" + "\\"
myLog   = myPath + "pyRevitLog_" + userName + ".csv"
dataRow = dateStamp + "," + timeStamp + "," + userName + "," + toolName +".py" + "," + docTitle + ".rvt"
# -- ARCHILOGGER WRITE --
try:
	with open(myLog, "a") as file:
		file.writelines(dataRow + "\n")
except:
	pass
# -- ARCHILOGGER FINISHED --

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
        del_pass = 0
        with revit.Transaction('Purge Viewports'):
            for sht in return_options:
                sheetVps = sht.GetAllViewports()
                for vp in sheetVps:
                    try:
                        revit.doc.Delete(vp)
                        del_pass += 1
                    except:
                        pass

        # display the purging outcome
        form_message = str(del_pass) + " Viewports successfully Purged."
        forms.alert(form_message, title= "Script complete", warn_icon=False)
    # if script is cancelled
    else:
        forms.alert("No Viewports Purged.", title= "Script cancelled", warn_icon=False)