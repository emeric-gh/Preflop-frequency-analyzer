#Data Prep Code Base

#completed functions -------------------------------------------------------------

import pandas as pd

def parseHandPos(preflopLine):
    #accept 1 line of preflop text 
    #returns hand and Position info
    
    if preflopLine.find("Card dealt to a spot") == -1: #this would mean this isnt a card assignemnt line #mistakes 
        positionInfo,leftcard,rightcard = None,None,None
    else: #text parse out 
        
        preflopLinewMeRemoved = preflopLine.replace(' [ME] ','')
        positionInfo = preflopLinewMeRemoved[:preflopLinewMeRemoved.find(":")-1]
        leftcard = preflopLinewMeRemoved[preflopLinewMeRemoved.find("[")+1:preflopLinewMeRemoved.find("[")+3]
        rightcard = preflopLinewMeRemoved[preflopLinewMeRemoved.find("[")+4:preflopLinewMeRemoved.find("[")+6]
    
    return positionInfo,leftcard,rightcard #cards have no fucntional order

def findSubstringInList(searchList, substring):
    #this useful fuction will return the index of the first list index that contains the substring
    
    if any(substring in string for string in searchList):
        return [idx for idx, s in enumerate(searchList) if substring in s][0] #returns the index location
    else:
        return -1 # returns -1 if the substring is not in the list

def preflopChunkParse(handHistory):
    ##assume that the last preflop aciton is the line before the "*** FLOP ***"
    handHistoryLines = handHistory.splitlines()
    
    preflopEndPhrase = "*** FLOP ***"
    preflopStartPhrase = "Card dealt to a spot"
    #using the phrase that starts the next phase
    preflopEnd =  findSubstringInList(handHistoryLines,preflopEndPhrase)
    
    #find the first list index in the reverse list that contains the phrase for card delt
    #this should be the last thing done before the preflop aciton 
    preflopStart = len(handHistoryLines) - findSubstringInList(handHistoryLines[::-1],preflopStartPhrase)
    
    #find the beginning and ending line
    preflopHandHistoryLines = handHistoryLines[preflopStart:preflopEnd]
    return preflopHandHistoryLines

def RFIAction(preflopHandHistoryLines):
    #expecting input of lines from the preflop
    
    RFIEndPhrase = "Raises"
    
    endingIndex = findSubstringInList(preflopHandHistoryLines, RFIEndPhrase)
    
    RFIActionLines = preflopHandHistoryLines[endingIndex]
    
    return RFIActionLines

def getAllLinesContainingSubString(listOfStrings, substring):
    
    return [s for s in listOfStrings if substring in s]



def spliceDeal(handHistory):
    handHistoryLines = handHistory.splitlines() 
    cardDealPhrase = "Card dealt to a spot"
    return getAllLinesContainingSubString(handHistoryLines, cardDealPhrase)


def createHoleCardDict(handHistory):
    
    #first reduce the Hand History to a list of relevant dealing card to position list
    dealtCardLines = spliceDeal(handHistory)
    
    #this line creats a dictionary by taking each line of the dealing action 
    #then it runs throught the parseHandpositions which give it the pos dict to the cards
    holeCardByPos = {parseHandPos(dealCardLine)[0]:(parseHandPos(dealCardLine)[1],parseHandPos(dealCardLine)[2]) for dealCardLine in dealtCardLines}
        
    return holeCardByPos

def getRFIPositionHand(agrigateHandHistory):
    #feed in Hand history output 
    #we want a dataframe that has Position and hand for every hand fed through a string
    
    #get line with RFI action 
    RFIAcitonLine = RFIAction(agrigateHandHistory.splitlines())
    
    preflopLinewMeRemoved = RFIAcitonLine.replace(' [ME] ','')
    RFIPosition = preflopLinewMeRemoved[:preflopLinewMeRemoved.find(":")-1]
    


    #if RFIPosition in position_list:
    #use the line to get position and then feed into dictionary
    
    holeCardByPos = createHoleCardDict(agrigateHandHistory)
        
    hand = (holeCardByPos[RFIPosition])
    
    
    return RFIPosition, hand 


def basicFileReader(fname=None): #rename this is aweful
    if fname==None:
        handhistoryfilename = input("file dir:")
    else:
        handhistoryfilename = fname
        
    handhistoryfilename.replace("\\","\\\\")
    #handhistoryfilename.replace('','')                            
    handHistoryText = open(handhistoryfilename,"r").read()
    return handHistoryText


    



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





#Main Run ---------------------------------------------------------------------------

def handHistoryToRFIdata(handHistoryPath):
    #position_list = ['Dealer' , 'Small Blind' , 'Big Blind', 'UTG', 'UTG+1', 'UTG+2', 'UTG+3', 'UTG+4', 'UTG+5']

    Header1 = 'Positions'
    Header2 = 'Hand'

    position_Headers = [Header1, Header2]
    RFITable = pd.DataFrame(columns = position_Headers)


    bulkHandHistory = basicFileReader(handHistoryPath)
    #iterate over Hands
    bulkHandHistoryLines = bulkHandHistory.split("Ignition Hand")

    for hand in bulkHandHistoryLines:
        
        if  findSubstringInList(preflopChunkParse(hand),"Raises") > 0:
            d = {Header1: getRFIPositionHand(hand)[0], Header2 : (getRFIPositionHand(hand)[1],)}
            newRFIData = pd.DataFrame(d)
            RFITable = RFITable.append(newRFIData)
        
    return RFITable


