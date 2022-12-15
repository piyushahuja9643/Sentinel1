import os
from snappy import GPF,ProductIO,HashMap
import time
import datetime
from queue import *
from _thread import *
from time import *
from datetime import datetime
 
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
prods = []
file1 = ""
file2 = ""
strFile1 = ""
strFile2 = ""
strInSAR = ""
target1 = ""
target2 = ""
targetTOPSplit1 = ""
targetTOPSplit2 = ""
targetbackGeo = ""
targetInterferogram = ""
targetTOPSARDeburst = ""
targetESD =""
 
q = Queue()
 
def readFiles(filename1, filename2):
   global file1
   global file2
   global strFile1
   global strFile2
   global strInSAR
   file1 = ProductIO.readProduct(filename1)
   strFile1 = file1.getName()
   file2 = ProductIO.readProduct(filename2)
   strFile2 = file2.getName()
  
 
def tOPSARSplit():
   global file1
   global file2
   global targetTOPSplit1
   global targetTOPSplit2
   parameters = ""
   parameters = HashMap()
   parameters.put('subswath', 'IW3')
   parameters.put('selectedPolarisations', 'VV')
   parameters.put('firstBurstIndex', 7)
   parameters.put('lastBurstIndex', 8)
   targetTOPSplit1 = GPF.createProduct("TOPSAR-Split",     parameters, file1)
   targetTOPSplit2 = GPF.createProduct("TOPSAR-Split", parameters, file2)
 
def applyOrbitFile():
   global targetTOPSplit1
   global targetTOPSplit2
   global target1
   global target2
   global prods
   parameters = HashMap()
   parameters.put("orbitType", "Sentinel Precise (Auto Download)")
   parameters.put("polyDegree", 3)
   target1 = GPF.createProduct("Apply-Orbit-File", parameters, targetTOPSplit1)
   target2 = GPF.createProduct("Apply-Orbit-File", parameters, targetTOPSplit2)
   prods.append(target2)
   prods.append(target1)

def backGeocoding():
   global prods
   global targetbackGeo
   parameters = ""
   parameters = HashMap()
   parameters.put("externalDEMFile","C:\\Users\\Devishri\\Downloads\\srtm_54_07.zip")
   parameters.put("demResamplingMethod", "BICUBIC_INTERPOLATION")
   parameters.put("resamplingType", "BISINC_5_POINT_INTERPOLATION")
   parameters.put("maskOutAreaWithoutElevation", True)
   parameters.put("outputDerampDemodPhase", False)
   targetbackGeo = GPF.createProduct("Back-Geocoding", parameters, prods)
  
def ESD():
   global targetESD
   parameters = ""
   parameters = HashMap()
   parameters.put("fineWinWidthStr", "512")
   parameters.put("fineWinHeightStr", "512")
   parameters.put("fineWinAccAzimuth", "16")
   parameters.put("fineWinAccRange", "16")
   parameters.put("fineWinOversampling", "128")
   parameters.put("xCorrThreshold", 0.1)
   parameters.put("cohThreshold", 0.3)
   parameters.put("numBlocksPerOverlap", 10)
   parameters.put("esdEstimator", "Periodogram")
   parameters.put("weightFunc", "Inv Quadratic")
   parameters.put("temporalBaselineType", "Number of images")
   parameters.put("maxTemporalBaseline", 4)
   parameters.put("integrationMethod", "L1 and L2")
   parameters.put("overallRangeShift", 0.0)
   parameters.put("overallAzimuthShift", 0.0)
   targetESD = GPF.createProduct("Enhanced-Spectral-Diversity", parameters, targetbackGeo)
  
def writeprod(target,filename):
   print("write")
   writeloc = input("Enter the location of folder for reading the file: \n")
   print("Printing the Location of folder:"+ writeloc)
   ofile = writeloc+filename
   ProductIO.writeProduct(target, ofile, 'BEAM-DIMAP')   # TO DO:  allow other types here: BEAM-DIMAP, GeoTIFF-BigTIFF, HDF5

def DestinationThread() :
   while True :
       f, args = q.get()
       f(*args)
 
start_new_thread( DestinationThread, tuple() )
 
print ("Snappy TOPSAR InSAR: start")
start = datetime.now()
readloc = input("Enter the location of folder for reading the file: \n")
#Checking the Folder
for x in os.listdir():
   if x.endswith(".zip"):
       # Prints only text file present in My Folder
       print("Printing all the files inside folder: \n"+ x)
#Taking file input
print("Printing the Location of folder:"+ readloc)
# NOTE:  add them in date order, oldest to newest
filename1 = readloc + input("Enter the name of the Master File: \n ")
filename2 = readloc + input("Enter the name of the Slave File: \n")
#Reading the file
sleep(1)
readFiles(readloc+filename1,readloc+filename2)
### tOPSAR-Split step
sleep( 1 )
tOPSARSplit()
### ApplyOrbitFile step
sleep( 1 )
applyOrbitFile()
### backGeocoding step
sleep( 1 )
backGeocoding()
sleep(1)
writeprod()
end = datetime.now()
print("The time of execution of the above program is :",(end-start), "seconds")
