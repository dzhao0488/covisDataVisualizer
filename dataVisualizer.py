from urllib.request import urlopen
from urllib.request import urlretrieve
from pathlib import Path
import os
import pandas as pd
import numpy as np
import csv
import re
from collections import defaultdict


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


def downloadYearFolder(yearLink, fileType = None):
    page = urlopen(yearLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{yearLink}{link}' for link in links]
    
    for link in fullLinks:
        downloadMonthFolder(link, fileType)


def downloadMonthFolder(monthLink, fileType = None):
    page = urlopen(monthLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{monthLink}{link}' for link in links]
    
    for link in fullLinks:
        downloadDayFolder(link, fileType)

# WIP
def downloadDayFolder(dayLink, fileType = None):
    page = urlopen(dayLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    fullLinks = [f'{dayLink}{link}' for link in links]
    
    
    for link in fullLinks:
        downloadFile(link, fileType)

# WIP
def downloadFile(fileLink, fileType=None):
    page = urlopen(fileLink)
    html = page.read().decode('utf-8')

    pattern = r'href\s*=\s*["\']([^"\']+\.mat)["\']'
    links = re.findall(pattern, html)
    if not links:
        return 0

    cwd = os.getcwd()
    for link in links:
        if fileType and fileType.lower() not in link.lower():
            print(f'{link} rejected (wrong type)')
            continue

        fullLink = f'{fileLink}{link}'
        os.makedirs(os.path.join(cwd, 'matFiles'), exist_ok=True)
        urlretrieve(fullLink, os.path.join(cwd, 'matFiles', link))
        print(f'{link} has been successfully downloaded')


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
    menuList = ['1: Download files ']
    for item in menuList:
        print(item)

def downloadNav(tf):
    if tf == '1':
        yearLink = input('Please paste the full link: ')
        fileType = input('Please choose file type: diffuse, doppler, imaging (blank for all): ')
        downloadYearFolder(yearLink, fileType)
    elif tf == '2':
        monthLink = input('Please paste the full link: ')
        fileType = input('Please choose file type: diffuse, doppler, imaging (blank for all): ')
        downloadMonthFolder(monthLink, fileType)
    elif tf == '3':
        dayLink = input('Please paste the full link: ')
        fileType = input('Please choose file type: diffuse, doppler, imaging (blank for all): ')
        downloadDayFolder(dayLink, fileType)
    elif tf == '4':
        fileLink = input('Please paste the full link: ')
        fileType = input('Please choose file type: diffuse, doppler, imaging (blank for all): ')
        downloadDayFolder(fileLink, fileType)


def main():

    while True:
        displayMenu()
        choice = input('Choose an option (0 to quit): ')
        if choice == '1':
            downloadNav(input('Choose a time frame (1 for year, 2 for month, 3 for day, or 4 for single file): '))
        elif choice == '0':
            return

main()