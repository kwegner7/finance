'''
    CsvProcessorBase
'''

import csv, os, glob, re, io, commands
from helper import Container
from abc import ABCMeta

###############################################################################
# allow access to these internal items
############################################################################### 
__all__ = \
[
    "CsvFolder",
    "CsvObject",
    "CsvStandardDialect",
    "CsvBackquoteDialect",
    "FolderOfCsvObjects",
]

ConstructorParameter = None
StateVariable        = None
PureVirtual          = None
DefaultVirtual       = None
Const                = None

###############################################################################
# dialect
###############################################################################
class CsvStandardDialect(csv.Dialect):

    # constants
    delimiter = ','
    doublequote = True
    escapechar = None
    lineterminator = '\r\n'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = False
    
    # constructor
    def __init__(self):        
        csv.Dialect.__init__(self)       
        return None

###############################################################################
# dialect
###############################################################################
class CsvBackquoteDialect(csv.Dialect):

    # constants
    delimiter = '`'
    doublequote = True
    escapechar = None
    lineterminator = '\r\n'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = False

    # constructor              
    def __init__(self):        
        csv.Dialect.__init__(self)       
        return None
 
###############################################################################
# CsvFolder
###############################################################################
class CsvFolder():

    # constructor
    def __init__(self, 
        folder,
        fieldnames, 
        dialect = CsvBackquoteDialect(),
        skip_first_record = False): 
               
        self.folder = folder
        self.fieldnames = fieldnames
        self.dialect = dialect
        self.skip_first_record = skip_first_record
        pass
     
###############################################################################
# CsvObject
###############################################################################
class CsvObject():
    __metaclass__ = ABCMeta

    # static    
    rdescriptor = StateVariable
    wdescriptor = StateVariable
    reader      = StateVariable
    writer      = StateVariable

    # constructor
    def __init__(self, 
        filename, fieldnames, 
        dialect=CsvBackquoteDialect(), skip_first_record=False): 
               
        self.filename = filename
        self.fieldnames = fieldnames
        self.dialect = dialect
        self.skip_first_record = skip_first_record
        self.folder = os.path.dirname(self.filename)
        #print 'FOLDER IS', self.folder
        return None
        
    def numberOfRows(self):
        number_lines = commands.getoutput("wc --lines "+self.filename+" | cut -d' ' -f1")
        return number_lines
        
    def numberOfFieldss(self):
        with open(self.filename, 'rb') as csvfile:
            likely_dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect=likely_dialect)
            i = 0; number_of_fields = 0;
            # find the third row of the file and determine its length
            for row in reader:
                if i == 2:
                    number_of_fields = len(row)
                i = i+1
        return number_of_fields, likely_dialect

    def text(self):
        number_of_cols, likely_dialect = self.numberOfFields() 
        number_of_rows = self.numberOfRows()
        print "    CSV file:", self.filename
        print "        has", number_of_rows, "rows and", number_of_cols, "columns,",
        print "its delimiter is", likely_dialect.delimiter
        return
              
    def text0(self):
        print self.filename
        print self.fieldnames
        print self.dialect

    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def openReadList(self):
        if (self.rdescriptor==None
        or  self.rdescriptor.closed):
            self.rdescriptor = open(self.filename, 'rb')            

            self.reader = csv.reader(
                self.rdescriptor,
                dialect=self.dialect)

            if False: self.reader = csv.DictReader(
                self.rdescriptor,
                fieldnames=self.fieldnames,
                dialect=self.dialect)
            
            if self.skip_first_record:
                self.reader.next()
        else:
            print "ERROR: trying to open file already open (openRead)"
        return None

    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def openRead(self):
        if (self.rdescriptor==None
        or  self.rdescriptor.closed):
            self.rdescriptor = open(self.filename, 'rb')            

            self.reader = csv.DictReader(
                self.rdescriptor,
                fieldnames=self.fieldnames,
                dialect=self.dialect)
            
            if self.skip_first_record:
                self.reader.next()

        else:
            print "ERROR: trying to open file already open (openRead)"
        return None

    # fixed method                
    def openWrite(self):        
        folder = os.path.dirname(self.filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)    
        if (self.wdescriptor==None
        or  self.wdescriptor.closed):
            self.wdescriptor = open(self.filename, 'wb')
            self.writer = csv.writer(
                self.wdescriptor,
                dialect=self.dialect)
        else:
            print "ERROR: trying to write to file already open (openWrite)"
        return None

    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def openAppend(self):        
        folder = os.path.dirname(self.filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)    
        if (self.wdescriptor==None
        or  self.wdescriptor.closed):
            self.wdescriptor = open(self.filename, 'ab', newline='')
            self.writer = csv.writer(
                self.wdescriptor,
                dialect=self.dialect )
        else:
            print "ERROR: trying to write to file already open (openAppend)"
        return None

    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def openAppend(self):        
        folder = os.path.dirname(self.filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)    
        if (self.wdescriptor==None
        or  self.wdescriptor.closed):
            self.wdescriptor = open(self.filename, 'ab')
            self.writer = csv.writer(
                self.wdescriptor,
                dialect=self.dialect )
        else:
            print "ERROR: trying to write to file already open (openAppend)"
        return None

    # fixed method                
    def openWriteAnother(self, another): 
        folder = os.path.dirname(another)
        if not os.path.isdir(folder):
            os.makedirs(folder)    
        descriptor = open(another, 'wb', newline='')
        writer = csv.writer(descriptor, dialect=self.dialect )
        return writer, descriptor
        
    # fixed method                
    def closeRead(self):        
        self.rdescriptor.close()
        return None            
    def closeWrite(self):        
        self.wdescriptor.close()
        return None

    # public
    def copySomeFieldsMinimizeWhitespace(self, rows_out):
        rows_in = self
        rows_in.openRead(); rows_out.openWrite()
        for row in rows_in.reader:
            rows_out.writer.writerow([ String(row[x]).whiteSpaceToBlank()
                for x in rows_out.fieldnames])
        rows_in.closeRead(); rows_out.closeWrite()
        return rows_out

    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def copySomeFields(self, rows_out):
        self.openReadDict(); rows_out.openWrite()
        for row in self.reader:
            fields_out = [row[x] for x in rows_out.fieldnames]
            rows_out.writer.writerow(fields_out)
        self.closeRead(); rows_out.closeWrite()
        return rows_out
    
    # THIS WAS MODIFIED TO FIX SPECIAL CAMP DBG         
    def copySomeFields(self, rows_out):
        self.openRead(); rows_out.openWrite()
        for row in self.reader:
            fields_out = [row[x] for x in rows_out.fieldnames]
            rows_out.writer.writerow(fields_out)
        self.closeRead(); rows_out.closeWrite()
        return rows_out
    
    # public
    def appendSomeFields(self, rows_out):
        print "    Appending records from", self.filename
        print "                        to", rows_out.filename
        self.openRead(); rows_out.openAppend()
        for row in self.reader:
            fields_out = [row[x] for x in rows_out.fieldnames]
            rows_out.writer.writerow(fields_out)
        self.closeRead(); rows_out.closeWrite()
        return rows_out
        
