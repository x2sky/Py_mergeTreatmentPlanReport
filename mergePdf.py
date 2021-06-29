# -*- mergePdf -*- #
"""
SYNOPSIS
    Merge plan pdf files, currently only Oncentra brachy plan report

DESCRIPTION
    Merge plan pdf files, first, a list of plan files is compiled from a predetermined folder,
    then getPdfInfo and getJpgInfo were used to get the file info,
    then the appropriate files are merged and saved into a designated folder
    
EXAMPLES
    main(srcFolderPath, mergFolderPath): Compile list of plan files and merge the appropriate files together
    mergeBrachyPlanFile(ptPdfInfos, ptJpgInfos, mergFolderPath): combine the brachy plan files into a merged file
    
VERSION 0.1
AUTHOR
    Becket Hui 2020 10
    
"""

import glob, os, sys, time
from PyPDF4 import PdfFileMerger
from datetime import datetime, timedelta
from getPdfInfo import DocInfo
from getJpgInfo import ImgInfo


def main(srcFolderPath, mergFolderPath):
    # Get info from pdf files
    print('%s  Getting information from files...' % datetime.now().strftime('%m/%d %H:%M'))
    lsPdfs = glob.glob(os.path.join(srcFolderPath, '*.pdf'))
    lsPdfInfos = []
    for pdfFilePath in lsPdfs:
        pdfInfo = DocInfo()
        readSuccess = pdfInfo.getInfo(pdfFilePath)
        if readSuccess:
            lsPdfInfos.append(pdfInfo)
    if len(lsPdfInfos) <= 1:
        print('%s  No pdf file available to merge currently' % datetime.now().strftime('%m/%d %H:%M'))
        return
    # Get info from jpg files
    lsJpgs = glob.glob(os.path.join(srcFolderPath, '*.jpg'))
    lsJpgInfos = []
    for jpgFilePath in lsJpgs:
        jpgInfo = ImgInfo()
        readSuccess = jpgInfo.getInfo(jpgFilePath)
        if readSuccess:
            lsJpgInfos.append(jpgInfo)
    # Merge brachy plan files
    for pdfInfo in lsPdfInfos:
        if pdfInfo.type == 'plandocOncentra':  # find the Oncentra plan file
            # find all files that match the same patient name
            ptPdfInfos = [pdfInfo]
            ptPdfInfos.extend([info for info in lsPdfInfos if
                               info.patient == pdfInfo.patient and info.type != 'plandocOncentra'])
            ptJpgInfos = [info for info in lsJpgInfos if info.patient.lower() == pdfInfo.patient.lower()]
            print('%s  Found %i pdf files and %i jpg file(s) for patient %s.'
                  % (datetime.now().strftime('%m/%d %H:%M'), len(ptPdfInfos), len(ptJpgInfos), pdfInfo.patient))
            if len(ptPdfInfos) > 1 and len(ptJpgInfos) > 0:
                mergeBrachyPlanFile(ptPdfInfos, ptJpgInfos, mergFolderPath)
            else:
                print('%s  --Not enough files are present for merge.' % datetime.now().strftime('%m/%d %H:%M'))


def mergeBrachyPlanFile(ptPdfInfos, ptJpgInfos, mergFolderPath):
    patient = ptPdfInfos[0].patient
    print('%s  Start creating plan for patient %s.' % (datetime.now().strftime('%m/%d %H:%M'), patient))
    mergFilePath = os.path.join(mergFolderPath, patient + '.pdf')
    if os.path.isfile(mergFilePath):
        print('%s  --The merged file already exists in %s.' % (datetime.now().strftime('%m/%d %H:%M'), mergFilePath))
        return
    findPlnFile = False
    findDVHFile = False
    find2ndCalcFile = False
    findImgFile = False
    mergPdf = PdfFileMerger(strict=False)
    # find Oncentra plan
    pdfInfo = next((info for info in ptPdfInfos if info.type == 'plandocOncentra'), None)
    if pdfInfo is not None:
        plnTime = pdfInfo.printTime
        findPlnFile = True
        mergPdf.append(pdfInfo.fileName)
    if findPlnFile == False:
        print('%s  --Cannot find the plan file.' % datetime.now().strftime('%m/%d %H:%M'))
        mergPdf.close()
        return
    # find Oncentra DVH plan
    for pdfInfo in ptPdfInfos:
        if pdfInfo.type == 'DVHOncentra':
            if abs(plnTime - pdfInfo.printTime) < timedelta(hours=5):
                findDVHFile = True
                mergPdf.append(pdfInfo.fileName)
                break
    if findDVHFile == False:
        print('%s  --Cannot find the DVH file within 5 hours time frame.' % datetime.now().strftime('%m/%d %H:%M'))
        mergPdf.close()
        return
    # find plan image(s), can merge multiple images
    for imgInfo in ptJpgInfos:
        if abs(plnTime - imgInfo.modifiedTime) < timedelta(hours=5):
            imgFilePath = imgInfo.convertPdf()
            if imgFilePath:
                mergPdf.append(imgFilePath)
                findImgFile = True
    if findImgFile == False:
        print('%s  --Cannot find the image file within 5 hours time frame.' % datetime.now().strftime('%m/%d %H:%M'))
        mergPdf.close()
        return
    # find 2nd check
    for pdfInfo in ptPdfInfos:
        if pdfInfo.type == '2ndchkbrachy':
            if abs(plnTime - pdfInfo.printTime) < timedelta(hours=24):
                find2ndCalcFile = True
                mergPdf.append(pdfInfo.fileName)
                break
    if find2ndCalcFile == False:
        print('%s  --Cannot find the 2nd check file within 1 day time frame.' % datetime.now().strftime('%m/%d %H:%M'))
        mergPdf.close()
        return
    try:
        mergPdf.write(mergFilePath)
        print('%s  --Merged plan completed.' % datetime.now().strftime('%m/%d %H:%M'))
        mergPdf.close()
    except:
        print('%s  --Fail to save merged plan file.' % datetime.now().strftime('%m/%d %H:%M'))
        return


if __name__ == '__main__':
    folderCurr = os.getcwd()
    settingFile = os.path.join(folderCurr, 'mergePdfSetting.txt')  # read the source folder from setting file
    try:
        filePtr = open(settingFile, 'r')
        folderSrc = filePtr.readline()
        filePtr.close()
    except:
        print('%s  Cannot read source folder from %s.' % (datetime.now().strftime('%m/%d %H:%M'), settingFile))
        os.system('pause')
        sys.exit()
    while True:
        if not os.path.isdir(folderSrc):  # if source folder doesn't exist, exit
            print('%s  source folder %s does not exist.' % (datetime.now().strftime('%m/%d %H:%M'), folderSrc))
            os.system('pause')
            sys.exit()
        folderMerge = os.path.join(folderSrc, 'MergePlans')  # create folder for merged plan document
        if not os.path.isdir(folderMerge):
            print('%s  %s does not exist, create folder.' % (datetime.now().strftime('%m/%d %H:%M'), folderMerge))
            os.mkdir(folderMerge)
        main(folderSrc, folderMerge)
        time.sleep(120)
    sys.exit()
