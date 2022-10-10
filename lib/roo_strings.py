# Make a string legal
def legalize(str):
	reps = ['/','?','<','>','\\',':','*','|','"','^']
	newStr = ""
	for char in str:
		if char in reps:
			pass
		else:
			newStr += char
	return newStr