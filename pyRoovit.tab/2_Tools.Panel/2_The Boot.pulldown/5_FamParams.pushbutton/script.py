# preImport
from pyrevit import forms

# postImport
from pyrevit import revit, DB, script

# Store current document into variable
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# get family manager
famMan = doc.FamilyManager

# Ask user to pick family parameters
paramSelect = forms.select_family_parameters(doc, title='Select Parameters', button_name='Delete', multiple=True, include_builtin=False)

# If parameters available, try to delete them
if not paramSelect:
    forms.alert("No parameters selected", title= "Script cancelled")
else:
    with forms.ProgressBar(step=1, title="Deleting parameters") as pb:
        
        pbCount = 0
        pbTotal = len(paramSelect)
        
        parLen = str(pbTotal)
        parCnt = 0
        
        with revit.Transaction('Delete parameters'):
            for p in paramSelect:
                try:
                    famMan.RemoveParameter(p)
                    parCnt += 1
                except:
                    pass
                # Update progress bar
                pb.update_progress(pbCount, pbTotal)
                pbCount += 1
        
        parRatio = str(parCnt) + "/" + parLen
        forms.alert(parRatio + " Family parameters deleted.", "Script completed", warn_icon=False)