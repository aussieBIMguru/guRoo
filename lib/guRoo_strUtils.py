# Make a string legal
def strUtils_legalize(str):
	reps = ['/','?','<','>','\\',':','*','|','"','^']
	newStr = ""
	for char in str:
		if char in reps:
			pass
		else:
			newStr += char
	return newStr