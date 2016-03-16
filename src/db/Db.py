'''
    Db
'''

import os, csv, tempfile, commands, sys, hashlib, shutil
from datetime import datetime
from helper import Container
import db
from db import CsvObject
from abc import ABCMeta, abstractmethod
from apt_pkg import md5sum

__all__ = list()

#=========================================================================
# class MonitorField
#=========================================================================
class MonitorField():
    
    def __init__(self):
        self.reset()
        pass

    def reset(self):
        self.first_time = True
        self.prev_fields = None
        self.current_fields = None
        self.next_fields = None
        return

    def slideFieldValues(self, row, row_next):
        if self.first_time:
            self.first_time = False
        else:
            self.prev_fields = self.current_fields
        self.current_fields = row
        self.next_fields = row_next
        return
 
    # The first time this is invoked, "row" is row 1, "row_next" is row 2.
    # When current "row" is:
    #                                          last time     outside
    #                row1     row2     row3      in loop     loop
    #    prev    None --> None --> row1 --> row2 ... row n-2 --> row n-1
    #    current None --> row1 --> row2 --> row3 ... row n-1 --> row n
    #    next    None --> row2 --> row3 --> row4 ... row n   --> None
    #
    # First time, when "row" is row 1 we force this to return True (has changed) on row 1
    # When "row" is row n this will correctly test row n-1 vs. row n

    def fieldsHaveChanged(self, list_of_fields):
        if self.prev_fields == None: return True # has changed from nothing to something
        for field in list_of_fields:
            if (field in self.prev_fields.keys()
            and field in self.current_fields.keys()):
                if (self.prev_fields[field] != self.current_fields[field]):
                    return True
        return False

    def fieldWillChange(self, field):
        if self.current_fields == None: return True
        if self.next_fields == None: return True
        return (self.current_fields[field] != self.next_fields[field])
 
    # The first time this is invoked, "row" is row 1, "row_next" is row 2.
    # When current "row" is:
    #                                          last time     outside
    #                row1     row2     row3      in loop     loop
    #    prev    None --> None --> row1 --> row2 ... row n-2 --> row n-1
    #    current None --> row1 --> row2 --> row3 ... row n-1 --> row n
    #    next    None --> row2 --> row3 --> row4 ... row n   --> None
    #
    # First time, when "row" is row 1 this will correctly test row 1 vs. row 2
    # When "row" is row n this test row n vs. itself so returns False
    # so we force it to return True (fields will change)

    def fieldsWillChange(self, list_of_fields):
        if self.next_fields == None: return True # will change from something to nothing
        for field in list_of_fields:
            if (field in self.next_fields.keys()
            and field in self.current_fields.keys()):
                if (self.current_fields[field] != self.next_fields[field]):
                    return True
        return False
                
#===============================================================================
# class Scripts
#===============================================================================
class Scripts():

    @classmethod    
    def timeStampFile(cls, folder):

        if not os.path.exists(folder) or not os.path.isdir(folder): 
            print "The folder to timestamp does not exist", folder
            return

        text = datetime.now().strftime('Updated on %Y-%m-%d at %H:%M:%S')   
        new_file = os.path.join(folder, text) 
        
        # find a file under this folder that matches "Updated on"
        original_file = str('')
        for item in os.listdir(folder):
            fullpath = os.path.join(folder, item)
            if os.path.isfile(fullpath):
                if (item.startswith('Updated on ')
                and item.startswith(' at ',21)):
                    original_file = fullpath
                            
        # append timestamp to the end of the file and rename the file
        if len(original_file) == 0:
            with open(new_file, "w") as timestamp:
                timestamp.write(text+'\n')
        else:
            os.rename(original_file, new_file)
            with open(new_file, "a") as timestamp:
                timestamp.write(text+'\n')
        return
            

    @classmethod    
    def importPictures(cls, picture_tree, flat_folder):

        if False:
            folder = '/media/kurt/Linux3TB/pictures/Kurts-Blue-Nikon/SD1'
            Scripts.timeStampFile(folder)
        
        if not os.path.exists(picture_tree): 
            print "The import tree does not exist", picture_tree
            return
        
        if not os.path.exists(flat_folder): 
            print "The destination folder does not exist", flat_folder
            return

        # The existing destination flat folder to receive the pictures        
        flat_folder_csv = SetOfFiles.generateCsvSetOfFiles(flat_folder)
        existing_files = SetOfFiles(flat_folder_csv)
        existing_files.internalize()

        # This source folder is the base of a tree containing pictures
        picture_tree_csv = SetOfFiles.generateCsvSetOfFiles(picture_tree)
        importing_files = SetOfFiles(picture_tree_csv)
        importing_files.collectFilesIntoFolder(existing_files, flat_folder)

        print "DONE"
        return
    
