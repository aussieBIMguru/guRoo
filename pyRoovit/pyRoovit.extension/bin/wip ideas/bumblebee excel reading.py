# Copyright(c) 2016, David Mans, Konrad Sobon
# @arch_laboratory, http://archi-lab.net, http://neoarchaic.net

# import basic libraries
import clr
import System

# import excel for reading
clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel
System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

#from os import path
#bb_path = "C:\\Users\\Gavin\\AppData\\Roaming\\Dynamo\\Dynamo Revit\\2.3\\packages\\BumbleBee\\extra\\"
#sys.path.append(bb_path)
#import bumblebee as bb

# sets up Excel to run not in live mode
def SetUp(xlApp):
	# supress updates and warning pop ups
	xlApp.Visible = False
	xlApp.DisplayAlerts = False
	xlApp.ScreenUpdating = False
	return xlApp

# read excel data of a worksheet
def ReadData(ws, origin, extent, byColumn):

	rng = ws.Range[origin, extent].Value2
	if not byColumn:
		dataOut = [[] for i in range(rng.GetUpperBound(0))]
		for i in range(rng.GetLowerBound(0)-1, rng.GetUpperBound(0), 1):
			for j in range(rng.GetLowerBound(1)-1, rng.GetUpperBound(1), 1):
				dataOut[i].append(rng[i,j])
		return dataOut
	else:
		dataOut = [[] for i in range(rng.GetUpperBound(1))]
		for i in range(rng.GetLowerBound(1)-1, rng.GetUpperBound(1), 1):
			for j in range(rng.GetLowerBound(0)-1, rng.GetUpperBound(0), 1):
				dataOut[i].append(rng[j,i])
		return dataOut

# exit excel once worksheet is read
def ExitExcel(xlApp, wb, ws):
	# clean up before exiting excel, if any COM object remains
	# unreleased then excel crashes on open following time
	def CleanUp(_list):
		if isinstance(_list, list):
			for i in _list:
				Marshal.ReleaseComObject(i)
		else:
			Marshal.ReleaseComObject(_list)
		return None
		
	xlApp.ActiveWorkbook.Close(False)
	xlApp.ScreenUpdating = True
	CleanUp([ws,wb,xlApp])
	return None

# inputs
filePath = IN[0]
sheetName = IN[1]
byColumn = IN[2]

# try to get Excel data
try:
	xlApp = SetUp(Excel.ApplicationClass())
	xlApp.Workbooks.open(unicode(filePath))
	wb = xlApp.ActiveWorkbook
	ws = xlApp.Sheets(sheetName)
	originGot = ws.Cells(ws.UsedRange.Row, ws.UsedRange.Column)
	extentGot = ws.Cells(ws.UsedRange.Rows(ws.UsedRange.Rows.Count).Row, ws.UsedRange.Columns(ws.UsedRange.Columns.Count).Column)
	dataOut = ReadData(ws, originGot, extentGot, byColumn)
	ExitExcel(xlApp, wb, ws)
except:
	dataOut = None

# return result
OUT = dataOut