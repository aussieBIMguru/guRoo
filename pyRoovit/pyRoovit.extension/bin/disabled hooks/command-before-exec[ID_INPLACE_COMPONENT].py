# import libraries
from pyrevit import EXEC_PARAMS
from pyrevit import forms

# prevent the tool, await input
mip = forms.alert("No modelling in place!", options = ["Oops, my bad...", "But you see, I am an artiste"], title = "Not going to happen", footer = "Uhoh")

# process the outcome
if mip == "Oops, my bad...":
    # if they concede
    EXEC_PARAMS.event_args.Cancel = True
elif mip == "But you see, I am an artiste":
    # if they challenge the command
    pw = forms.GetValueWindow.show('Input password', title='Input password', width=500, height=600, default="")
    if pw != "Interior designer":
        # if they get it right
        EXEC_PARAMS.event_args.Cancel = True
    else:
        # if they don't
        EXEC_PARAMS.event_args.Cancel = False
else:
    # cancelling the command
    EXEC_PARAMS.event_args.Cancel = True