#===============================================================================
# DbClasses
#===============================================================================
class DbClasses(CsvObject.CsvObject):
    
    #===========================================================================
    # Accumulation
    #===========================================================================
    class Accumulation():
   
        # class data    
        monitor = MonitorField()
        
        @classmethod    
        def reset(cls):
            cls.monitor.reset()
            return
    
        @classmethod    
        def slideRows(cls, row, row_next):
            cls.monitor.slideFieldValues(row, row_next)
            return
    
        @classmethod    
        def fieldsHaveChanged(cls, list_of_fields):
            return cls.monitor.fieldsHaveChanged(list_of_fields)
    
        @classmethod    
        def fieldsWillChange(cls, list_of_fields):
            return cls.monitor.fieldsWillChange(list_of_fields)
                           
        @abstractmethod
        def accumulate(): pass
            
        @abstractmethod
        def get(): pass
    
    class Count(Accumulation):
    
        def __init__(self, fields):
            self.fields = fields
            self.count = 0
    
        def get(self):
            return str(self.count)
    
        def accumulate(self, row):
            if self.fieldsHaveChanged(self.fields):
                self.count = 1
            else:
                self.count += 1 
            return self.get()
    
    class Total(Accumulation):
    
        def __init__(self, fields):
            self.fields = fields
            self.total = 0.00
    
        def get(self):
            if self.fieldsWillChange(self.fields):
                return Container.formatDollars(self.total)
            else:
                return Container.formatDollars(self.total)
                return '&nbsp;'
            return Container.formatDollars(self.total)
    
        def accumulate(self, row):
            amount = row['Amount']
            if self.fieldsHaveChanged(self.fields):
                self.total = Container.getFloatNoCommas(amount)
            else:
                self.total += Container.getFloatNoCommas(amount) 
            return self.get()
    
    class Credit(Accumulation):
    
        def __init__(self, fields):
            self.fields = fields
            self.total = 0.00
    
        def get(self):
            return Container.formatDollars(self.total)
        
        def accumulate(self, row):
            amount = row['Amount']
            money = Container.getFloatNoCommas(amount)
            if self.fieldsHaveChanged(self.fields):
                if money >= 0.0: self.total = money
                else:            self.total = 0.0
            else:
                if money >= 0.0: self.total += money
            return self.get()
        
    
    class Debit(Accumulation):
    
        def __init__(self, fields):
            self.fields = fields
            self.total = 0.00
    
        def get(self):
            return Container.formatDollars(self.total)
        
        def accumulate(self, row):
            amount = row['Amount']
            money = Container.getFloatNoCommas(amount)
            if self.fieldsHaveChanged(self.fields):
                if money < 0.0: self.total = money
                else:           self.total = 0.0
            else:
                if money < 0.0: self.total += money
            return self.get()
    
    class Collapse(Accumulation):
    
        def __init__(self, fields):
            self.fields = fields
            self.fields_empty = (len(self.fields) == 0)
    
        def get(self):
            return True
    
        def accumulate(self, row):
            if self.fields_empty:
                return True # write the row
            if self.fieldsWillChange(self.fields):
                return True
            else:
                return False

