from urllib.request import urlopen
from urllib.request import urlretrieve
from pathlib import Path
import os
import scipy
import pandas as pd
import numpy as np
import csv
import json
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Web Functions

def checkForMatFiles(link, choice):
    noMatFiles = []
    
    if choice == 'year':
        pattern = r'/(\d{4})/'
        year = re.search(pattern, link).group(1)
        noMatFiles.append(downloadYearFolder(link, checking = True))
        if noMatFiles:
            with open(f'{year}MissingMatFiles', 'w') as fileOut:
                for link in noMatFiles:
                    fileOut.write(link)
    elif choice == 'month':
        pattern = r'/(\d{2})/'
        month = re.search(pattern, link).group(1)
        noMatFiles.append(downloadMonthFolder(link, checking = True))
        if noMatFiles:
            with open(f'{month}MissingMatFiles', 'w') as fileOut:
                for link in noMatFiles:
                    fileOut.write(link)
    elif choice == 'day':
        pattern = r'/(\d{2})/'
        day = re.search(pattern, link).group(1)
        noMatFiles.append(downloadDayFolder(link, checking = True))
        if noMatFiles:
            with open(f'{day}MissingMatFiles', 'w') as fileOut:
                for link in noMatFiles:
                    fileOut.write(link)
    else:
        print('Invalid Choice')


