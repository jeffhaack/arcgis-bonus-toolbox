'''
Geoprocessing Tool which builds clips and exports a single raster
Additional options provided based on past projects
'''

import arcpy
import os
from osgeo import gdal
from exportRaster import exportRaster

def clipRaster(inputRaster, inputGeometry, bNoDataToWhite, bBlackPixelsToWhite, bBuildPyramids, outputFormat, outFile):
    
    # Clip Raster; if bNoDataToWhite, set nodata as 255 (try this with clip and Con)
    arcpy.SetProgressor("default", f"Clipping Raster...")
    arcpy.AddMessage("Clipping Raster...")
    clippedRasterFile = os.path.join(arcpy.env.scratchFolder, "clipped_raster.tif")
    arcpy.env.compression = "LZW"
    arcpy.management.Clip(inputRaster, "", clippedRasterFile, inputGeometry, "255", "ClippingGeometry", "NO_MAINTAIN_EXTENT")

    # if bNoDataToWhite, GDAL remove nodata
    if bNoDataToWhite:
        arcpy.SetProgressor("default", f"Converting no data to white...")
        arcpy.AddMessage("Converting no data to white...")
        # Use GDAL to remove the no data from the TIF, so that it shows as white
        gdalRasterFile = os.path.join(arcpy.env.scratchFolder, "gdal_raster.tif")
        gFile = gdal.Open(clippedRasterFile)
        gdal.Translate(gdalRasterFile, gFile, format="GTiff", noData="none", creationOptions=["COMPRESS=LZW"])
        gFile = None    # Close dataset (important)
    else:
        gdalRasterFile = clippedRasterFile

    # if bBlackPixelsToWhite, run Con tool to change values
    if bBlackPixelsToWhite:
        arcpy.SetProgressor("default", f"Converting black pixels to white...")
        arcpy.AddMessage("Converting black pixels to white...")
        b2wRasterFile = os.path.join(arcpy.env.scratchFolder, "b2w_raster.tif")        
        conRaster = arcpy.ia.Con(gdalRasterFile, 255, gdalRasterFile, "VALUE = 0")
        conRaster.save(b2wRasterFile)
    else:
        b2wRasterFile = gdalRasterFile

    # call exportRaster to save (also will add to current map)
    arcpy.SetProgressor("default", f"Saving {outFile}")
    arcpy.AddMessage(f"Saving {outFile}")
    exportRaster(b2wRasterFile, bBuildPyramids, outputFormat, outFile)


    # remove temp files
    arcpy.management.Delete(b2wRasterFile)
    arcpy.management.Delete(gdalRasterFile)
    arcpy.management.Delete(clippedRasterFile)


    arcpy.AddMessage("Success!")


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputRaster = arcpy.GetParameterAsText(0)
    inputGeometry = arcpy.GetParameterAsText(1)
    bNoDataToWhite = arcpy.GetParameter(2)
    bBlackPixelsToWhite = arcpy.GetParameter(3)
    bBuildPyramids = arcpy.GetParameter(4)
    outputFormat = arcpy.GetParameterAsText(5)
    outFile = arcpy.GetParameterAsText(6)
    
    clipRaster(inputRaster, inputGeometry, bNoDataToWhite, bBlackPixelsToWhite, bBuildPyramids, outputFormat, outFile)
