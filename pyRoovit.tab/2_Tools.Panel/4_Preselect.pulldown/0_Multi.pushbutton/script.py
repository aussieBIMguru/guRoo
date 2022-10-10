# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
from Autodesk.Revit.UI.Selection import *

# Revit doc and UIdoc
doc = revit.doc
uidoc = revit.uidoc

# Custom selection filter class
class CustomISelectionFilter(ISelectionFilter):
    def __init__(self, nom_category):
        self.nom_category = nom_category
    def AllowElement(self, e):
        if e.Category.Name in self.nom_category:
            return True
        else:
            return False

# List of options
catOptions = ["Areas","Casework","Ceilings","Doors","Floors","Furniture","Generic Models","Plumbing Fixtures","Roofs","Specialty Equipment","Walls","Windows"]

# Message for selection
selmsg = forms.SelectFromList.show(catOptions, title= "Select categories", width=500, button_name = "Choose categories", multiselect = True)

# Proceed if message accepted
if selmsg:
    try:
        selFil = CustomISelectionFilter(selmsg)
        sel = uidoc.Selection.PickObjects(ObjectType.Element,selFil,"Select elements")
    except:
        pass
else:
    forms.alert("Script cancelled", title= "Cancelled", warn_icon=False)
    script.exit()

# Libraries for selection
import System
from System.Collections.Generic import List

# Empty ID list
elementIds = List[DB.ElementId]()

# Try to get elements for selection
for s in sel:
	try:
		id = s.ElementId
		el = doc.GetElement(id)
		elementIds.Add(id)
	except:
		pass

# Select the elements
try:
    uidoc.Selection.SetElementIds(elementIds)
except:
    script.exit()