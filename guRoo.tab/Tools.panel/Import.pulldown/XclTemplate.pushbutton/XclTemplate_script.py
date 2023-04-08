# import libraries
import clr
import os
# import pyrevit libraries
from pyrevit import forms, script

# get bin path
curPath = script.get_script_path()
remPath = curPath.split('guRoo.tab')[0]
temPath = remPath + r'bin\Templates'

# Load the path
try:
	# Return outcome to user
	form_message = "1. Copy the Excel template to another location." + "\n" + "2. Populate with numbers/names." + "\n" + "3. Run the import sheets tool."
	checkForm = forms.alert(form_message, title= "Instructions", warn_icon=False)
except:
	print('The path was not found.')

# Open the path
if checkForm:
	os.startfile(temPath)