#===============================================================================
# DbMethods
#===============================================================================
class DbMethods(DbClasses):

    def checkClass(self, obj, superclass, classname):
        #print "    Transforming to columns of type ", superclass.__name__, "from columns of type ", classname.__name__
        if not isinstance(obj, classname):
            try:
                raise Exception('ERROR: Object Class Should Be '+classname.__name__)
            except Exception as msg:
                print msg
        return              

    @classmethod    
    def temporaryCsvFile(self):
        os.system ("mkdir --parents /tmp/csv")
        return tempfile.NamedTemporaryFile(
            delete=True,prefix='CSV-',suffix='.csv',dir='/tmp/csv/').name
        
    def copyCsvFile(self, original_csv_file, internal_csv_file):
        os.system("cp "+original_csv_file+" "+internal_csv_file)        
        return

    def numberOfRows(self):
        number_lines = commands.getoutput("wc --lines "+self.filename+" | cut -d' ' -f1")
        return number_lines

    def seemsToHaveHeader(self, filename, dialect):
        with open(filename, 'rb') as csvfile:
            likely_dialect = csv.Sniffer().sniff(csvfile.read(1024),delimiters=dialect.delimiter)
            has_header = csv.Sniffer().has_header(csvfile.read(1024))
        return has_header

    def delimiterSeemsToBe(self, filename):
        with open(filename, 'rb') as csvfile:
            likely_dialect = csv.Sniffer().sniff(csvfile.read(1024),delimiters=self.dialect.delimiter)
        return likely_dialect.delimiter
                
    def numberFields(self, filename, dialect):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, dialect=dialect)
            i = 0; number_of_fields = 0;
            for row in reader:
                i = i+1
                if i == 1:
                    check = len(row)
                number_of_fields = len(row)
                if check != number_of_fields:
                    #print "BAD ROW:",row
                    return False, number_of_fields
        return True, number_of_fields

    def checkCsvFile(self, filename, format):
        return
        number_columns_ok, number_columns = \
            self.numberFields(filename, format.dialect)
        dialect = format.dialect
        has_header = format.skip_first_record
        seems_to_have_header = self.seemsToHaveHeader(filename, dialect)
        should_have_header = has_header and not seems_to_have_header
        should_not_have_header = not has_header and seems_to_have_header
        if should_not_have_header:
            print "ERROR: CSV file has header but should not"
        if should_have_header:
            print "ERROR: CSV file should have header but does not" 
        if not number_columns_ok:
            print "ERROR: Number of columns in csv is not consistent" 
        if len(self.fieldNames()) != number_columns:
            print "ERROR: Number of columns in csv does not match number fields specified"
        return

    def sniffTheCsv(self, filename):
        with open(filename, 'rb') as csvfile:
            likely_dialect = csv.Sniffer().sniff(csvfile.read(1024),delimiters=self.dialect().delimiter)
            has_header = csv.Sniffer().has_header(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect=likely_dialect)
            i = 0; number_of_fields = 0;
            # find the third row of the file and determine its length
            for row in reader:
                i = i+1
                if i == 3:
                    number_of_fields = len(row)
                    break
        return number_of_fields, has_header

    def printAppend(self, db_in, db_out):
        printit = \
            "    Appending    {1:>2d}/{2:>4s}/{3} {0:<20s} to {5:>2d}/{6:>4s}/{7} {4:<20s} {8}".format(
                type(db_in).__name__,
                len(db_in.fieldnames),
                db_in.numberOfRows(),
                db_in.dialect.delimiter,
                type(db_out).__name__, 
                len(db_out.fieldnames),
                db_out.numberOfRows(),
                db_out.dialect.delimiter,
                db_out.filename,
                )
        print printit
        return              
        
    def append(self, other_db):
        self.printAppend(other_db, self)        
        if len(self.fieldnames) != len(other_db.fieldnames):
            print "ERROR: APPENDING FILES WITH DIFFERING COLUMNS"
        command = 'cat ' + self.filename + " " + other_db.filename + " > " + '/tmp/bb.csv'
        os.system(command)        
        command = 'cat /tmp/bb.csv > ' + self.filename
        os.system(command)
        return

    def append_unique(self, other_db):
        if len(self.fieldnames) != len(other_db.fieldnames):
            print "ERROR: APPENDING FILES WITH DIFFERING COLUMNS"
        command = 'cat ' + self.filename + " " + other_db.filename + " | sort -u > " + '/tmp/bb.csv'
        os.system(command)        
        command = 'cat /tmp/bb.csv > ' + self.filename
        os.system(command)        
        return

    def export(self, export_csv):
        os.system('mkdir --parents $(dirname ' + export_csv + ')')
        os.system('cat ' + self.filename + ' > ' + export_csv)
        print "    Exporting CSV file to", export_csv 
        
    #def sectionChange(self): return list([])         

    #def subsectionChange(self): return list([])

    def pages(self, dirpath = Container.temporaryFolder()):
        #print "pages", dirpath
        self.htmlPresentation(dirpath)
        return 
        
    def text(self, prepend="", append=""):
        printit = \
            "CSV {0:>2d}/{1:>4s}/{2} {3}".format(
                len(self.fieldnames),
                self.numberOfRows(),
                self.dialect.delimiter,
                self.filename)
        print prepend + printit + append
        return 
                
    def reorderRows(self, fieldnames, sort_order):
        setA = set(fieldnames)
        setB = set(sort_order)
        setC = setA - setB
        fieldnames = sort_order + list(setC)
        return fieldnames
        
    #===========================================================================
    # Specify how to transform from the input Db to this Db
    #===========================================================================
    def printReorder(self):
        printit = \
            "    Reordering   {1:>2d}/{2:>4s}/{3} {0:<20s} to {1:>2d}/{2:>4s}/{3} {0:<20s} {4}".format(
                type(self).__name__,
                len(self.fieldnames),
                self.numberOfRows(),
                self.dialect.delimiter,
                self.filename,
                )
        print printit
        return 
            

    def printTransform(self, db_in, db_out):
        printit = \
            "    Transforming {1:>2d}/{2:>4s}/{3} {0:<20s} to {5:>2d}/{6:>4s}/{7} {4:<20s} {8}".format(
                type(db_in).__name__,
                len(db_in.fieldnames),
                db_in.numberOfRows(),
                db_in.dialect.delimiter,
                type(db_out).__name__, 
                len(db_out.fieldnames),
                db_out.numberOfRows(),
                db_out.dialect.delimiter,
                db_out.filename,
                )
        print printit
        return              

    def reorderCsvFile(self, sort_order, temp_csv_file):
        order = [self.fieldnames.index(x)+1 for x in sort_order]
        dash_key = [' --key='+str(x)+','+str(x) for x in order]
        all_keys = str()
        for next in dash_key:
            all_keys += next
        command = str( 
            "sort --field-separator='`' " + all_keys + 
            " --output=" + temp_csv_file + " "+ self.filename +
            " "
            )
        os.system( command )
        return

