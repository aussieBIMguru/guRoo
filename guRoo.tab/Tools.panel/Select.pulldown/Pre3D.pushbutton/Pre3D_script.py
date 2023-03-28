# import pyrevit libraries
from pyrevit import forms,revit,DB,script
from Autodesk.Revit.UI.Selection import *

# Revit doc and UIdoc
doc = revit.doc
uidoc = revit.uidoc

# Custom selection filter class
class CustomISelectionFilter(ISelectionFilter):
	def __init__(self, view_specific):
		self.view_specific = view_specific
	def AllowElement(self, e):
		if not e.ViewSpecific:
			return True
		else:
			return False
	def AllowReference(self, ref, point):
		return true

# Message for selection
selmsg = True

# Proceed if message accepted
if selmsg:
	try:
		sel = uidoc.Selection.PickObjects(ObjectType.Element,CustomISelectionFilter("Non-view specific"),"Select elements")
	except:
		script.exit()
else:
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
	pass