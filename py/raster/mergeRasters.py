'''
Geoprocessing Tool which builds clips and exports a single raster
Additional options provided based on past projects
'''

import arcpy
import os
import gdal_merge as gm
from exportRaster import exportRaster


def mergeRasters(inputDirectory, bBuildPyramids, outputFormat, outputFile):
    # Get list of rasters in inputDirectory
    arcpy.env.workspace = inputDirectory
    rasters = arcpy.ListRasters("*", "All")
    rasterCount = len(rasters)

    # Get the extension and make sure they all have the same extension
    extension = os.path.splitext(rasters[0])[-1]
    for raster in rasters:
        if extension != os.path.splitext(raster)[-1]:
            arcpy.AddError(f"Multiple file formats found in input directory, cannot process!")
    arcpy.AddMessage(f"Found {rasterCount} rasters in {inputDirectory} with extension {extension}")
    arcpy.SetProgressor("default", f"Found {rasterCount} rasters with extension {extension}")
    
    # Merge rasters to TIFF with gdal_merge - it doesn't seem to work right to compress it
    mergedRasterFile = os.path.join(arcpy.env.scratchFolder, "merged_raster.tif")
    arcpy.AddMessage(f"Merging with GDAL...")
    arcpy.SetProgressor("default", f"Merging with GDAL")
    gm.main(['', '-o', mergedRasterFile, '-of', 'GTiff', '-ot', 'Byte', os.path.join(inputDirectory, rf"*{extension}")])

    # call exportRaster to save (also will add to current map)
    arcpy.SetProgressor("default", f"Saving {outputFile}")
    arcpy.AddMessage(f"Saving {outputFile}")
    exportRaster(mergedRasterFile, bBuildPyramids, outputFormat, outputFile)

    # remove temp files
    arcpy.management.Delete(mergedRasterFile)


    arcpy.AddMessage("Success!")
    


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputDirectory = arcpy.GetParameterAsText(0)
    bBuildPyramids = arcpy.GetParameter(1)
    outputFormat = arcpy.GetParameterAsText(2)
    outputFile = arcpy.GetParameterAsText(3)
    
    mergeRasters(inputDirectory, bBuildPyramids, outputFormat, outputFile)
