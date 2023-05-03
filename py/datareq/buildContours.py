'''
Geoprocessing Tool which builds contour lines from an input DEM
The steps follow TWM Geo's standard method for outputting z-enabled contour lines that open correctly in CAD software
'''

import arcpy
import os

def buildContours(inputDEM, outDir, outFilename, contourInterval, srs):
    # Run Focal Statistics function
    arcpy.AddMessage("Running Focal Statistics with cell size of 5...")
    arcpy.SetProgressor("default", f"Running Focal Statistics with cell size of 5")
    rasterFocalStats = arcpy.ia.FocalStatistics(inputDEM, "Rectangle 5 5 CELL", "MEAN", "DATA", 90);

    # Get SR of raster
    sr = arcpy.Raster(rasterFocalStats).getRasterInfo().getSpatialReference()
    # Get Units
    units = sr.linearUnitName
    arcpy.AddMessage(f"Linear Units of Raster: {units}")

    # Convert Units if necessary
    if units == "Meter":
        arcpy.AddMessage("Raster units are in meters, converting to feet...")
        arcpy.SetProgressor("default", f"Converting units to feet")
        rasterFt = arcpy.ia.UnitConversion(rasterFocalStats, "Meters", "Feet")
    elif units == "Foot" or units == "Foot_US":
        arcpy.AddMessage("Raster units are in feet...")
        rasterFt = rasterFocalStats
    else:
        arcpy.AddError("Raster units are not in meters or feet!")

    # Build Contours
    arcpy.AddMessage("Creating z-enabled contours...")
    arcpy.SetProgressor("default", f"Creating z-enabled contours...")
    arcpy.env.outputCoordinateSystem = srs
    arcpy.env.outputZFlag = "Enabled"
    savefile = os.path.join(outDir, outFilename)
    arcpy.ddd.Contour(rasterFt, savefile, int(contourInterval), 0, 1, "CONTOUR", None)

    # Add Contours to Map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprx.activeMap.addDataFromPath(savefile)
    arcpy.AddMessage("Contours added to map")


    arcpy.AddMessage("Success!")


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputDEM = arcpy.GetParameterAsText(0)
    outDir = arcpy.GetParameterAsText(1)
    outFilename = arcpy.GetParameterAsText(2)
    contourInterval = arcpy.GetParameterAsText(3)
    srs = arcpy.GetParameterAsText(4)

    buildContours(inputDEM, outDir, outFilename, contourInterval, srs)
