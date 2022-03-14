# import libraries
import clr
import os

# Get and build the pyrevit path
userProfile = os.environ.get("USERPROFILE")
prvPath = userProfile + '\\AppData\\Roaming\\pyRevit-Master\\'

# Load the path
try:
    os.startfile(prvPath)
except:
    print('The path was not found.')