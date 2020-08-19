# -*- getPdfInfo.py -*- #
"""
SYNOPSIS
    obtain information from a pdf file

DESCRIPTION
    description of the functions
   
EXAMPLES
    examples of each function

VERSION 0.0
AUTHOR
    Becket Hui 2020 07
    
"""
import os, sys
import PyPDF4 as pdf
from datetime import datetime


class DocInfo:
    """
    class of info of the pdf doc
    """
    def __init__(self):
        self.fileName = ''
        self.type = ''
        self.patient = ''
        self.plan = ''
        self.printTime = datetime(datetime.now())


def getInfo(filePath):
    try:
        doc = pdf.PdfFileReader(filePath)
    except:
        print(filePath + ' cannot be loaded, skipped...\n')
        return None
    NPage = doc.getNumPages()
    pgNow = doc.getPage(0)
    textNow = pgNow.extractText()