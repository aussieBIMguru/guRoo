# import pyrevit libraries
from pyrevit import revit,DB,forms,script

# get document
doc = revit.doc

# Prompt user to specify file path
pathFile = forms.pick_file(files_filter='Excel Workbook (*.xlsx)|*.xlsx|''Excel 97-2003 Workbook|*.xls')

# Catch if no file selected
if not pathFile:
    script.exit()

# import Excel dependent libraries
from guRoo_xclUtils import *

# Import excel data
xcl = xclUtils([],pathFile)
dat = xcl.xclUtils_import("Sheet1",2,0)

# Try to get column data
if dat[1]:
	worksetNames = []
	for row in dat[0]:
		worksetNames.append(str(row[0]))
else:
	forms.alert("Data not found. Make sure Excel is closed, and on Sheet1.", title= "Script cancelled")
	script.exit()

# collect all worksets in document
fec_worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset).ToWorksets()

# get all workset names as a list
names_worksets,names_new = [],[]

# Only proceed with workset names not in use
for w in fec_worksets:
    names_worksets.append(w.Name)

for n in worksetNames:
    if n not in names_worksets:
        names_new.append(n)
    else:
        continue
        
# show a UI to add workset names not present
selectWorksets = forms.SelectFromList.show(names_new, 'Select worksets to create', 500, 800, multiselect=True, button_name='Create')

# if no worksets selected, finish the script
if selectWorksets:
    with forms.ProgressBar(step=1 , title="Creating worksets..." + "{value} of {max_value}") as pb:
    
    finalCount = len(selectWorksets)
        progressCount = 1
        madeWorksets = 0
        
        for n in selectWorksets:
            
            with revit.Transaction('Make workset'):
                try:
                    DB.Workset.Create(doc, n)
                    madeWorksets += 1
                except:
                    pass
            
            # Update progress bar
            pb.update_progress(progressCount, finalCount)
            progressCount += 1
            
        # final message to the user
        forms.alert(str(madeWorksets) + ' new Worksets created.',title='Script complete.', warn_icon=False)