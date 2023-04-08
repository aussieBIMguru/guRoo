# Import libraries
from pyrevit import revit, DB, script, forms

# Store current document into variable
doc = revit.doc

# Function to create sheets
def createSheet(number, name, titleBlockId):
	sheet = DB.ViewSheet.Create(doc, titleBlockId)
	sheet.SheetNumber = number
	sheet.Name = name
	return 1

# Prompt user to specify file path
pathFile = forms.pick_file(files_filter='Excel Workbook (*.xlsx)|*.xlsx|''Excel 97-2003 Workbook|*.xls')

# Catch if no file selected
if not pathFile:
	script.exit()

# Prompt user to select titleblock
titleBlock = forms.select_titleblocks(doc=doc)

# Catch if no titleblock selected
if not titleBlock:
	script.exit()

# Import excel data
from guRoo_xclUtils import *

xcl = xclUtils([],pathFile)
dat = xcl.xclUtils_import("Sheet1",2,0)

# Try to get column data
if dat[1]:
	sheetNumbers, sheetNames, sheetSeries, sheetSets = [],[],[],[]
	for row in dat[0][1:]:
		sheetNumbers.append(xclUtils_strFix(row[0]))
		sheetNames.append(xclUtils_strFix(row[1]))
else:
	forms.alert("Data not found. Make sure Excel is closed, and on Sheet1 as per the template.", title= "Script cancelled")
	script.exit()

# get all sheets in document
sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
sheetnums = [n.SheetNumber for n in sheets]

# Create sheets
with forms.ProgressBar(step=1, title="Creating sheets", cancellable=True) as pb:
	# Create progress bar
	pbCount = 1
	pbTotal = len(sheetNumbers)
	passCount = 0
	# Start transaction
	with revit.Transaction('guRoo: Create sheets'):
		# Make sheets
		for sNumb, sNam in zip(sheetNumbers, sheetNames):
			if pb.cancelled:
				break
			if sNumb not in sheetnums:
				passCount += createSheet(sNumb, sNam, titleBlock)
			# Update progress bar
			pb.update_progress(pbCount, pbTotal)
			pbCount += 1

# Process the outcome
if pb.cancelled:
	extraMsg = "\n\n" + "Script cancelled partway through run."
	warnIcon = False
elif passCount != pbTotal:
	extraMsg = "\n\n" + "Skipped sheets typically are caused by sheet numbers already existing in the model."
	warnIcon = True
else:
	extraMsg = ""
	warnIcon = False

# Display the outcome
form_message = str(passCount) + "/" + str(pbTotal) + " sheets created." + extraMsg
forms.alert(form_message, title= "Script complete", warn_icon=warnIcon)