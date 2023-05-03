import arcpy
import os
import urllib3
import shutil
import re

httpPath = r"http://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/1m/Projects/MO_WestCentral_2018_D19/TIFF/USGS_1M_15_x62y431_MO_WestCentral_2018_D19.tif"
savePath = r"test.tif"


http = urllib3.PoolManager()

with http.request('GET', httpPath, preload_content=False) as resp, open(savePath, 'wb') as out_file:
    if resp.status != 200:
        print(f"ERROR reaching {httpPath}")
    else:
        # Save the output file
        shutil.copyfileobj(resp, out_file)