#===============================================================================
# Db (may be instantiated)
#    The characteristics of a Db file are:
#        File Name
#        Field Names
#        Delimiter
#        Does the Db file have a header?
#        Number of columns (should be size of Field Names)
#        Number of rows
#        Content of each cell (row, column)
#
#
#  Db - instantiable
#        Original - abstract, requires fieldNames
#                MapImport - abstract, requires fieldNames, rowContainsKey
#        Transformer - abstract, requires fieldNames, isSelectedRow, transform
#                Essence - abstract, requires fieldNames, transform
#                Model - abstract, requires fieldNames, transform
#                View - abstract, requires fieldNames, isSelectedRow, transform
#                      def initializeTransform(self): pass
#                      def sortBeforeTransform(self): pass 
#                      def sortAfterTransform(self): pass 
#                      def subsectionChange(self): pass
#                      def sectionChange(self): pass
#                      def htmlPresentation(self, dirpath): pass
#                        MapGenerate
#===============================================================================

#===============================================================================
# Db
#===============================================================================
__all__ += ['Db']
class Db(DbMethods):
    
    def __init__(self, filename, fieldnames, dialect, skip_first_record): 
        CsvObject.CsvObject.__init__(self, 
            filename, fieldnames, dialect, skip_first_record)
    
    #===========================================================================
    # const class CsvFormat
    #===========================================================================
    class CsvFormatStandard():
        dialect = CsvObject.CsvStandardDialect()
        skip_first_record = True
                
    class CsvFormatBackquote():
        dialect = CsvObject.CsvBackquoteDialect()
        skip_first_record = False

