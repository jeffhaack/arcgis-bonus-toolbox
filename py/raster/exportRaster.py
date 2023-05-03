'''
Geoprocessing Tool which exports a single raster to a selection of output formats.
Option to output nodata pixels as white.
'''

import arcpy
from osgeo import gdal
import os
from datetime import datetime

def exportRaster(inputRaster, bBuildPyramids, outputFormat, outFile):
    # Measure speed
    start = datetime.now()

    arcpy.SetProgressor("default", f"Exporting to {outFile}...")
    arcpy.AddMessage(f"Exporting to {outFile}...")


    if outputFormat == "TIFF (LZ77 compression)":
        # Export as TIFF
        outDir = os.path.dirname(outFile)
        arcpy.env.compression = "LZ77"
        arcpy.conversion.RasterToOtherFormat(inputRaster, outDir, "TIFF")

        # Rename output file
        outFilePath = os.path.join(outDir, os.path.splitext(os.path.basename(inputRaster))[0] + '.tif')
        arcpy.management.Rename(outFilePath, outFile)


    if outputFormat == "JP2 (ArcGIS - Max Quality)":
        # Export as JP2
        outDir = os.path.dirname(outFile)
        arcpy.env.compression = "JPEG2000 100"
        arcpy.conversion.RasterToOtherFormat(inputRaster, outDir, "JP2000")

        # Rename output file
        outFilePath = os.path.join(outDir, os.path.splitext(os.path.basename(inputRaster))[0] + '.jp2')
        arcpy.management.Rename(outFilePath, outFile)


    if outputFormat == "JP2 (GDAL - Faster)":
        # Save to file so GDAL can work with it
        workingRaster = arcpy.Raster(inputRaster)
        workingRasterFile = os.path.join(arcpy.env.scratchFolder, "tempRaster.tif")
        workingRaster.save(workingRasterFile)

        # Process with GDAL
        gFile = gdal.Open(workingRasterFile)
        # Note that JP2KAK is the only JP2 codec that works in ArcGIS GDAL module
        gdal.Translate(outFile, gFile, format="JP2KAK", noData="none", creationOptions=["QUALITY=100"])
        gFile = None    # Close dataset (important)

        # Remove temp file
        arcpy.management.Delete(workingRasterFile)

    

    # If bBuildPyramids... build pyramids
    if bBuildPyramids:
        arcpy.management.BuildPyramids(outFile)

    # Add to Map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprx.activeMap.addDataFromPath(outFile)

    # End and message
    end = datetime.now()
    arcpy.AddMessage(f"Exported {outFile} in {end - start}")
    arcpy.AddMessage("Success!")


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputRaster = arcpy.GetParameterAsText(0)
    bBuildPyramids = arcpy.GetParameter(1)
    outputFormat = arcpy.GetParameterAsText(2)
    outFile = arcpy.GetParameterAsText(3)

    exportRaster(inputRaster, bBuildPyramids, outputFormat, outFile)
