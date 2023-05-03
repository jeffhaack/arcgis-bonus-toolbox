# TWM Tools

A toolbox for common GIS operations.

<img src="https://user-images.githubusercontent.com/322468/215392772-d6325600-bbb3-421f-abfe-ddd2ba6aa7ed.png" width=250>


## Data Request

A set of tools for serving GIS data requests.



### Build Contours From DEM

![image](https://user-images.githubusercontent.com/322468/215391370-4dc8c20f-01a0-4be3-9e0c-75c6c5761175.png)

This tool builds contour lines from a DEM according to a standard procedure.

  1. Focal Statistics is run with a cell size of 5.
  2. Raster units are checked. If the vertical units are in meters, they are converted to feet.
  3. Contour lines are created in a z-enabled shapefile.

Inputs:

  - **Input DEM:** The elevation raster from which to build contours
  - **Output Directory:** Directory where the output contours will be saved
  - **Output Filename:** Name of the saved contours file. Must be .shp
  - **Contour Interval (ft):** Interval between contours lines, in feet
  - **Output Coordinate System:** The SRS of the output shapefile

___________________________

### Fetch DEM (& Build Contours)

![image](https://user-images.githubusercontent.com/322468/215390548-8979fff5-0be9-45e9-9695-c0c97e2a6585.png)

This tool compares an AOI with an index of 1m resolution USGS DEMs. It then retrieves them from USGS servers,
merges if necessary, and clips to the AOI to output a 1m resolution DEM.

If the option to Build Contours is selected, it will additionally run the Build Contours tool (described above).

Inputs:

  - **Area of Interest:** A polygon feature layer of the area requested
  - **Output Directory:** Directory where the output DEM (and contours) will be saved
  - **DEM Output Filename:** Name of the saved DEM file. Save as a .tif

___________________________

### Get Parcels

![Screenshot 2023-01-29 111807](https://user-images.githubusercontent.com/322468/215390072-819eb66a-1068-46ec-86b0-a5dc4317ab65.png)

This tool compares an AOI with an index of TWM parcel data. It retrieves overlapping data sets and clips them to the AOI, saving
to shapefile.

_Note that most of our parcel data is organized by county. In the rare case that an AOI overlaps two or more counties, the tool
will save multiple shapefiles that must then be merged manually._

Inputs:

  - **Area of Interest:** A polygon feature layer of the area requested
  - **Output Directory:** Directory where the output parcels will be saved
  - **Output Filename:** Name of the output parcel shapefile. Save as a .shp
  - **Output Coordinate System:** The SRS of the output shapefile
  - **Clip to AOI:** If selected, the parcels will be clipped by the AOI. If unselected, all parcels which intersect the AOI will be output in full. Default is unselected.
  
