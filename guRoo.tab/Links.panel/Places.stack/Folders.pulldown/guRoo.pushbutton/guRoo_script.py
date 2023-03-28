# import libraries
import clr
import os
from pyrevit import script

# Get and build the pyrevit path
curPath = script.get_script_path()
remPath = curPath.split('Panel.extension')[0]

# Load the path
try:
	os.startfile(remPath)
except:
	pass