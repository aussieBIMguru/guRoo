# import libraries
import clr
import os
from os import listdir
import System
from System.IO import SearchOption
from System import Environment

# import pyrevit libraries
from pyrevit import forms,revit,DB

# get document
doc = revit.doc

# try to open document, or cache
try:
	curdoc = DB.Document.PathName.GetValue(doc)
	curdir = curdoc.rsplit('\\',1)
	os.startfile(curdir[0])
except:
	try:
		guid = doc.WorksharingCentralGUID
		AppDataList = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData).split("\\")
		AppDataList.pop(-1)
		AppData = "\\".join(AppDataList)
		location =  AppData + "\\Local\\Autodesk\\Revit"
		os.startfile(location)
	except:
		forms.alert('File could not be found.', title='Script completed')