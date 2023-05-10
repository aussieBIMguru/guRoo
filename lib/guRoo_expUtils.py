# Prepare for utilities
from pyrevit import revit,DB,forms,script
from System.Collections.Generic import List
import os, datetime

# get print directory
def expUtils_getDir():
	dp = os.path.expanduser("\\guRoo Exports")
	return dp

# make subfolder extension
def expUtils_getFolder(task = "_PDF"):
	dateStamp = datetime.datetime.today().strftime("%y%m%d")
	timeStamp = datetime.datetime.today().strftime("%H%M%S")
	return dateStamp + "_" + timeStamp + task

# make directory if it doesn't exist
def expUtils_ensureDir(dp):
	if not os.path.exists(dp):
		os.makedirs(dp)
	return dp

# open the directory
def expUtils_openDir(dp):
	try:
		os.startfile(dp)
	except:
		pass
	return dp

# function for checking version
def expUtils_canPrint():
	app = __revit__.Application
	rvt_year = int(app.VersionNumber)
	# Check that version is 2022 or higher
	if rvt_year < 2022:
		forms.alert("Only available in Revit 2022 or later.", title= "Script cancelled")
		script.exit()
	else:
		return True

# make sheet name for print
def expUtils_nameSheet(s):
	# Get revision number
	try:
		curRev = s.GetCurrentRevision()
		curNum = s.GetRevisionNumberOnSheet(curRev)
	except:
		curNum = "-"
	# get string utility
	from guRoo_strUtils import *
	# make sheet name
	preName = s.SheetNumber + "[" + curNum + "] -" + s.Name
	shtName = strUtils_legalize(preName)
	return shtName

# make view name for print
def expUtils_nameView(v):
	# get string utility
	from guRoo_strUtils import *
	# make sheet name
	preName = str(v.ViewType) + '_' + v.Name
	viewName = strUtils_legalize(preName)
	return viewName

# open a view/sheet
def expUtils_viewFocus(v,myDoc,myUiDoc):
	myUiDoc.RequestViewChange(v)
	curView  = myDoc.ActiveView
	allViews = myUiDoc.GetOpenUIViews()
	for v in allViews:
		if v.ViewId != curView.Id:
			try:
				v.Close()
			except:
				pass

# make pdf options
def expUtils_pdfOpts(hcb=False,hsb=True,hrp=True,hvt=True,mcl=True):
	opts = DB.PDFExportOptions()
	# Settings default
	opts.HideCropBoundaries = hcb
	opts.HideScopeBoxes = hsb
	opts.HideReferencePlane = hrp
	opts.HideUnreferencedViewTags = hvt
	opts.MaskCoincidentLines = mcl
	# Paper format
	opts.PaperFormat = DB.ExportPaperFormat.Default
	return opts

# make dwg options
def expUtils_dwgOpts(sc=False,mv=True):
	opts = DB.DWGExportOptions()
	# Settings default
	opts.SharedCoords = sc
	opts.MergedViews = mv
	return opts

# export a single sheet to pdf
def expUtils_exportSheetPdf(d,s,opt,myDoc,myUidoc):
	docName = expUtils_nameSheet(s)
	expUtils_viewFocus(s,myDoc,myUidoc)
	opt.FileName = docName
	# Prepare an Id list
	exportSheet = List[DB.ElementId]()
	exportSheet.Add(s.Id)
	# Export the sheet to PDF
	myDoc.Export(d, exportSheet, opt)
	return 1

# export a single sheet to dwg
def expUtils_exportSheetDwg(d,s,opt,myDoc,myUidoc):
	docName = expUtils_nameSheet(s)
	expUtils_viewFocus(s,myDoc,myUidoc)
	# Prepare an Id list
	exportSheet = List[DB.ElementId]()
	exportSheet.Add(s.Id)
	# Export the sheet to DWG
	myDoc.Export(d, docName, exportSheet, opt)
	return 1

# export a single view to dwg
def expUtils_exportViewDwg(d,v,opt,myDoc,myUidoc):
	docName = expUtils_nameView(v)
	expUtils_viewFocus(v,myDoc,myUidoc)
	# Prepare an Id list
	exportView = List[DB.ElementId]()
	exportView.Add(v.Id)
	# Export the sheet to DWG
	myDoc.Export(d, docName, exportView, opt)
	return 1

# export a single sheet to pdf and dwg
def expUtils_exportSheetPdfDwg(d,s,optPdf,optDwg,myDoc,myUidoc):
	docName = expUtils_nameSheet(s)
	expUtils_viewFocus(s,myDoc,myUidoc)
	optPdf.FileName = docName
	# Prepare an Id list
	exportSheet = List[DB.ElementId]()
	exportSheet.Add(s.Id)
	# Export the sheet to PDF
	myDoc.Export(d, exportSheet, optPdf)
	# Export the sheet to DWG
	myDoc.Export(d, docName, exportSheet, optDwg)
	return 1