# import libraries
import clr
import os
# import pyrevit libraries
from pyrevit import forms, script

# get users mydocs
userName    = os.environ.get("USERNAME")
userProfile = os.environ.get("USERPROFILE")
userDocs    = userProfile + '\\AppData\\Roaming\\pyRevit\\'
myLinks     = userDocs + "\\" "pouch_" + userName + ".csv"

# UI for link alias
sel_alias = forms.GetValueWindow.show('Set nickname', title='SET A NAME', width=500, height=600, default="")

# UI for link path
if sel_alias and sel_alias != "":
    sel_path = forms.GetValueWindow.show('Set full path', title='SET A PATH', width=500, height=600, default="")
else:
    forms.alert('No nickname provided.', title='Script cancelled')
    script.exit()

# Make sure the file exists and make with 1 path if not
if sel_path and sel_path != "":
    #try reading the contents
    if os.path.isfile(myLinks):
        try:
            file = open(myLinks, mode='r')
            readLinks = file.read()
            file.close()
        except:
            forms.alert('Pouch in unreadable state/location.', title='Script cancelled')
            script.exit()
    #otherwise, try writing a new empty file
    else:
        try:
            with open(myLinks, "a") as file: 
                readLinks = "pyRevit~" + userDocs
                file.writelines(readLinks + "\n")
        # if that fails, assume the file exists but is empty
        except:
            forms.alert('Links file in unwritable state/location.', title='Script cancelled')
            script.exit()
# if no path selected, cancel script     
else:
    forms.alert('No item provided.', title='Script cancelled')
    script.exit()
    
# test for alias presence in existing paths
full_alias = sel_alias + "~"

# if alias is valid, write the line to the file
if full_alias != None and full_alias not in readLinks:
    try:
        with open(myLinks, "a") as file:
            storeLink = sel_alias + "~" + sel_path + "\n"
            file.writelines(storeLink)
        forms.alert('Item added to pouch.', title='Script complete', warn_icon=False)
    except:
        forms.alert('Item was not able to be stored.', title='Script cancelled')
# if alias exists, cancel the store
else:
    forms.alert('Alias already exists.', title='Script cancelled')