# import libraries
import clr
import os
import csv
# import pyrevit libraries
from pyrevit import revit, forms, script

# get document
doc = revit.doc

# Get pouch folder path
current_path = os.path.realpath(__file__)
pouch_path = current_path.replace(r'pyRoovit.extension\pyRoovit.tab\About.Panel\Pouch.pulldown\1Open.pushbutton\script.py','')

# Make user pouch file path
userName    = os.environ.get("USERNAME")
myPouch     = pouch_path + "pouch_" + userName + ".csv"

# check if the file exists
if os.path.isfile(myPouch):
    with open(myPouch,"r") as file:
        reader = csv.reader(file,delimiter = "~")
        csv_data = list(reader)
        row_count = len(csv_data)
else:
    forms.alert('No pouch, make one by storing a path first.', title='Script cancelled')
    script.exit()

# check if there are rows, then write them to alias/path pairs
link_alias,link_path = [],[]

# try to deconstruct the csv list
if row_count > 0:
    for lst in csv_data:
        link_alias.append(lst[0])
        link_path.append(lst[1])
else:
    forms.alert('Pouch is empty.', title='Script cancelled')
    script.exit()

# ask the user to nominate paths for removal
selectPath = forms.SelectFromList.show(link_alias, 'Select link to open', 500, 800, multiselect=False, button_name='Open')

# if paths are selected, rebuild the list of paths
if selectPath:
    
    i = link_alias.index(selectPath)
    path = link_path[i] + "\\"
    
    # try to access the link
    try:
        os.startfile(path)
    except:
        # display the outcome to the user if link not found
        forms.alert('Path does not exist, try removing and remaking it.', title='Script cancelled')
    
else:
    forms.alert('No path chosen.', title='Script cancelled')