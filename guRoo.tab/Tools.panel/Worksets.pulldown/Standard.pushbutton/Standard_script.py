# import pyrevit libraries
import clr
import os, csv
from pyrevit import revit,DB,forms,script

# get document
doc = revit.doc

# Get workset names from package csv
curPath = script.get_script_path()
remPath = curPath.split('guRoo.tab')[0]
csvFile = remPath + r'bin\Standards\BG Worksets.csv'

# check if the file exists, get names if so
if os.path.isfile(csvFile):
    with open(csvFile,"r") as f:
        reader = csv.reader(f)
        worksetNames = [row[0] for row in csv.reader(f.read().splitlines())]
else:
    forms.alert('No settings file found.', title='Script cancelled')
    script.exit()

# collect all worksets in document
fec_worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset).ToWorksets()

# get all workset names as a list
names_worksets = []

for w in fec_worksets:
    names_worksets.append(w.Name)

# if shared levels and grids is present, offer to rename it
if "Shared Levels and Grids" in names_worksets:
	rename_slg = forms.alert('Would you like to rename Shared Levels and Grids?', title='Workset detected', ok =False, yes=True, no=True, warn_icon=False)
	if rename_slg:
		i = names_worksets.index("Shared Levels and Grids")
		w = fec_worksets[i]
		with revit.Transaction('Renaming levels and grids'):
			DB.WorksetTable.RenameWorkset(doc,w.Id,'00_Levels and Grids')

# only allow workset names which are not taken yet
names_new = []

for n in worksetNames:
    if n not in names_worksets:
        names_new.append(n)
    else:
        continue
        
# show a UI to add workset names not present
selectWorksets = forms.SelectFromList.show(names_new, 'Select worksets to create', 500, 800, multiselect=True, button_name='Create')

# if no worksets selected, finish the script
if not selectWorksets:
    script.exit()
# proceed to create any other worksets
else:
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