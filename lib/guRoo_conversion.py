# Prepare for converters
from pyrevit import revit,DB

# get document
doc = revit.doc
app = __revit__.Application
rvt_year = int(app.VersionNumber)

# Return internal unit type
def conversion_getUnits():
    # RVT < 2022
    if rvt_year < 2022:
        intUnits = doc.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
        return intUnits
    # RVT >= 2022
    else:
        intUnitsId = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
        return intUnitsId

# Convert project units to internal
def conversion_prjToInt(length):
    # RVT < 2022
    if rvt_year < 2022:
        intUnits = doc.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
        return DB.UnitUtils.Convert(length,intUnits,DB.DisplayUnitType.DUT_DECIMAL_FEET)
    # RVT >= 2022
    else:
        intUnitsId = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
        return DB.UnitUtils.ConvertToInternalUnits(length, intUnitsId)

# Convert project units from internal
def conversion_intToPrj(length):
    # RVT < 2022
    if rvt_year < 2022:
        intUnits = doc.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
        return DB.UnitUtils.Convert(length,DB.DisplayUnitType.DUT_DECIMAL_FEET,intUnits)
    # RVT >= 2022
    else:
        intUnitsId = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
        return DB.UnitUtils.ConvertFromInternalUnits(length, intUnitsId)