# import libraries
import clr
import os

# Get and build the pyrevit path
userProfile = os.environ.get("USERPROFILE")
runPath = userProfile + '\\AppData\\Roaming\\Dynamo\\Dynamo Revit\\'

# Load the path
try:
    os.startfile(runPath)
except:
    pass