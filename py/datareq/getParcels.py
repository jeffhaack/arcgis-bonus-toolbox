'''
Geoprocessing Tool which checks an AOI against an index of parcel data
Fetches intersecting data and saves to output location
'''

parcelDB = r"T:\Geospatial\GIS\BoundaryLines\Parcels\Ext_Parcel.gdb"
defaultParcelIndex = r"T:\Geospatial\GIS\BoundaryLines\Parcels\Ext_Parcel.gdb\Parcel_Coverage_Index"
coverageFields = ["Parcel_Status", "Data_Path"]       # the fields we need from the index (not actually using Parcel_Status though)

import arcpy
import os


def clipParcels(boundaryFC, outDir, outFilename, srs, clipToAOI):
    # Check Parcel Index
    arcpy.AddMessage("Checking data sources...")
    if arcpy.Exists(defaultParcelIndex):
        arcpy.AddMessage(f"Using parcel index in {defaultParcelIndex}")
    else:
        arcpy.AddError(f"ERROR! Could not find parcel index in {defaultParcelIndex}")

    # Make sure AOI is a polygon
    ### DEPRECATED; this validation is done in the tool parameters already
    # desc = arcpy.Describe(boundaryFC)
    # if desc.featureType == 'Simple' and desc.shapeType == "Polygon":
    #     count = arcpy.management.GetCount(boundaryFC)
    #     arcpy.AddMessage(f"Input is a polygon feature class, hooray! Number of features: {count}")
    # else:
    #     arcpy.AddError("Input is not a Polygon layer!")


    # Get overlapping features, where Parcel_Status is True
    arcpy.SetProgressor("default", f"Looking for intersecting parcel data...")
    validRegions = arcpy.management.SelectLayerByAttribute(defaultParcelIndex, 'NEW_SELECTION', "Parcel_Status = 'Y'")  # Only check features that are marked as "Y" ("Yes")
    intersectingRegions = arcpy.management.SelectLayerByLocation(validRegions, 'INTERSECT', boundaryFC)                 # See which features are intersected
    regionCount = int(arcpy.management.GetCount(intersectingRegions)[0])                                                # convert Result object to int (via str)
    if regionCount == 0:
        arcpy.AddError("No DEMs in the index file intersect your AOI! Check the index to see the coverage area")
    elif regionCount > 1:
        # Warning if there are more than one intersecting areas
        arcpy.AddWarning(f"The AOI intersects {regionCount} parcel index feature classes. Parcels will be output to multiple shapefiles")
    else:
        arcpy.AddMessage(f"Found {regionCount} match that intersects the AOI...")


    # Get the data source from index file
    fcList = []
    arcpy.AddMessage(f"\nLoading intersecting parcel feature classes...")
    with arcpy.da.SearchCursor(intersectingRegions, coverageFields) as cursor:
        i = 0
        for row in cursor:
            i += 1
            dataSource = os.path.join(parcelDB, row[1])
            arcpy.AddMessage(f"Found parcel data in {dataSource}")

            # Extend file name if there are multiple outputs
            if i == 1:
                savefile = os.path.join(outDir, outFilename)
            else:
                savefile = os.path.join(outDir, outFilename.replace('.shp', f"_{i}.shp"))
 

            # Clip parcels using output SRS
            arcpy.env.outputCoordinateSystem = srs
            # savefile = os.path.join(outDir, outFilename)
            if clipToAOI == 'false':
                # Get intersecting parcels
                arcpy.SetProgressor("default", f"Outputting parcels which intersect the AOI")
                intersectingParcels = arcpy.management.SelectLayerByLocation(dataSource, 'INTERSECT', boundaryFC)
                arcpy.management.CopyFeatures(intersectingParcels, savefile)
            else:
                # Clip parcels to AOI
                arcpy.SetProgressor("default", f"Clipping and outputting parcels which intersect the AOI")
                arcpy.analysis.Clip(dataSource, boundaryFC, savefile, None)

            # Add Parcels to Map
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            aprx.activeMap.addDataFromPath(savefile)
            arcpy.AddMessage("Parcels added to map")


    arcpy.AddMessage("Success!")


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    boundaryFC = arcpy.GetParameterAsText(0)
    outDir = arcpy.GetParameterAsText(1)
    outFilename = arcpy.GetParameterAsText(2)
    srs = arcpy.GetParameterAsText(3)
    clipToAOI = arcpy.GetParameterAsText(4)
    
    clipParcels(boundaryFC, outDir, outFilename, srs, clipToAOI)
