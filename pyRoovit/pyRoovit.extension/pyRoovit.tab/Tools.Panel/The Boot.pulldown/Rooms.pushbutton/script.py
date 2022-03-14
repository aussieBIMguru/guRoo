# import libraries
import clr
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB, UI
from pyrevit import script

# get document
doc = revit.doc

# get all rooms in document
rooms = DB.FilteredElementCollector(revit.doc)\
        .OfCategory(DB.BuiltInCategory.OST_Rooms)

# make spatial boundary calculator
calculator = DB.SpatialElementGeometryCalculator(doc)
options = DB.SpatialElementBoundaryOptions()
boundloc = DB.AreaVolumeSettings.GetAreaVolumeSettings(doc).GetSpatialElementBoundaryLocation(DB.SpatialElementType.Room)
options.SpatialElementBoundaryLocation = boundloc

# build lists to append to
roomsInvalid,roomState = [],[]

# verify room states
for r in rooms:
    if r.Area == 0:
        # room is identified as invalid
        roomsInvalid.append(r)
        # if it has a boundary
        segments = r.GetBoundarySegments(options)
        if len(segments) > 0:
            state = 'Redundant'
            roomState.append('Redundant')
        # if it has no location
        elif r.Location == None:
            state = 'Unplaced'
            roomState.append('Unplaced')
        # otherwise it is unenclosed
        else:
            state = 'Unenclosed'
            roomState.append('Unenclosed')

# display message if no views found
if not roomsInvalid:
    forms.alert("No invalid rooms found.", title= "Script complete", warn_icon=False)
    script.exit()
# otherwise proceed to select options
else:
    invalidOptions = \
        forms.SelectFromList.show(
            list(set(roomState)),
            title = 'Which states would you like to review?',
            width = 500,
            button_name = 'Next',
            multiselect = True
            )

# display message if no options provided
if not invalidOptions:
    forms.alert("No states selected.", title= "Script complete")
    script.exit()
# otherwise proceed to construct list of invalid rooms of those states
else:
    roomsInvalid2, roomDescriptors = [],[]
    for r,s in zip(roomsInvalid,roomState):
        if s in invalidOptions:
            roomsInvalid2.append(r)
            roomName = r.LookupParameter('Name').AsString()
            roomDescriptors.append(r.Number + ' : ' + roomName + ' [' + str(r.Id) + '] (' + s + ')')
    # display message if rooms available for those states
    if len(roomsInvalid2) == 0:
        forms.alert("No invalid rooms found.", title= "Script complete")
        script.exit()

# display primary UI if rooms are available
selectRooms = \
    forms.SelectFromList.show(
    roomDescriptors,
    title = 'Which rooms would you like to delete?',
    width = 500,
    button_name = 'Delete',
    multiselect = True
    )

# display message if no rooms provided
if not selectRooms:
    forms.alert("No rooms selected.", title= "Script complete")
    script.exit()
# otherwise proceed to try to delete those rooms
else:
    with revit.Transaction('Delete rooms'):
        # generate counters and total
        countTotal = len(selectRooms)
        countDelete = 0
        # if its description was selected, try to delete it
        for r,s in zip(roomsInvalid2,roomDescriptors):
            if s in selectRooms:
                try:
                    revit.doc.Delete(r.Id)
                    countDelete += 1
                except:
                    continue
    # construct final message and display results
    form_message = str(countDelete) + '/' + str(countTotal) + " Rooms successfully deleted."
    forms.alert(form_message, title= "Script complete", warn_icon=False)