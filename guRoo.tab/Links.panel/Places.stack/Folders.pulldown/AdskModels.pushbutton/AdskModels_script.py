# import libraries
import clr
import os
# import pyrevit libraries
from pyrevit import revit, HOST_APP

# get document
ver = HOST_APP.version

# Get and build the pyrevit path
runPath = 'C:\Program Files\Autodesk\\Revit ' + ver + '\\Samples\\'

# Load the path
try:
	os.startfile(runPath)
except:
	pass