###-
###This takes the session Hand history and puts it into one file for processing
###---------------------------------------------------------------------------

from os import listdir
from os.path import isfile, join

def mergeTextToWriteDestination(filenames,Dir):
    fileOutputPath = input("path to output files")
    with open(fileOutputPath, 'w') as outfile:
        for fname in filenames:
            with open(Dir + fname) as infile:
                outfile.write(infile.read())
    pass

def getAllFilesFromPath(directoryPath):
    return [f for f in listdir(directoryPath) if isfile(join(directoryPath, f))]

#file process
def sessionFilestoOneFile():
    mypath = input("Path to Files")
    AllFilePaths = getAllFilesFromPath(mypath)

    mergeTextToWriteDestination(AllFilePaths, mypath)
    pass
