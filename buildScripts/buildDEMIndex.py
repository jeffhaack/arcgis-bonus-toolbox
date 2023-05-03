'''
The FESM_1m index has coverage for 1m resolution USGS DEMs, and links to the TIFF directories
in those areas.

I'd like a finer index that references each individual DEM.

This script will go through all the index features in a FESM_1m file (something clipped so it is not
the whole country). Then it will find all the TIFFs in the related web directory, download them, build
an coverage feature for each, and append it to a new feature layer, which will index every DEM in the
coverage area.

inputCoverage is derived from https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/1m/FullExtentSpatialMetadata/
however, many of the links are slightly incorrect, so ./indices/FESM_1m_IL_MO_TN.shp is a corrected version of the coverage area

some inspiration at https://dwtkns.com/srtm30m/

direct access to TNM data at https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/
'''

# Edit these as needed:
inputCoverage = r"./indices/FESM_1m_IL_MO_TN.shp"
inputCoverageFields = ["project", "product_li"]
outputCoverageDir = r"output"
outputCoverageFile = r"1m_usgs_dem_coverage.shp"
tempDir = r"tempData"


import arcpy
import os
import urllib3
import shutil
import re
import zipfile

# Create output shapefile
if not os.path.exists(outputCoverageDir):
    cmd = f"mkdir {outputCoverageDir}"
    os.system(cmd)
if not os.path.exists(os.path.join(outputCoverageDir, outputCoverageFile)):
    arcpy.management.CreateFeatureclass(os.path.abspath(outputCoverageDir), outputCoverageFile, "POLYGON", None, "DISABLED", "DISABLED", 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision', '', 0, 0, 0, '')
    arcpy.management.AddFields(os.path.abspath(os.path.join(outputCoverageDir, outputCoverageFile)), "project TEXT # 255 # #;link TEXT # 400 # #;linkaws TEXT # 400 # #")

# Create Temp Directory
if not os.path.exists(tempDir):
    cmd = f"mkdir {tempDir}"
    os.system(cmd)

# Open shapefile and iterate features
areaCounter = 0
with arcpy.da.SearchCursor(inputCoverage, inputCoverageFields) as inputCoverageCursor:
    try:
        for row in inputCoverageCursor:
            projectName = row[0]
            httpTiffDir = row[1] + "/TIFF"
            # Switch URL to USGS Server instead of Amazon, bc its easier to scrape for the TIF files
            httpTiffDir = httpTiffDir.replace("http://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/", "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/")
            # Patch because they changed some of the directories to use underscores w/o updating index
            httpTiffDir = httpTiffDir.replace("-", "_")
            httpTiffDir = httpTiffDir.replace("prd_tnm", "prd-tnm")


            http = urllib3.PoolManager()
            r = http.request('GET', httpTiffDir)
            if r.status != 200:
                print(f"ERROR reaching {httpTiffDir}")
            else:
                # Find all tifs on page
                matches = re.findall(r'USGS.*?tif', str(r.data))
                # and remove duplicates (from links)
                matches = list(dict.fromkeys(matches))

                print(f"{len(matches)} matches in {httpTiffDir}")

                if len(matches) < 50000:
                    print(f"Retrieving {len(matches)} tifs from {projectName}")
                    # Download each TIF to tempDir
                    tifCount = 0
                    for tif in matches:
                        tifCount += 1
                        savePath = os.path.abspath(os.path.join(tempDir, tif))
                        httpPath = httpTiffDir + "/" + tif

                        # Switch URL to back to Amazon Server, bc its way faster to download
                        linkRocky = httpPath
                        httpPath = httpPath.replace("https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/", "http://prd-tnm.s3.amazonaws.com/StagedProducts/")

                        # If it's already been added to the output, skip this row
                        alreadyDone = False                        
                        with arcpy.da.SearchCursor(os.path.abspath(os.path.join(outputCoverageDir, outputCoverageFile)), ["linkaws"]) as checkCursor:
                            for row in checkCursor:
                                if row[0] == httpPath:
                                    # print(f"Already got {httpPath}")
                                    alreadyDone = True
                        if alreadyDone or (projectName == "IL_HicksDome_FluorsparDistrict_2019_D19" and tifCount == 155): # FOR SOME REASON THIS ONE TIF BREAKS THINGS, I ADDED IT TO OUTPUT MANUALLY
                            # print(f"Skipping {tifCount}")
                            continue

                        with http.request('GET', httpPath, preload_content=False) as resp, open(savePath, 'wb') as out_file:
                            if resp.status != 200:
                                print(f"ERROR reaching {httpPath}")
                            else:
                                # Save the output file
                                shutil.copyfileobj(resp, out_file)
    
                                # Convert the raster to two bits, one of which is nodata
                                savePathTemp = os.path.abspath(os.path.join(tempDir, "temp_" + tif))
                                arcpy.management.CopyRaster(savePath, savePathTemp, '', None, "0", "NONE", "NONE", "2_BIT", "NONE", "NONE", 'TIFF', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
                                # NOTE: for some reason I can't remember, I had this set at 2_BIT, which worked for every DEM except one; really it should be 1_BIT though, which ought to work ??
                                # TODO
                                # arcpy.management.CopyRaster(savePath, savePathTemp, '', None, "0", "NONE", "NONE", "1_BIT", "NONE", "NONE", "TIFF", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

                                # Convert the temp raster to a polygon
                                tempShp = os.path.abspath(os.path.join(tempDir, "temp.shp"))
                                arcpy.env.outputZFlag = "Disabled"
                                arcpy.env.outputMFlag = "Disabled"
                                arcpy.conversion.RasterToPolygon(savePathTemp, tempShp, "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
                                
                                # Reproject - not actually necessary!
                                # tempShpProject = os.path.abspath(os.path.join(tempDir, "tempProj.shp"))
                                # arcpy.management.Project(tempShp, tempShpProject, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', "WGS_1984_(ITRF00)_To_NAD_1983", 'PROJCS["NAD_1983_UTM_Zone_15N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-93.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]', "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")

                                # Merge the temp polygon into the output file
                                outFilePath = os.path.abspath(os.path.join(outputCoverageDir, outputCoverageFile))
                                with arcpy.da.InsertCursor(outFilePath, ["Shape@", "project", "link", "linkaws"]) as outCursor:
                                    for poly in arcpy.da.SearchCursor(tempShp, ["Shape@"]):
                                        outCursor.insertRow([poly[0], projectName, linkRocky, httpPath])

                                

                        # Empty the temp directory
                        for file in os.scandir(tempDir):
                            os.remove(file.path)

                        resp.release_conn()

                        # exit()
                        # Backup every 10 iterations
                        if tifCount % 10 == 0:
                            filenames = os.listdir(outputCoverageDir)
                            with zipfile.ZipFile(rf"zips\bak_{projectName}_{tifCount}.zip", mode="w") as archive:
                                for filename in filenames:
                                    if not filename.endswith(".lock"):
                                        archive.write(os.path.join(outputCoverageDir, filename))


            # Get link and find TIFF directory
            # Download each TIF to tempDir
            # Get extent of each TIF
            # Make sure extent is in EPSG 4269
            # Append feature to output shapefile, including link to the TIF and project name

            areaCounter += 1
    except Exception as e:
        print(e)


print(areaCounter)



# arcpy.env.workspace = './indices'
# test =arcpy.ListFeatureClasses()
# print(test)

# print(arcpy.ListFields(inputCoverage))




 