'''
Geoprocessing Tool which exports a single raster to a selection of output formats.
Option to output nodata pixels as white.
'''

import arcpy
from osgeo import gdal
import os
from datetime import datetime

def exportRaster(inputRaster, bNoDataToWhite, bBuildPyramids, outDir, outFilename, bExportTif, bExportJP2Max, bExportJP2Fast):
    arcpy.env.nodata = "255"
    
    # Load inputRaster as ArcGIS Raster object
    workingRaster = arcpy.Raster(inputRaster)

    # Remove extension if user put it on output file
    outFilenameNoExtension = os.path.splitext(outFilename)[0]

    # If bNoDataToWhite, convert no data pixels to white, using GDAL
    if bNoDataToWhite:
        # Convert NoData value to 255 & copy as 8-bit unsigned
        arcpy.env.compression = "LZ77"
        step01 = os.path.join(arcpy.env.scratchFolder, 'step01.tif')
        arcpy.management.CopyRaster(workingRaster, step01, '', None, "255", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", 'TIFF', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

        # Use GDAL to remove NoData from the TIF, so that it shows as white
        step02 = os.path.join(arcpy.env.scratchFolder, outFilenameNoExtension + '.tif')
        gFile = gdal.Open(step01)
        gdal.Translate(step02, gFile, format="GTiff", noData="none", creationOptions=["COMPRESS=LZW", "BIGTIFF=YES"])
        gFile = None    # Close dataset (important)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx.activeMap.addDataFromPath(step01)
        aprx.activeMap.addDataFromPath(step02)

    # Otherwise, just convert to 8-bit unsigned
    else:
        arcpy.env.compression = "LZ77"
        step02 = os.path.join(arcpy.env.scratchFolder, outFilenameNoExtension + '.tif')
        arcpy.management.CopyRaster(workingRaster, step02, '', None, "NONE", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", 'TIFF', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")


    

    # If bExportTif, Export LZ77 TIF
    if bExportTif:
        start = datetime.now()

        # Export as TIFF
        arcpy.env.compression = "LZ77"
        arcpy.conversion.RasterToOtherFormat(step02, outDir, "TIFF")

        # Get Exported File Path
        exportFile = os.path.join(outDir, outFilenameNoExtension + '.tif')

        # If bBuildPyramids... build pyramids
        if bBuildPyramids:
            arcpy.management.BuildPyramids(exportFile)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx.activeMap.addDataFromPath(exportFile)

        end = datetime.now()
        arcpy.AddMessage(f"Exported {exportFile} in {end - start}")

    # If bExportJP2Max, Export JP2 100% quality
    if bExportJP2Max:
        start = datetime.now()

        # Export as JP2
        arcpy.env.compression = "JPEG2000 100"
        arcpy.conversion.RasterToOtherFormat(step02, outDir, "JP2000")

        # Get Exported File Path
        exportFile = os.path.join(outDir, outFilenameNoExtension + '.jp2')

        # If bBuildPyramids... build pyramids
        if bBuildPyramids:
            arcpy.management.BuildPyramids(exportFile)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx.activeMap.addDataFromPath(exportFile)

        end = datetime.now()
        arcpy.AddMessage(f"Exported {exportFile} in {end - start}")

    # If bExportJP2Fast, Export JP2 from GDAL
    if bExportJP2Fast:
        start = datetime.now()

        # Set Export File Path (rename if ArcGIS JP2 was created with this name)
        if bExportJP2Max:
            exportFile = os.path.join(outDir, outFilenameNoExtension + '_gdal.jp2')
        else:
            exportFile = os.path.join(outDir, outFilenameNoExtension + '.jp2')

        # Process with GDAL
        gFile = gdal.Open(step02)
        # Note that JP2KAK is the only JP2 codec that works in ArcGIS GDAL module
        gdal.Translate(exportFile, gFile, format="JP2KAK", noData="none", creationOptions=["QUALITY=100"])
        gFile = None    # Close dataset (important)

        # If bBuildPyramids... build pyramids
        if bBuildPyramids:
            arcpy.management.BuildPyramids(exportFile)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx.activeMap.addDataFromPath(exportFile)

        end = datetime.now()
        arcpy.AddMessage(f"Exported {exportFile} in {end - start}")
    
    


    # Remove files created in arcpy.env.scratchFolder (they are not automatically deleted)
    arcpy.SetProgressor("default", "Removing temporary files...")
    arcpy.AddMessage("Removing temporary files...")
    # arcpy.management.Delete(step01)
    # arcpy.management.Delete(step02)


    arcpy.AddMessage("Success!")


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputRaster = arcpy.GetParameterAsText(0)
    bNoDataToWhite = arcpy.GetParameter(1)
    bBuildPyramids = arcpy.GetParameter(2)
    outDir = arcpy.GetParameterAsText(3)
    outFilename = arcpy.GetParameterAsText(4)
    bExportTif = arcpy.GetParameter(5)
    bExportJP2Max = arcpy.GetParameter(6)
    bExportJP2Fast = arcpy.GetParameter(7)

    exportRaster(inputRaster, bNoDataToWhite, bBuildPyramids, outDir, outFilename, bExportTif, bExportJP2Max, bExportJP2Fast)
