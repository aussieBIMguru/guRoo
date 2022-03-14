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
pouch_path = current_path.replace(r'pyRoovit.extension\pyRoovit.tab\About.Panel\Pouch.pulldown\2Add.pushbutton\script.py','')

# Make user pouch file path
userName    = os.environ.get("USERNAME")
myPouch     = pouch_path + "pouch_" + userName + ".csv"

# get users mydocs
userProfile = os.environ.get("USERPROFILE")
userDesktop = userProfile + "\Desktop"

# UI for link nickname
sel_nickname = forms.GetValueWindow.show('Set nickname', title='SET A NICKNAME', width=500, height=600, default="")

# UI for link path
if sel_nickname and sel_nickname != "":
    sel_path = forms.GetValueWindow.show('Set folder path', title='SET FOLDER PATH', width=500, height=600, default="")
else:
    forms.alert('No nickname provided.', title='Script cancelled')
    script.exit()

# Make sure the file exists and make with 1 path if not
if sel_path and sel_path != "":
    #try reading the contents
    if os.path.isfile(myPouch):
        try:
            file = open(myPouch, mode='r')
            readLinks = file.read()
            file.close()
        except:
            forms.alert('Your pouch is in unreadable state/location.', title='Script cancelled')
            script.exit()
    #otherwise, try writing a new empty file
    else:
        try:
            with open(myPouch, "a") as file: 
                readLinks = "Desktop~" + userDesktop
                file.writelines(readLinks + "\n")
        # if that fails, assume the file exists but is empty
        except:
            forms.alert('Your pouch is in unwritable state/location.', title='Script cancelled')
            script.exit()
# if no path selected, cancel script     
else:
    forms.alert('No path provided.', title='Script cancelled')
    script.exit()
    
# test for nickname presence in existing paths
full_nickname = sel_nickname + "~"

# if nickname is valid, write the line to the file
if full_nickname != None and full_nickname not in readLinks:
    try:
        with open(myPouch, "a") as file:
            storeLink = sel_nickname + "~" + sel_path + "\n"
            file.writelines(storeLink)
        forms.alert('Path stored.', title='Script complete', warn_icon=False)
    except:
        forms.alert('Path was not able to be stored. Contact aussiebimguru@gmail.com for assistance if you like.', title='Script cancelled')
# if nickname exists, cancel the store
else:
    forms.alert('Nickname already exists.', title='Script cancelled')