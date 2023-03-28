# import pyrevit libraries
from pyrevit import revit, DB

# get selection
selection = revit.get_selection()

# Reform selection
filtered_elements = []

for el in selection:
	if el.GroupId == DB.ElementId.InvalidElementId and not isinstance(el, DB.Group):
		filtered_elements.append(el.Id)

# Make selection again
selection.set_to(filtered_elements)