# import pyrevit libraries
from pyrevit import forms,revit,DB,script
from System.Collections.Generic import List

# Revit doc and UIdoc
doc = revit.doc
curview = revit.active_view

# get selection
selection = revit.get_selection()

# function to make filter
def create_filter(param,value):
	f_param = DB.ParameterValueProvider(DB.ElementId(param))
	f_value = value
	f_rule  = DB.FilterElementIdRule(f_param,DB.FilterNumericEquals(),f_value)
	f_eleid = DB.ElementParameterFilter(f_rule)
	return f_eleid

# Construct element filters
bip = DB.BuiltInParameter.ELEM_CATEGORY_PARAM
filters = List[DB.ElementFilter]()

for s in selection:
	f = create_filter(bip,s.Category.Id)
	filters.Add(f)

if filters:
	filter_mult = DB.LogicalOrFilter(filters)
	col = DB.FilteredElementCollector(doc,curview.Id).WherePasses(filter_mult).WhereElementIsNotElementType().ToElements()
	
	# Select objects
	all_type = [e.Id for e in col]
	
	# Make selection again
	selection.set_to(all_type)