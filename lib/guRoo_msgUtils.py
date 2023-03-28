# import libraries
import clr
import os

# make path
def msgUtils_mutePath():
	# get path
	userName    = os.environ.get("USERNAME")
	userProfile = os.environ.get("USERPROFILE")
	userDocs    = userProfile + '\\AppData\\Roaming\\pyRevit\\'
	return userDocs + "\\" "guRoo_mute" + ".csv"

# check if path exists, return its state
def msgUtils_muted():
	# check if mute is on
	if os.path.isfile(msgUtils_mutePath()):
		return True
	else:
		return False

# turn off mute
def msgUtils_muteOff():
	mutePath = msgUtils_mutePath()
	if os.path.isfile(mutePath):
		os.remove(mutePath)
		return True
	else:
		return False

# turn on mute
def msgUtils_muteOn():
	mutePath = msgUtils_mutePath()
	if not os.path.isfile(mutePath):
		with open(mutePath, "a") as file:
			file.writelines("muted")
		return True
	else:
		return False