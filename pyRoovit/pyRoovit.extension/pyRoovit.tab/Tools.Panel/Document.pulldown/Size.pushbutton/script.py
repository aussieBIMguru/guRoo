# import libraries
import clr
import os
from os import listdir
import System
from System.IO import SearchOption
from System import Environment
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit,DB

# get document
doc = revit.doc

# try to find file path
try:
    guid = doc.WorksharingCentralGUID
    AppDataList = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData).split("\\")
    AppDataList.pop(-1)
    AppData = "\\".join(AppDataList)
    location =  AppData + "\\Local\\Autodesk\\Revit"
    cashedFile = System.IO.Directory.GetFiles(location, str(guid) + ".rvt" ,SearchOption.AllDirectories)
    size = [os.path.getsize(file) for file in cashedFile][0]
    sizeString = str(size/1000000)+ " MB"
except:
    try:
        pn = doc.PathName
        size = os.path.getsize(pn)
        sizeString = str(size/1000000)+" MB"
    except:
        sizeString = "not readable."

# return the file path in a message
forms.alert("Model size is " + sizeString, title='File size', warn_icon=False)