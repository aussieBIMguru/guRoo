# import pyrevit libraries
from pyrevit import revit, DB, forms, script

# import libraries
import os
import xlsxwriter
from datetime import datetime

# Store current document into variable
doc = revit.doc

# Retrieve data from the schedule
sched = revit.active_view

try:
	tableData = sched.GetTableData()
	sectionData = tableData.GetSectionData(DB.SectionType.Body)
	numbRows = sectionData.NumberOfRows
	numbCols = sectionData.NumberOfColumns
except:
	forms.alert("No data in table to export.", title= "Script cancelled")
	script.exit()

# Retrieve date
now = datetime.now()
date = now.strftime("%y%m%d")

# Retrieve project number
projNumber = doc.ProjectInformation.Number
if projNumber == "":
	projNumber = "PRJ"

# Select folder to export excel
destinationFolder = forms.pick_folder()

# stop script if no folder
if not destinationFolder:
	script.exit()

# Create list with schedule data with rows as second level lists
data = []

for i in range(numbRows):
	rows = []
	for j in range(numbCols):
		content = sched.GetCellText(DB.SectionType.Body, i, j)
		rows.append(content)
	data.append(rows)

# Check maximun length of data in columns
lengths = [len(x) for x in data[0]]
for row in data:
	for cell, lng in zip(row, lengths):
		newLength = len(cell)
		if newLength > lng:
			ind = lengths.index(lng)
			lengths[ind] = newLength

# Export data to excel
if len(sched.Name)<30:
	worksheetName = sched.Name
else:
	worksheetName = sched.Name[:29]

filePath = destinationFolder + "\\" + date + "_" + projNumber + "_" + sched.Name + ".xlsx"
workbook = xlsxwriter.Workbook(filePath, {'strings_to_numbers': True})
worksheet = workbook.add_worksheet(worksheetName)

# Define format for cells
fontSize = 12
fillColor = "cyan"
widthFactor = 1.5
titleFormat = workbook.add_format({"bold": True, "font_size": fontSize})
subtitleFormat = workbook.add_format({"bg_color": fillColor, "bold": True, 'font_color': "white", "font_size": fontSize})
cellFormat = workbook.add_format({"font_size": fontSize, 'align': "left"})

# Set columns width
for le, i in zip(lengths, range(len(lengths))):
	worksheet.set_column(i, i, le * widthFactor)

# Start from the first cell. Rows and columns are zero indexed.
row = 1
col = 0

# Set title of schedule
worksheet.write(0, 0, sched.Name.upper(), titleFormat)

# Iterate over the data and write it out row by row.
for item in data:
	first, rest = item[0], item[1:]
	for it in item:
		if (first != "" and rest.count("") == len(lengths)-1) or item.count("") == len(lengths):
			worksheet.write(row, col, it, subtitleFormat)
		elif row == 1:
			worksheet.write(row, col, it, titleFormat)
		else:
			worksheet.write(row, col, it, cellFormat)
		col += 1
	row += 1
	col = 0

workbook.close()

# Return outcome to user
forms.alert("Schedule export complete.", title= "Script complete", warn_icon=False)