#===============================================================================
# Abstract Methods
#===============================================================================
__all__ += ['Abstract']
class Abstract():
    __metaclass__ = ABCMeta

class TransformerAbstract(Abstract):

    @abstractmethod
    def isSelectedRow(self, row): pass
    
    @abstractmethod
    def fieldNames(self): pass

    @abstractmethod
    def initializeTransform(self): pass
    
    @abstractmethod
    def sortBeforeTransform(self): pass 

    @abstractmethod
    def transform(self, this_row, next_row): pass
    
    @abstractmethod
    def sortAfterTransform(self): pass 
    
    @abstractmethod
    def collapseOnFields(self): pass 
       

#===============================================================================
# Transformer (abstract)
#    The constructor transforms one type of Db to another type of Db
#===============================================================================
__all__ += ['Transformer']
class Transformer(Db, TransformerAbstract):
    
    # constructor
    def __init__(self, db_in, format=Db.CsvFormatBackquote):
        Db.__init__(self, 
            self.temporaryCsvFile(),
            self.fieldNames(),
            format.dialect,
            format.skip_first_record)
        self.forEachRow(db_in)

    def process(self, row, row_next):
        Db.Accumulation.slideRows(row, row_next)
        please_write_row, row_out = self.transform(row, row_next)
        if please_write_row and self.isSelectedRow(row_out):
            self.writer.writerow([row_out[x] for x in self.fieldnames])
        return row_out
                
    # common
    def forEachRow(self, db_in):
        
        # possibly reorder before transform        
        if len(self.sortBeforeTransform()) != 0:
            temp_csv_file = self.temporaryCsvFile()
            db_in.reorderCsvFile(self.sortBeforeTransform(), temp_csv_file)
            db_in.filename = temp_csv_file
            db_in.printReorder()
        
        # transform
        first_time = True
        Db.Accumulation.reset() 
        self.initializeTransform()
        db_in.openRead(); self.openWrite();
        for row_next in db_in.reader:
            if first_time:
                first_time = False
                self.first_row = row_next
            else: self.process(row, row_next)
            row = row_next
        row_out = self.process(row_next, None)
        self.last_row = row_next
        db_in.closeRead(); self.closeWrite();
        if False and 'Date' in self.first_row.keys():
            print "FIRST ROW IS:", self.first_row['Date']
            print "LAST ROW IS:", self.last_row['Date']
        
        self.printTransform(db_in, self)
        if set(row_out.keys()) != set(self.fieldnames):
            print "ERROR: Transform method is not producing correct fields" 
            print "Producing", row_out.keys()
            print "Expected", self.fieldnames
        
        # possibly reorder after transform        
        if len(self.sortAfterTransform()) != 0:
            self.reorderCsvFile(self.sortAfterTransform(), self.filename)
            self.printReorder()
        
        return None

#===============================================================================
# Essence (abstract)
#    The constructor transforms an Original Db into the essential fields
#    that are expected by the Model Db
#===============================================================================
__all__ += ['Essence']
class Essence(Transformer):

    def isSelectedRow(self, row): return True
    
    def initializeTransform(self): return

    def sortBeforeTransform(self): return list([])
    
    def sortAfterTransform(self): return list([])

    def collapseOnFields(self): return list([])

    # constructor
    def __init__(self, db_in, format=Db.CsvFormatBackquote):
        Transformer.__init__(self, db_in, format)

