# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms

# Display message
form_message = "Thanks for using guRoo, the BIM Guru toolbar to support our template and content!" + "\n\n" + "If you have queries or suggestions about these tools, reach out to us via our course and content support over on the platform."
forms.alert(form_message, title= "About guRoo", warn_icon=False)