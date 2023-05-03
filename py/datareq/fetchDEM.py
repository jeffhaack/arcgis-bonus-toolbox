defaultDEMindex = "indices/1m_usgs_dem_coverage.shp"
coverageFields = ["project", "linkaws"]       # the fields housing project name and DEM link in the index

import arcpy
import urllib3
import os
import shutil
from buildContours import buildContours
 
def fetchDEM(boundaryFC, outDir, outFilename):

    # Check 1m DEM Index
    if arcpy.Exists(defaultDEMindex):
        count = arcpy.management.GetCount(defaultDEMindex)
        arcpy.AddMessage(f"Found {count} DEMs indexed in {defaultDEMindex}")
    else:
        arcpy.AddError(f"ERROR! Could not find parcel index in {defaultParcelIndex}")

    # Compare boundaryFC to DEM Index to see what DEMs need fetching
    arcpy.SetProgressor("default", f"Checking for DEMs which intersect the AOI...")
    intersectingDems = arcpy.SelectLayerByLocation_management(defaultDEMindex, 'INTERSECT', boundaryFC)
    demCount = int(arcpy.management.GetCount(intersectingDems)[0]) # convert Result object to int (via str)
    if demCount > 0:
        arcpy.AddMessage(f"{demCount} DEMs intersect the AOI")
    else:
        arcpy.AddError("No DEMs in the index file intersect your AOI! Check the index to see the coverage area")
    
    # Fetch all DEMs
    demList = []
    arcpy.AddMessage(f"\nDownloading Intersecting DEMs, please wait...")
    with arcpy.da.SearchCursor(intersectingDems, coverageFields) as cursor:
        for row in cursor:
            httpPath = row[1]
            basename = os.path.basename(httpPath)
            savePath = os.path.join(arcpy.env.scratchFolder, basename) # get rid of underscores for the DB

            arcpy.AddMessage(f"Downloading {httpPath} to {arcpy.env.scratchFolder}")
            arcpy.SetProgressor("default", f"Downloading {basename}")

            http = urllib3.PoolManager()
            with http.request('GET', httpPath, preload_content=False) as resp, open(savePath, 'wb') as out_file:
                if resp.status != 200:
                    arcpy.AddError(f"ERROR reaching {httpPath}")
                else:
                    # Save the output file
                    shutil.copyfileobj(resp, out_file)
            
            demList.append(savePath)

            # Add temp DEMs to map (don't do this now bc they are removed at end of script; kept in case needed for testing)
            # aprx = arcpy.mp.ArcGISProject("CURRENT")
            # aprx.activeMap.addDataFromPath(savePath)

    # Merge if there is more than one DEM
    if demCount > 1:
        arcpy.SetProgressor("default", f"Merging multiple rasters...")
        arcpy.AddMessage("Merging multiple rasters...")
        mergeRaster = arcpy.ia.Merge(demList, "FIRST")
    else:
        mergeRaster = demList[0]

    # Clip DEM to boundaryFC
    arcpy.SetProgressor("default", f"Clipping raster to area of interest...")
    arcpy.AddMessage("Clipping raster to area of interest...")
    savefile = os.path.join(outDir, outFilename)
    # outRaster = os.path.join(arcpy.env.scratchWorkspace, "out_raster")
    arcpy.management.Clip(mergeRaster, "", savefile, boundaryFC, "", "ClippingGeometry", "NO_MAINTAIN_EXTENT")

    # Add DEM to map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprx.activeMap.addDataFromPath(savefile)

    # Remove files created in arcpy.env.scratchFolder (they are not automatically deleted)
    arcpy.SetProgressor("default", "Removing temporary files...")
    arcpy.AddMessage("Removing temporary files...")
    for tempFile in demList:
        arcpy.management.Delete(tempFile)
    

    arcpy.AddMessage("Success!")


    return savefile





# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    boundaryFC = arcpy.GetParameterAsText(0)
    outDir = arcpy.GetParameterAsText(1)
    outTiffFilename = arcpy.GetParameterAsText(2)
    optionBuildContours = arcpy.GetParameterAsText(3)
    contourInterval = arcpy.GetParameterAsText(4)
    srs = arcpy.GetParameterAsText(5)
    outShpFilename = arcpy.GetParameterAsText(6)

    derivedDEM = fetchDEM(boundaryFC, outDir, outTiffFilename)

    # Also build contours if this option is set
    if optionBuildContours == 'true':
        buildContours(derivedDEM, outDir, outShpFilename, contourInterval, srs)
