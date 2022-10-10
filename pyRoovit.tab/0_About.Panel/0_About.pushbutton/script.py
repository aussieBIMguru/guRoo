# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms

# Display message
form_message = "Thanks for using pyRoovit!" + "\n\n" + "This is a small toolbar I've developed to help people learn more about pyRevit. I hope to update it from time to time, and if you have any issues or requests leave them on the github." + "\n\n" + "Thanks to Ehsan for this amazing app that allows us to make Python tools for Revit and much more!"
forms.alert(form_message, title= "About this panel", warn_icon=False)