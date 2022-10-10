# import libraries
from pyrevit import EXEC_PARAMS
from pyrevit import forms

# prevent the tool, await input
mip = forms.alert("This tool should be used sparingly, are you sure you need to use it?", options = ["Yes", "No"], title = "Modelling in place", footer = "pyRarch")

# process the outcome
if mip == "Yes":
    EXEC_PARAMS.event_args.Cancel = False
else:
    EXEC_PARAMS.event_args.Cancel = True