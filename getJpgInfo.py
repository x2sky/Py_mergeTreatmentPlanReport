# -*- getJpgInfo -*- #
"""
SYNOPSIS
    obtain information from a jpg file, currently, designed for Oncentra screen capture only,
    which does not save any header info, so the procedure only gets info from file name & creation time

DESCRIPTION
    detail description including different functions
    
EXAMPLES
    examples of each function
    
VERSION 0.0
AUTHOR
    Becket Hui 2020 10
    
"""

import exifread, os, re, sys
from datetime import datetime
from PIL import Image

class ImgInfo:
    """
    class of info of the jpg image
    """
    def __init__(self):
        self.fileName = ''
        self.type = 'jpg'
        self.patient = ''
        self.modifiedTime = datetime.now()

    def getInfo(self, filePath):
        if os.path.isfile(filePath):
            try:
                im = Image.open(filePath)  # check if it is image file
                self.fileName = filePath
                self.type = im.format
                fName = os.path.basename(filePath)
                ptName = re.search('(.*?)sc.jpg', fName)  # use the file name ('ptname'sc.jpg) to determine pt name
                self.patient = ptName.group(1)
                self.modifiedTime = datetime.fromtimestamp(os.path.getmtime(filePath))
                return True
            except:
                return False
        else:
            return False

    def convertPdf(self):
        if not os.path.isfile(self.fileName):
            return False
        dirPath = os.path.dirname(self.fileName)
        fName = os.path.basename(self.fileName)
        savePdfName = os.path.splitext(fName)[0] + '.pdf'
        savePdfPath = os.path.join(dirPath, savePdfName)
        if os.path.isfile(savePdfPath):  # pdf file already exists
            return savePdfPath  # no need to do anything
        else:
            im = Image.open(self.fileName)
            im.save(savePdfPath, 'PDF', resolution=100.0)  # else save jpg as pdf
            return savePdfPath
