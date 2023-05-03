import arcpy
from arcpy.sa import *
from osgeo import gdal
import os
from datetime import datetime


import gdal_merge as gm
inDir = r"C:\code\imageProcessingBenchmarkTests\sampleSubsetECW"
gm.main(['', '-o', r'C:\Scratch\merged.tif', '-of', 'GTiff', '-ot', 'Byte', os.path.join(inDir, r"*.ecw")])

exit()



# outDir = r"C:\code\imageProcessingBenchmarkTests"
inFile = r"C:\code\imageProcessingBenchmarkTests\imagery_2018.tif"

try:
    outFile = r"C:\code\imageProcessingBenchmarkTests\imagery_2018_con.tif"
    outCon = Con(IsNull(Raster(inFile)), 100, inFile)
    outCon.save(outFile) # saves as 16-bit for some reason

    # Another way to save, ie as 8-bit
    #arcpy.management.CopyRaster(outCon, outFile, '', None, "NONE", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", 'TIFF', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

    # Notes
    # So this Con tool is a big piece of crap, and rarely works as you expect it to
    # In theory the above command should convert all the NoData values in the raster to a value of 100
    # It does do this, but then when you save the file those values go back to being NoData
    # I've spent way too long on this so I'm finally giving up

    # Set Null also a useful tool for, ie. converting black values to nodata; but they are still
    # somehow thought of differently than original NoData; super annoying

    # Next ideas would be to use a Raster Calculator type function in either ArcGIS or GDAL
    # - Tried Raster Calculator in ArcGIS, same bullshit.

    # Links
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/raster-calculator.htm
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/con-.htm
    # https://resources.arcgis.com/en/help/main/10.2/index.html#//009z00000005000000

    
except:
    print("ERROR 1")
