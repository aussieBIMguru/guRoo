# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit,DB
from Autodesk.Revit.DB import Transaction

# import list library
from System import Type
from System.Collections.Generic import List

# get document
doc = revit.doc
curview = revit.active_view

# get warnings
doc_warnings = doc.GetWarnings()

# get warning descriptions
des_warnings = []

for w in doc_warnings:
    des = w.GetDescriptionText().ToString()
    if len(des)>75:
        slc = des[0:75]+"..."
    else:
        slc = des
    des_warnings.append(slc)

set_warnings = set(des_warnings)

# user selects warning to isolate
sel_warning = forms.SelectFromList.show(set_warnings, button_name='Select warning type to isolate')

# run the process if a warning type is selected
if sel_warning:
    
    # empty objects to add to
    list_ids = List[DB.ElementId]()
    count_ids = []
    count_warnings = 0

    # for each warning get its ids
    for w,d in zip(doc_warnings,des_warnings):
        if d == sel_warning:
            count_warnings += 1
            for id in w.GetFailingElements():
                list_ids.Add(id)
                count_ids.append(id)
    
    # start a transaction
    t = Transaction(doc, "Isolate elements in view")
    t.Start()
    # isolate elements in ilist
    curview.IsolateElementsTemporary(list_ids)
    # finish a transaction
    t.Commit()
    
    # display end user message
    set_ids = set(count_ids)
    message = str(count_warnings) + " warnings involving " + str(len(set_ids)) + " elements isolated in view."
    forms.alert(message)