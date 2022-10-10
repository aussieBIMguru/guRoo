# import libraries
import clr
import os

# Get and build the pyrevit path
userProfile = os.environ.get("USERPROFILE")
tryPath = "C:\\Program Files\\pyRevit-Master\\"
prvPath = userProfile + '\\AppData\\Roaming\\pyRevit-Master\\'

# Load the path
try:
    os.startfile(prvPath)
except:
    os.startfile(tryPath)