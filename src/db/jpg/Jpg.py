'''
    Jpg - the Model, Original
'''

#===============================================================================
# imports
#===============================================================================
from db import Db
from db.finance import View

#===============================================================================
# Field Names
#===============================================================================
class FieldNames():

    # 589967981e6a4fec07a18b195f35313a`
    # 2014-05-29`
    # Apple(iPad Air)`
    # /media/kurt/Windows/Users/Kurt/Pictures/2015-07-10/IMG_0014.JPG  
  
    original = model = list([
        "Checksum",
        "Date",
        "Camera",
        "Folder",
        "File",
    ])
        
#===============================================================================
# Conversion from Original Reference to the Model
#===============================================================================
class Model(Db.Model):
                
    def __init__(self, ref):
        Db.Model.__init__(self, ref)

    def fieldNames(self):
        return FieldNames.model

    def sortAfterTransform(self): 
        return list([ 'Date', 'File' ])

    def transform(self, this_row, next_row):
        return True, this_row
        
#===============================================================================
# This is simply a reference to a CsvObject with specified field names
#===============================================================================
class Original(Db.SetOfFiles):
                    
    def __init__(self, csv):
        Db.SetOfFiles.__init__(self, csv)

    def fieldNames(self):
        return FieldNames.original

class Diff(Db.Reference):
                    
    def __init__(self, csv):
        Db.Reference.__init__(self, csv)

    def fieldNames(self):
        return FieldNames.original

