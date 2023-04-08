# -*- coding: UTF-8 -*-

# import Excel dependent libraries
import clr
import System
from System import Array
from System.Collections.Generic import *

clr.AddReference('System.Drawing')
import System.Drawing
from System.Drawing import *

# Try and get specific interop, if not just the general one
try:
	clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
except:
	clr.AddReference('Microsoft.Office.Interop.Excel')

from Microsoft.Office.Interop import Excel
from System.Runtime.InteropServices import Marshal

# Force int or string
def xclUtils_strFix(s):
	try:
		fix = str(int(s))
	except:
		fix = str(s)
	return fix

# Excel utility class
# Thanks Cyril Poupin for most of this code with some tweaks...
class xclUtils():
	
	def __init__(self, lstData, filepath):
		self.lstData = lstData
		self.filepath = filepath

	# Define import function
	def xclUtils_import(self,wsName,col=0,row=0):
			
			# Open Excel file
			ex = Excel.ApplicationClass()
			ex.Visible = False
			workbook = ex.Workbooks.Open(self.filepath)
			
			# Try to get the worksheet, if not pass
			try:
				ws = ex.Sheets(wsName)
				wsFound = True
			except:
				wsFound = False
			
			# If worksheet is found
			if wsFound:
				# Have row and column been specified
				if col == 0:
					colCountF = ws.UsedRange.Columns.Count
				else:
					colCountF = col
				if row == 0:
					rowCountF = ws.UsedRange.Rows.Count
				else:
					rowCountF = row
				# Get data range
				self.fullrange = ws.Range[ws.Cells(1, 1), ws.Cells(rowCountF, colCountF)]
				self.fullvalue = list(self.fullrange.Value2)
				# Split data into sublists
				n = colCountF
				dataOut = list(self.fullvalue [i:i+n] for i in range(0, len(self.fullvalue ), n))
			
			# If worksheet is not found
			else:
				dataOut = []
			
			# close Excel
			ex.Workbooks.Close()
			ex.Quit()
			
			if workbook is not None:
				Marshal.ReleaseComObject(workbook)
			if ex is not None:
				Marshal.ReleaseComObject(ex)
				workbook = None
			ex = None
			
			return [dataOut, wsFound]