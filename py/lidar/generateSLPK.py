'''
Geoprocessing Tool which builds clips and exports a single raster
Additional options provided based on past projects
'''

import arcpy
import os

lasToolsBinaryDir = r'..\..\bin\LAStools'
# LAStools used in this script
lasinfo = os.path.join(lasToolsBinaryDir, "lasinfo.exe")
las2las = os.path.join(lasToolsBinaryDir, "las2las.exe")
txt2las = os.path.join(lasToolsBinaryDir, "txt2las.exe")
lassplit = os.path.join(lasToolsBinaryDir, "lassplit.exe")

def generateSLPK(inputDirectory, srs, outputFile):
    # Get datasets in inputDirectory
    arcpy.env.workspace = inputDirectory
    lasDatasets = arcpy.ListFiles("*.las")
    lasDSCount = len(lasDatasets)
    xyzDatasets = arcpy.ListFiles("*.xyz")
    xyzDSCount = len(xyzDatasets)

    # Error Checking
    if lasDSCount != 0 and xyzDSCount != 0:
        arcpy.AddError("ERROR! Found multiple data formats in input directory (las and xyz)")
    elif lasDSCount == 0 and xyzDSCount == 0:
        arcpy.AddError("ERROR! Found no LAS or XYZ files in input directory")
    elif lasDSCount != 0:
        datasets = lasDatasets
        format = "las"
        arcpy.AddMessage(f"Found {lasDSCount} .{format} files in {inputDirectory}")
    elif xyzDatasets != 0:
        datasets = xyzDatasets
        format = "xyz"
        arcpy.AddMessage(f"Found {xyzDSCount} .{format} files in {inputDirectory}")
    else:
        arcpy.AddError("UNKNOWN ERROR! Check with your developer. Tell him Error Code 999992123419124912421499412491239. Just kidding.")


    # Convert xyz to las if necessary
    if format == 'xyz':
        # Add quotation marks to a string; used to wrap system paths that contain whitespace
        def addQuotes(str):
            return f'"{str}"'
        # Notify user
        arcpy.SetProgressor("default", f"Converting XYZ files to LAS...")
        arcpy.AddMessage(f"Converting XYZ files to LAS...")
        # Make new folder in scratch directory and point inputDirectory there
        arcpy.management.CreateFolder(arcpy.env.scratchFolder, "tempFolder")
        tempDirectory = os.path.join(arcpy.env.scratchFolder, "tempFolder")
        # Convert each XYZ file
        for file in datasets:
            convertedFile = os.path.join(tempDirectory, os.path.splitext(os.path.basename(file))[0] + '.las')
            cmd = f'{txt2las} -i {addQuotes(os.path.join(inputDirectory, file))} -o {addQuotes(convertedFile)} -parse xyz'
            os.system(cmd)
        # Reassign inputDirectory to tempDirectory
        inputDirectory = tempDirectory
        arcpy.env.workspace = inputDirectory
        datasets = arcpy.ListFiles("*.las")

    # Define projection
    arcpy.SetProgressor("default", f"Setting Projection...")
    arcpy.AddMessage(f"Setting Projection...")
    for file in datasets:
        arcpy.management.DefineProjection(file, srs)

    # Create SLPK
    slpkProj = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["EGM96_Geoid",VDATUM["EGM96_Geoid"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
    slpkConversionMethod = "NAD_1983_HARN_To_WGS_1984_2" # PROBLEM HERE; THIS WILL BE DIFFERENT DEPENDING ON ORIGINAL PROJECTION
    arcpy.management.CreatePointCloudSceneLayerPackage(inputDirectory, outputFile, slpkProj, "", "INTENSITY;RGB;CLASS_CODE;RETURNS", 0, 0.01, 0.01, None, "2.x")

    # Delete tempDirectory
    arcpy.management.Delete(tempDirectory)

    arcpy.AddMessage("Success!")
    


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    inputDirectory = arcpy.GetParameterAsText(0)
    srs = arcpy.GetParameterAsText(1)
    outputFile = arcpy.GetParameterAsText(2)
    
    generateSLPK(inputDirectory, srs, outputFile)
