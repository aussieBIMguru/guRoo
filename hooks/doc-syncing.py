# mute check
from pyrevit import script
from guRoo_msgUtils import *

# import libraries
from datetime import datetime

# get the time
time = datetime.now()
dt_f = time.strftime("%H-%M-%S")

# try to write data
try:
	script.store_data("Sync start", dt_f, this_project=True)
except:
	pass