###############################################################################
# FolderOfCsvObjects
###############################################################################
class FolderOfCsvObjects():

    def __init__(self,  fullpath_out, originals):
              
        self.originals = originals
        self.folder_in = self.originals.folder
        self.fullpath_out = fullpath_out      
        self.folder_out = os.path.dirname(fullpath_out)
        self.combined_csv_object = CsvObject(
            self.fullpath_out, self.originals.fieldnames)
        pass

    # private
    def appendCsvObject(self,
        csv_object_receiving, csv_filename_to_append, please_capitalize=False):
  
        rows_in = CsvObject(
            csv_filename_to_append,
            self.originals.fieldnames,
            self.originals.dialect,
            self.originals.skip_first_record)
        rows_out  = csv_object_receiving

        rows_in.openRead(); rows_out.openAppend()
        for row in rows_in.reader:
            if please_capitalize:
                capitalized_row =[
                    String(row[x]).whiteSpaceToBlankAndCapitalize()
                    for x in rows_out.fieldnames ]
                rows_out.writer.writerow(capitalized_row)
            else:
                rows_out.writer.writerow([
                    String(row[x]).whiteSpaceToBlank()
                    for x in rows_out.fieldnames ])
        rows_in.closeRead(); rows_out.closeWrite()
        return rows_out

    # public
    def combineIntoOneCsvObject(self, please_capitalize=False):
        if False: print 'Combining .csv files from the folder', self.folder_in
        for next_csv_filename in glob.glob(self.folder_in + '*.csv'):
            print "   ", next_csv_filename
            self.combined_csv_object = self.appendCsvObject(
                self.combined_csv_object, next_csv_filename, please_capitalize)
            pass
        temp_csv = re.sub('.csv$', '.tmp', self.fullpath_out)
        #ShellCommand( 'sort -u ' + self.combined_csv_object.filename 
        #    ).redirect(temp_csv)
        if os.access(self.combined_csv_object.filename, os.F_OK):
            os.remove(self.combined_csv_object.filename)
        os.rename(temp_csv, self.combined_csv_object.filename)
        if False: print 'The    combined .csv file is', self.combined_csv_object.filename
        return self.combined_csv_object
    
    
