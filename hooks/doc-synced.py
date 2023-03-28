# mute check
from pyrevit import script
from guRoo_msgUtils import *

# check if notifications are disabled
if msgUtils_muted():
	script.exit()

# import libraries
from pyrevit import forms
from datetime import datetime
import math

# get the time
time = datetime.now()
dt_f2 = time.strftime("%H-%M-%S")

# try to write data
# Get a datetime
dt_f1  = script.load_data("Sync start", this_project=True)

# Break down to parts
before = dt_f1.split("-")
after  = dt_f2.split("-")
msg    = ""

# Function to check for seconds
def getSeconds(lst):
	h = int(lst[0]) * 60 * 60
	m = int(lst[1]) * 60
	s = int(lst[2])
	return h+m+s

# Function to process time to string
def timeToString(s):
	unpad = str(s).split(".")[0]
	return unpad.rjust(2,"0")

# Get the seconds difference
try:
	elapsed = getSeconds(after) - getSeconds(before)
	e_mins  = math.floor(elapsed/60)
	e_secs  = elapsed % 60
	
	# Form user message
	msg_time = timeToString(e_mins) + "min " + timeToString(e_secs) + "sec"
	msg_title = "Sync completed"
	
	# Show toast message
	forms.toaster.send_toast(msg_time, title = msg_title, appid=None, icon=None, click=None, actions=None)
	
except:
	pass