#===============================================================================
# Model (abstract)
#    The constructor transforms an Essence Db by expanding the fields to be
#    useful to many Views of the Model Db.
#===============================================================================
__all__ += ['Model']
class Model(Transformer):
        
    def isSelectedRow(self, row): return True
    
    def initializeTransform(self): return

    def sortBeforeTransform(self): return list([])
    
    def sortAfterTransform(self): return list([])

    def collapseOnFields(self): return list([])
                
    # constructor
    def __init__(self, db_in, format=Db.CsvFormatBackquote):
        Transformer.__init__(self, db_in, format)
        

#===============================================================================
# View (abstract)
#    The constructor transforms a Model Db by sorting and sectioning the
#    Model Db into a useful view of the database.
#===============================================================================
class ViewAbstract(Abstract):

    @abstractmethod
    def htmlPresentation(self, dirpath): pass

    @abstractmethod
    def sectionChange(self): pass
            
    @abstractmethod
    def subsectionChange(self): pass

__all__ += ["View"]
class View(Transformer, ViewAbstract):
 
    # constructor
    def __init__(self, master_db, format=Db.CsvFormatBackquote):
        if isinstance(master_db, Transformer):
            self.master_first_row = master_db.first_row
            self.master_last_row = master_db.last_row
        else:
            self.master_first_row = dict()
            self.master_last_row = dict()
        Transformer.__init__(self, master_db, format)
         
#===============================================================================
# Original (abstract)
#    The constructor imports a csv file based upon its known format and names
#    of fields, and converts to a new temporary file that is backquote csv with
#    identical column names. Has no ability to transform.
#===============================================================================
class OriginalAbstract(Abstract):

    @abstractmethod
    def fieldNames(self): pass

__all__ += ['Original']
class Original(Db, OriginalAbstract):

    # constructor
    def __init__(self, csv_file, format=Db.CsvFormatBackquote):
        self.checkCsvFile(csv_file, format)
        orig_db = Db(
            csv_file,
            self.fieldNames(),
            format.dialect,
            format.skip_first_record)  
        default_format = Db.CsvFormatBackquote
        Db.__init__(self, 
            self.temporaryCsvFile(),
            self.fieldNames(),
            default_format.dialect,
            default_format.skip_first_record)  
        self.forEachRow(orig_db)

    def forEachRow(self, orig_db):
        orig_db.openRead(); self.openWrite();
        for row in orig_db.reader:
            self.writer.writerow([row[x] for x in self.fieldnames])
        orig_db.closeRead(); self.closeWrite();
        return

#===============================================================================
# Reference (abstract)
#    This is a simple reference to a csv file, including its characteristics.
#===============================================================================
__all__ += ['Reference']
class Reference(Db, OriginalAbstract):

    # constructor
    def __init__(self, csv_file, format=Db.CsvFormatBackquote):
        Db.__init__(self, 
            csv_file,
            self.fieldNames(),
            format.dialect,
            format.skip_first_record)  
        self.checkCsvFile(self.filename, format)
 