def downloadYearFolder(yearLink):
    page = urlopen(yearLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{yearLink}{link}' for link in links]
    
    for link in fullLinks:
        downloadMonthFolder(link)


def downloadMonthFolder(monthLink):
    page = urlopen(monthLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{monthLink}{link}' for link in links]
    
    for link in fullLinks:
        downloadDayFolder(link)


def downloadDayFolder(dayLink):
    page = urlopen(dayLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{dayLink}{link}' for link in links]
    
    for link in fullLinks:
        downloadFile(link)


def downloadFile(fileLink):
    page = urlopen(fileLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+\.mat)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{fileLink}{link}' for link in links]

    if (not fullLinks):
        return fileLink
    else:
        i = 0
        for link in fullLinks:
            urlretrieve(f'{link}', f'C:\\Users\\imort\\OneDrive\\Documents\\Personal Projects\\VizLab\\dataReader\\matFiles\\{links[i]}')
            print(f'{link} has been successfully downloaded')
            i += 1


# Local Directory Functions

# Converts a .mat file into a JSON file and returns a dictionary containing the contents of the .mat file
def convertFile(fileInName):   
    with open(fileInName, 'r') as fileIn:
        fileContents = scipy.io.loadmat(fileInName)
        covisDict = {}
        covisDict['header'] = fileContents['__header__'].decode('utf-8')
        covisDict['version'] = fileContents['__version__']
        covisDict['globals'] = fileContents['__globals__']
        covis = fileContents['covis'][0][0]
        for name in covis.dtype.names:
            covisDict[name] = covis[name][0]
        
        print(f'{fileInName} has been converted')
        return covisDict


def readCoords2D(fileInName):
    with open(fileInName) as fileIn:
        covisDict = convertFile(fileInName)
        xList = [x for x in covisDict['grid'][0][0][0]['x']]
        yList = [y for y in covisDict['grid'][0][0][0]['y']]
        vList = [v for v in covisDict['grid'][0][0][0]['v']]
        wList = [w for w in covisDict['grid'][0][0][0]['w']]
        coordsDict = {'xList': xList, 'yList': yList, 'vList': vList, 'wList': wList}
        return coordsDict


def readCoords3D(fileInName):
    with open(fileInName) as fileIn:
        covisDict = convertFile(fileInName)
        xList = [x for x in covisDict['grid'][0][0][0]['x']]
        yList = [y for y in covisDict['grid'][0][0][0]['y']]
        zList = [z for z in covisDict['grid'][0][0][0]['z']]
        vList = [v for v in covisDict['grid'][0][0][0]['v']]
        wList = [w for w in covisDict['grid'][0][0][0]['w']]
        coordsDict = {'xList': xList, 'yList': yList, 'vList': vList, 'wList': wList}
        return coordsDict
    

def createCoordsOfInterest(fileInName):
    coordsDict = readCoords2D(fileInName)
    coordsOfInterest = {x: [] for x in coordsDict.keys()}
    ind = 0
    for key in coordsDict.keys():
        for array in coordsDict['vList']:
            coordsOfInterest[key].append(coordsDict[key][ind])
            ind += 1
        ind = 0
    return coordsDict

    
def plotDiffuse2D(fileInName):
    coordsOfInterest = createCoordsOfInterest(r'matFiles\COVIS-20230701T003002-diffuse1.mat')
    plt.figure(figsize=(10, 6))
    max = np.amax(np.concatenate(coordsOfInterest['vList']))
    min = np.amin(np.concatenate(coordsOfInterest['vList'])) + 10e-10
    norm = mcolors.LogNorm(vmin=min, vmax=max)
    scatter = plt.scatter(coordsOfInterest['xList'], coordsOfInterest['yList'], c = coordsOfInterest['vList'], cmap = 'viridis', norm = norm)

    cbar = plt.colorbar(scatter)
    cbar.set_label('Data Values')

    plt.xlabel('East of COVIS (m)')
    plt.ylabel('North of COVIS (m)')
    plt.title(fileInName.split('\\')[-1])
    plt.show()


# WIP

def createJSONFromFile(fileInName, fileOutName):
    with open(fileInName) as fileIn, open(fileOutName, 'w') as fileOut:
        json.dump(convertFile(fileInName), fileOut, indent = 4, cls = NumpyEncoder)
        print(f'Created JSON file for {fileInName}')


def addToDirectory(fileName):
    if Path('directory.csv').exists():
        rows = []
        with open('directory.csv', 'r') as fileIn:
            reader = csv.reader(fileIn)
            header = next(reader)
            for row in reader:
                rows.append(row)
        with open('directory.csv', 'w', newline = '') as fileOut:
            writer = csv.writer(fileOut)
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)
            _, extension = os.path.splitext(fileName)
            writer.writerow([extension, fileName])
    else:
        with open('directory.csv', 'w', newline = '') as fileOut:
            writer = csv.writer(fileOut)
            writer.writerow(['fileType', 'fileName'])
            _, extension = os.path.splitext(fileName)
            writer.writerow([extension, fileName])


def displayLocalDirectory():
    with open('directory.csv', 'r') as fileIn:
        reader = csv.reader(fileIn)
        header = next(reader)
        fileName = header.index('fileName')
        fileList = []

        for row in reader:
            fileList.append(row[fileName])
        
        for fileName in fileList:
            print (fileName)


# Inspired by https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.void):
                return {name: obj[name] for name in obj.dtype.names}
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif isinstance(obj, np.generic):
                return obj.item()
            return json.JSONEncoder.default(self, obj)


def loadJSONFile(fileInName):
    with open(fileInName) as fileIn:
        fileContents = json.loads(fileInName)
        # covisDict = np.asarray(fileContents["a"])
        return fileContents

# User Interface
def displayMenu():
    menuList = ['1: Download files ', '2: Plot diffuse 2D from local file', '3: Plot imaging 3D from local file']
    for item in menuList:
        print(item)

def downloadNav(tf):
    if tf == '1':
        yearLink = input('Please paste the full link: ')
        downloadYearFolder(yearLink)
    elif tf == '2':
        monthLink = input('Please paste the full link: ')
        downloadMonthFolder(monthLink)
    elif tf == '3':
        dayLink = input('Plesae paste the full link: ')
        downloadDayFolder(dayLink)
    elif tf == '4':
        fileLink = input('Please paste the full link: ')
        downloadDayFolder(fileLink)


def main():
    while True:
        displayMenu()
        choice = input('Choose an option (0 to quit): ')
        if choice == '1':
            downloadNav(input('Choose a time frame (1 for year, 2 for month, 3 for day, or 4 for single file): '))
        elif choice == '2':
            plotDiffuse2D(input('Please paste the relative file path: '))
        elif choice == '0':
            break

main()