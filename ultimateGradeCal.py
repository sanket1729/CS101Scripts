# coding= latin-1
import glob, sys
import string
from nbgrader.api import Gradebook

from getCollabs import getCollabs

'''
getGradeFromFile(filename) opens a file given by extract_grades.py
in the format where each line is
netid,score
and return the grades as a dictionary.
'''
def getGradeFromFile(filename):
    grades = {} #Use a dictionary
    with open(filename) as f:
        for line in f.readlines():
            line = line.split()
            grades[line[0]] = float(line[1])
        collabs = {}
        if len(sys.argv)==5: # Using collabs
            collabs = getCollabs(sys.argv[3], sys.argv[4])
        for submitter in collabs:
            netidlist = collabs [submitter]
            if submitter in grades: # They should be, if not, print error I guess
                for netid in netidlist:
                    if netid in grades:
                        grades[netid] = grades[submitter]
    return grades

'''
getCollabs(filename) opens a file given by collabs.py
in the format where each line is
netid [netid netid ...]
and return a dictionary where the submitter is the key
'''
def getCollabsFromFile(filename):
    collabs = {}
    with open(filename) as f:
        for line in f.readlines():
            if (line==''):
                continue
            line2 = ""
            line = line.strip()
            for c in line:
                if c in string.printable:
                    line2 += c
            line = line2.split(' ')
            submitter = line[0]
            collabsList = line[1:]
            for i in range(len(collabsList)):
                collabsList[i] = collabsList[i].strip()
            collabs[submitter] = collabsList
    return collabs

def parseGrades(grades):
    maxGrade = grades[max(grades, key=grades.get)]
    if maxGrade != 0:
        for key, value in grades.items():
            grades[key] = value / maxGrade * 2.0
    else:
        for key, value in grades.items():
            grades[key] = 2.0
    return grades

def parseCollabs(content, collabs,colNo):
    if len(collabs)==0:
        pass
    # print (collabs)
    for collab in collabs:
        for word in collabs[collab]:
            if word in content:
                # print (word, collab)
                if content[word][colNo]!='':
                    if float(content[word][colNo])>float(content[collab][colNo]):
                        content[collab][colNo] = content[word][colNo]
                        continue
                    else:
                        content[word][colNo] = content[collab][colNo] = "2.0" #unable it so that everyone gets 2.0
                # print(content[word][colNo],content[collab][colNo])

if __name__ == "__main__":
    if len(sys.argv)<4:
        print ("Usage: python ultimateGradeCal.py compassScores.csv labSec({A,B,..,Q}) labNo({00,01...15}) [collabs:Y/N]")
        exit(1)
    csvfilename = sys.argv[1]
    labSec = sys.argv[2]
    aNo = sys.argv[3] if len(sys.argv[3]) == 2 else '0' + sys.argv[3]
    from extract_grades import extract_grades
    grades = {}
    for labSecChar in labSec:
        grades.update(extract_grades(labSecChar,aNo))
    # from getValue0 import getHw1Score
    # grades = getHw1Score()
    # print (grades)
    grades = parseGrades(grades)

    collabs = {}
    if len(sys.argv)==5 and sys.argv[-1] != 'N':
        for labSecChar in labSec:
            collabs.update(getCollabs(labSecChar,aNo))
        # print (collabs)
    with open(csvfilename,'r') as f:
        fileContent = f.readlines()
        headers = fileContent[0].strip().split(',')
        colNo = -1
        netidNo = -1
        sectionNo = -1
        availNo = -1
        fileOutput = {} # dict of lists
        for i in range(len(headers)):
            if headers[i].find("lab "+str(aNo))>-1:
                colNo = i
            if headers[i].find("Username")>-1:
                netidNo = i
            if headers[i].find("Section")>-1:
                sectionNo = i
            if headers[i].find("Availability")>-1:
                availNo = i
        if colNo == -1 or netidNo == -1 or sectionNo == -1:
            raise ValueError("CSV file doesn't have all necessary columns.")          
        for line in fileContent[1:]:
            line = line.strip().split(',')
            netid = line[netidNo].strip('"')
            # print (netid)
            if netid in grades:
                line[colNo] = str(grades[netid])
                # print (line[colNo])
                fileOutput[netid]=(line.copy())
            else:
                line[colNo] = '0' # Set empty ones to 0
                fileOutput[netid]=(line.copy())
        parseCollabs(fileOutput, collabs,colNo)
        print (headers[netidNo]+','+headers[colNo])
        for netid in fileOutput:
            section = fileOutput[netid][sectionNo].strip()[-2]
            if section in labSec and fileOutput[netid][availNo].find('Yes')>-1:
                line = ','.join([fileOutput[netid][netidNo], fileOutput[netid][colNo]])
                print (line)

