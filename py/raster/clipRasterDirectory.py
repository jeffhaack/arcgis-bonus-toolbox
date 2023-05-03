'''
Geoprocessing Tool which builds clips and exports a single raster
Additional options provided based on past projects
'''

import arcpy
import os
from osgeo import gdal
from clipRaster import clipRaster

def clipRasterDirectory(inputDirectory, inputGeometry, bNoDataToWhite, bBlackPixelsToWhite, bBuildPyramids, outputFormat, outputDirectory):
    # Get list of rasters in inputDirectory
    arcpy.env.workspace = inputDirectory
    rasters = arcpy.ListRasters("*", "All")
    rasterCount = len(rasters)
    arcpy.AddMessage(f"Found {rasterCount} rasters in {inputDirectory}")
    
    # Make output directory if it does not exist
    if not os.path.exists(outputDirectory):
        arcpy.AddMessage(f"Creating {outputDirectory}")
        os.mkdir(outputDirectory)

    i = 1
    for raster in rasters:
        arcpy.SetProgressor("default", f"{i}/{rasterCount}: Clipping {raster}")
        arcpy.AddMessage(f"{i}/{rasterCount}: Clipping {raster}")

        rInPath = os.path.join(inputDirectory, raster)
        rOutPath = os.path.join(outputDirectory, raster)

        clipRaster(rInPath, inputGeometry, bNoDataToWhite, bBlackPixelsToWhite, bBuildPyramids, outputFormat, rOutPath)
        i += 1


    arcpy.AddMessage("Success!")
    


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputDirectory = arcpy.GetParameterAsText(0)
    inputGeometry = arcpy.GetParameterAsText(1)
    bNoDataToWhite = arcpy.GetParameter(2)
    bBlackPixelsToWhite = arcpy.GetParameter(3)
    bBuildPyramids = arcpy.GetParameter(4)
    outputFormat = arcpy.GetParameterAsText(5)
    outputDirectory = arcpy.GetParameterAsText(6)
    
    clipRasterDirectory(inputDirectory, inputGeometry, bNoDataToWhite, bBlackPixelsToWhite, bBuildPyramids, outputFormat, outputDirectory)