#===============================================================================
# SetOfFiles
#===============================================================================
__all__ += ['SetOfFiles']
class SetOfFiles(Reference):
    
    def __init__(self, csv_file, format=Db.CsvFormatBackquote):
        Reference.__init__(self, csv_file, format)
        print "CONSTRUCTING SetOfFiles FROM THE CSV FILE", csv_file, "WITH FIELDS", self.fieldNames()
        #self.internalize()
        pass

    @classmethod    
    def generateCsvSetOfFiles(cls, top_folder):
        print "\nWALKING THE TREE", top_folder+",", "SEARCHING FOR PICTURES"
        csv_fullpath = DbMethods.temporaryCsvFile()
        csv = open(csv_fullpath, 'w')    
        for dirpath, dirnames, files in os.walk(top_folder):
            for name in files:
                if (name.lower().endswith('bmp')
                or  name.lower().endswith('gif')
                or  name.lower().endswith('jpg')
                or  name.lower().endswith('png')
                or  name.lower().endswith('tiff')):
                    row = dirpath+'`'+name+'\n'
                    csv.write(row)    
        csv.close()
        print "CSV FOLDER/FILE HAS BEEN GENERATED AT", csv.name 
        return csv_fullpath

    def getChecksum(self, fullpath):
        with open(fullpath) as file_to_check:
            data = file_to_check.read()    
            checksum = hashlib.md5(data).hexdigest()
        return checksum
            
    def internalize(self):
        print "READING CSV TO INTERNALIZE SET OF FILE CHECKSUMS"
        self.hash_set = set()
        self.openRead();
        for row in self.reader:
            fullpath = os.path.join(row['Folder'], row['File'])
            self.hash_set.add(self.getChecksum(fullpath))
        self.closeRead();
        return

    def collectFilesIntoFolder(self, flat_set_of_files, flat_folder, practicing=False):
        print "WRITING EACH FILE FROM THE TREE INTO THE FLAT FOLDER"
        hash_set = flat_set_of_files.hash_set
        original_number_flat_files = len(hash_set)
        count_tree_files = int(0)
        count_exists_already = int(0)
        count_duplicate_name = int(0)
        count_files_added = int(0)
        os.system("mkdir --parents "+flat_folder)
        self.openRead();
        for row in self.reader:
            count_tree_files += 1
            from_filename = os.path.join(row['Folder'], row['File'])
            to_filename = os.path.join(flat_folder, row['File'])
            checksum = self.getChecksum(from_filename)
            if checksum in hash_set:
                count_exists_already += 1
            elif os.path.exists(to_filename):
                count_duplicate_name += 1
                thru_name = os.path.splitext(to_filename)[0]
                dot_ext = os.path.splitext(to_filename)[1]
                new_filename = thru_name + '_' + checksum + dot_ext
                if not practicing:
                    shutil.copy2(from_filename, new_filename)
                hash_set.add(checksum)
            else:
                count_files_added += 1
                if not practicing:
                    shutil.copy2(from_filename, flat_folder)
                hash_set.add(checksum)
        self.closeRead();
        final_number_flat_files = len(hash_set)
        if not practicing and (final_number_flat_files > original_number_flat_files):
            Scripts.timeStampFile(flat_folder)
        print
        print "  {0:>6d} pictures originally in the destination flat folder".format(original_number_flat_files)
        print "  {0:>6d} pictures imported into the destination flat folder".format(count_files_added)
        print "  {0:>6d} pictures imported but renamed due to duplicate name".format(count_duplicate_name)
        print "  {0:>6d} pictures finally in the destination flat folder".format(final_number_flat_files)
        print
        print "  {0:>6d} pictures in the source tree trying to import".format(count_tree_files)
        print "  {0:>6d} pictures existed already in the destination folder".format(count_exists_already)
        print "  {0:>6d} pictures imported into the destination flat folder".format(count_files_added)
        print
        return

    def set_union(self, other_db):
        diff = SetOfFiles(self.temporaryCsvFile())   
        other_db.openRead(); diff.openWrite();
        for row in other_db.reader:
            fullpath = row['Folder']+'/'+row['File']
            checksum = self.getChecksum(fullpath)
            if not checksum in self.hash_set:
                diff.writer.writerow([row[x] for x in diff.fieldnames])
        other_db.closeRead(); diff.closeWrite();
        return diff
        
    def set_intersection(self, other_db):
        self.append(other_db)
        return
        
    def set_difference(self, other_db):
        self.append(other_db)
        return
        
    # an element of a database is an object
    # whose attributes are stored in a row of the csv file
    # we must transform row to object and object to row
    # Finance is a set of Transactions
    # SpecialCamp is a set of AdministerMeds
    # Jpg is a set of JPG picture files
    def isElementOfThisSet(self, row):
        return True

    def fieldNames(self): return list([
        #"Checksum",
        #"Date",
        #"Camera",
        "Folder",
        "File",
    ])
                    
                                                            
