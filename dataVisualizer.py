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
        cwd = os.getcwd()
        for link in fullLinks:
            urlretrieve(f'{link}', f'{cwd}\\matFiles\\{links[i]}')
            print(f'{link} has been successfully downloaded')
            i += 1

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
        dayLink = input('Please paste the full link: ')
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

main()