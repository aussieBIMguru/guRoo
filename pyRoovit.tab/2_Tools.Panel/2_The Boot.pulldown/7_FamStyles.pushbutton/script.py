# preImport
from pyrevit import revit, DB, script, forms

# create custom message class
class StyleToRemove(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.Category.Name + self.item.Name

# Store current document into variable
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Get all family styles
allLpats = DB.FilteredElementCollector(doc).OfClass(DB.LinePatternElement).ToElements()
allFpats = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement).ToElements()
allMats = DB.FilteredElementCollector(doc).OfClass(DB.Material).ToElements()
allSubs = doc.OwnerFamily.FamilyCategory.SubCategories

allStyles, styleNames = [],[]

# Convert all fill patterns to list items
for f in allFpats:
    styleNames.append("Fill Pattern: " + f.Name)
    allStyles.append(f)

# Convert all line patterns to list items
for l in allLpats:
    styleNames.append("Line Pattern: " + l.Name)
    allStyles.append(l)

# Convert all materials to list items
for m in allMats:
    styleNames.append("Material: " + m.Name)
    allStyles.append(m)

# Convert all styles to list items
for s in allSubs:
    styleNames.append("Object style: " + s.Name)
    allStyles.append(s)

# Make sure styles are present for deletion
if len(allStyles)<1:
    forms.alert('No styles found.', title='Script cancelled')
    script.exit()
else:
    pass

# ask user for styles to delete
return_options = \
    forms.SelectFromList.show(
    styleNames,
    title='Select styles to remove',
    width=500,
    button_name='Delete styles',
    multiselect=True
    )

# if styles found try to delete them
if not return_options:
    forms.alert("No styles selected", title= "Script cancelled")
else:
    with forms.ProgressBar(step=1, title="Deleting styles") as pb:
        pbCount = 0
        pbTotal = len(return_options)
        styLen = str(pbTotal)
        styCnt = 0
        with revit.Transaction('Delete styles'):
            for n,s in zip(styleNames,allStyles):
                if n in return_options:
                    try:
                        doc.Delete(s.Id)
                        styCnt += 1
                    except:
                        pass
                # Update progress bar
                pb.update_progress(pbCount, pbTotal)
                pbCount += 1
                
        styRatio = str(styCnt) + "/" + styLen
        forms.alert(styRatio + " Family styles deleted.", "Script completed", warn_icon=False)