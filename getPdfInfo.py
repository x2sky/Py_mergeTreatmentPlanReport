# -*- getPdfInfo.py -*- #
"""
SYNOPSIS
    obtain information from a pdf file

DESCRIPTION
    DocInfo - class that contains pdf file information
    DocInfo.getInfo - extract information from the pdf file
   
EXAMPLES
    examples of each function

VERSION 0.0
AUTHOR
    Becket Hui 2020 07
    
"""
import io, os, re, sys
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from datetime import datetime


class DocInfo:
    """
    class of info of the pdf doc
    """
    def __init__(self):
        self.fileName = ''
        self.NPg = 1
        self.type = 'unknown'
        self.patient = ''
        self.plan = ''
        self.printTime = datetime.now()
        self.fldN = 0

    def getInfo(self, filePath):
        try:
            filePointer = open(filePath, 'rb')
        except:
            print(filePath + ' cannot be loaded, skipped...\n')
            return False
        try:
            for pgN, page in enumerate(PDFPage.get_pages(filePointer, caching=True, check_extractable=True)):
                if pgN == 0:  # only extract first page
                    resource_manager = PDFResourceManager()
                    file_handler = io.StringIO()
                    converter = TextConverter(resource_manager, file_handler)
                    page_interpreter = PDFPageInterpreter(resource_manager, converter)
                    page_interpreter.process_page(page)
                    text = file_handler.getvalue()
            filePointer.close()
            self.fileName = filePath
            self.NPg = pgN + 1
        except:
            print(filePath + ' cannot be read as pdf, skipped...\n')
            filePointer.close()
            return False
        try:
            # look for keywords for doc type:
            if re.search('TREATMENT PLAN REPORT', text):
                self.type = 'plandocEclipse'
                match = re.search('IDs:([0-9]*)Birthdate', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('Plan ID:(.*?)Plan', text)
                if match:
                    self.plan = match.group(1)
                match = re.search('Printed (.*?) by', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%A, %B %d, %Y %I:%M:%S %p')
            elif re.search('microSelectron v3', text):
                self.type = 'plandocOncentra'
                match = re.search('ale[0-9]* .*? [0-9]*(.*?),', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('US Mountain Standard Time.*? by .*?([0-9]* [A-Z][a-z][a-z] [0-9]* [0-9]*:[0-9]*:[0-9]*) by', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%d %b %Y %H:%M:%S')
            elif re.search('DVHStructureStructure Status', text):
                self.type = 'DVHEclipse'
                match = re.search('Patient IDs:([0-9]*)Comment:', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('Plan History(.*?)C[0-9]', text)
                if match:
                    self.plan = match.group(1)
                match = re.search('Printed (.*?) by', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%A, %B %d, %Y %I:%M:%S %p')
            elif re.search('DVH values:', text):
                self.type = 'DVHOncentra'
                match = re.search('Patient name.*?(\W\w*?)Patient ID', text)
                if match:
                    self.patient = match.group(1).strip()
                match = re.search('Printed.*?([0-9]*-\w*-[0-9]* [0-9]*:[0-9]*:[0-9]*)Time zone', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%d-%b-%Y %H:%M:%S')
            elif re.search('Fields in plan', text):
                self.type = 'BEVEclipse'
                match = re.search('Patient Name:Course:Plan:.* \(([0-9]*)\)C', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('in plan \'(.*?)\' of', text)
                if match:
                    self.plan = match.group(1)
                match = re.search('Printed (.*?) by', text).group(1)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%A, %B %d, %Y %I:%M %p')
                match = re.search('Field \'(.*?)\' plotted at', text)
                if match:
                    self.fldN = match.group(1)
            elif re.search('ConstraintTemplate', text):
                self.type = 'clearchk'
                match = re.search('\(([0-9]*)\)BirthDate:', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('\)(.*?)PlanningApproved', text)
                if match:
                    self.plan = match.group(1)
                match = re.search('printedby.*?,.*?([0-9]*/[0-9*]/[0-9]*:[0-9]*:[0-9]*.*?)Page', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%m/%d/%Y%I:%M:%S%p')
            elif re.search('PhotonMonitor Unit Calc', text):
                self.type = '2ndchkLINAC'
                match = re.search('Patient ID\#:(.*?)Calculation Name', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('Calculation Name:(.*?)Comments', text)
                if match:
                    self.plan = match.group(1)
                match = re.search('Calculated By:.*? ([0-9]*/[0-9]*/[0-9]*)Checked By', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%m/%d/%Y')
            elif re.search('BrachytherapyDosimetric Verification', text):
                self.type = '2ndchkbrachy'
                match = re.search('Patient Name:(.*?), .*?Patient ID', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('Calculated By:.*? ([0-9]*/[0-9]*/[0-9]*)Checked By', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%m/%d/%Y')
            else:
                self.type = 'unknown'
                match = re.search('\(([0-9]*)\)', text)
                if match:
                    self.patient = match.group(1)
                match = re.search('Printed on (.*?) by', text)
                if match:
                    self.printTime = datetime.strptime(match.group(1), '%A, %B %d, %Y %I:%M:%S %p')
            return True
        except:
            return False
