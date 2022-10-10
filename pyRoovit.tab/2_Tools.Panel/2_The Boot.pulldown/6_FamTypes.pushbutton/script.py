# Import
from pyrevit import forms
from pyrevit import revit, DB, script

# create custom message class based on family types
class TypeToRemove(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.Name

# Store current document into variable
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Get all family types
famMan   = doc.FamilyManager
famTypes = famMan.Types
typeList = []

# Construct and reset forward iterator
typesetIterator = famTypes.ForwardIterator()
typesetIterator.Reset()

# Construct type list
while typesetIterator.MoveNext():
    typeList.append(typesetIterator.Current)

# Must be at least 2 types to delete
if len(typeList)<2:
    forms.alert("Not enough family types to delete.", title= "Types not deleted")
    script.exit()
else:
    # show user all the family types by name
    return_options = \
        forms.SelectFromList.show(
            [TypeToRemove(t)
            for t in typeList],
            title='Select types to remove',
            width=500,
            button_name='Remove types',
            multiselect=True
            )

# Remove family types if provided
if return_options:
    # try to remove all family types
    with forms.ProgressBar(step=1, title="Deleting types") as pb:
        
        pbCount = 0
        pbTotal = len(return_options)
        
        famLen = str(len(return_options))
        famCnt = 0
        with revit.Transaction('Delete types'):
            for r in return_options:
                try:
                    famMan.CurrentType = r
                    famMan.DeleteCurrentType()
                    famCnt+=1
                except:
                    # last type will fail if included
                    forms.alert("Cannot delete type: " + r.Name, "Last type reached")
                
                # Update progress bar
                pb.update_progress(pbCount, pbTotal)
                pbCount += 1
                
        # final message showing outcome
        famRatio = str(famCnt) + "/" + famLen
        forms.alert(famRatio + " Family types deleted.", "Script completed", warn_icon=False)
else:
    forms.alert("No types selected", title= "Script cancelled")