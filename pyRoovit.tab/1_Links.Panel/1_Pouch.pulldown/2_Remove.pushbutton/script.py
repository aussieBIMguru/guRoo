# import libraries
import clr
import os
import csv
# import pyrevit libraries
from pyrevit import forms, script

# get users mydocs
userName    = os.environ.get("USERNAME")
userProfile = os.environ.get("USERPROFILE")
userDocs = os.path.expanduser('~\Documents')
myLinks     = userDocs + "\\" "pyRoovitmyLinks_" + userName + ".csv"

# check if the file exists
if os.path.isfile(myLinks):
    with open(myLinks,"r") as file:
        reader = csv.reader(file,delimiter = "~")
        csv_data = list(reader)
        row_count = len(csv_data)
else:
    forms.alert('Must store links before forgetting them.', title='Script cancelled')
    script.exit()

# check if there are rows, then write them to alias/path pairs
link_alias,link_path = [],[]

# try to deconstruct the csv list
if row_count > 0:
    for lst in csv_data:
        link_alias.append(lst[0])
        link_path.append(lst[1])
else:
    forms.alert('Must store links before forgetting them.', title='Script cancelled')
    script.exit()

# ask the user to nominate paths for removal
selectPaths = forms.SelectFromList.show(link_alias, 'Select links to forget', 500, 800, multiselect=True, button_name='Forget')

# if paths are selected, rebuild the list of paths
if selectPaths:
    
    kept_paths = []
    
    # then rewrite them to new csv contents
    for r in range(0,row_count):
        if link_alias[r] not in selectPaths:
            kept_paths.append(link_alias[r] + "~" + link_path[r])
    
    # try to rewrite the file (should usually work)
    try:
        with open(myLinks,"w") as file:
            for path in kept_paths:
                file.writelines(path + "\n")
        
        # count the rows that were removed
        rem_rows = row_count - len(kept_paths)
        # display the outcome to the user
        forms.alert(str(rem_rows) + ' path(s) forgotten.', title='Script finished', warn_icon=False)
    # if the file could not be rewritten
    except:
        # display the outcome to the user
        forms.alert('Links file in unwritable state/location.', title='Script cancelled')
    
else:
    forms.alert('No links forgotten.', title='Script cancelled', warn_icon=False)