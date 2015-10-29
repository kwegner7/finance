'''
    Map Db is an Original Db for making a csv map internal
'''
#===============================================================================
# imports
#===============================================================================
import abc, re
from db.Db import Db, Abstract, Reference

__all__ = list()
    
#===============================================================================
# MapImport is an Original so it does not perform a transformation between
# databases. Rather, the csv file is imported in a loop to become a map.
# The Original csv file has useful data in columns and and a single key field.
#===============================================================================
class MapImportAbstract(Abstract):
    
    @abc.abstractmethod
    def rowContainsKey(self, row): pass

class MapImport(Reference, MapImportAbstract):
                
    # constructor
    def __init__(self, db_in, format=Db.CsvFormatBackquote):
        Reference.__init__(self, db_in, format)

    # common
    def getFieldsFromMap(self, key):
        if key in self.map:
            return True, self.map[key]
        else:
            return False, dict()
        
    def insertKeyAndItem(self, map, key, item):
        map[key] = item
        return None 
        
    def forEachRow(self):
        map = dict()
        self.openRead();
        for row in self.reader:
            self.insertKeyAndItem(map, row[self.fieldNames()[0]], row)
        self.closeRead();
        return map  
        
    def searchForKeyAndObtainMapFields(self, row):                              
        row_contains_key, key = self.rowContainsKey(row)
        if row_contains_key:
            key_found, fields_from_map = self.getFieldsFromMap(key)
            if key_found:
                return True, fields_from_map 
            else:
                print "ERROR: Map Key Not Found:", key
        return False, dict() 
        

#===============================================================================
# ImportMapBillPay (may be instantiated)
#
#    Reads from the CSV file .../in/maps/billpay.csv
#    And creates an internal map:
#           BillPayId        AccountAlias
#            00880303    YEKOPE MINISTRIE00880303
#
#    In the AccountAlias field of a Mint DB, search for 0088dddd anywhere
#
#===============================================================================
__all__ += ['ImportMapBillPay']
class ImportMapBillPay(MapImport):

    # constructor
    def __init__(self, filename, format=Db.CsvFormatBackquote):
        MapImport.__init__(self, filename, format)
        self.map = self.forEachRow()

    # these are the columns of the DB map file     
    def fieldNames(self): return list([
        "BillPayId",
        "AccountAlias",
        "Date",
        "Amount",
        ])

    # when the csv file was downloaded from the Mint website
    # here is how to find the key     
    def rowContainsKey(self, row):
        key = str("KEYNOTFOUND")
        # PAYEE UNRECORDE00880568     
        eight_digits = '0088[0-9]{4}'
        find_pattern = '^.*' + eight_digits + '.*$'
        matches = re.match(find_pattern, row['AccountAlias'])
        if matches:
            key = re.findall(eight_digits, row['AccountAlias'])[0]
        return matches, key

#===============================================================================
# ImportMapCheckNumber (may be instantiated)
#    While processing a row from a Mint database, determine if this Mint row
#    has a check number in the form:
#        PAYEE UNRECORDE 761 from the field AccountAlias
#        Check 123 from the field TransferMech2
#===============================================================================
__all__ += ['ImportMapCheckNumber']
class ImportMapCheckNumber(MapImport):

    # constructor
    def __init__(self, filename, format=Db.CsvFormatBackquote):
        MapImport.__init__(self, filename, format)
        self.map = self.forEachRow()

    # these are the columns of the DB map file     
    def fieldNames(self): return list([
        "CheckNumber",
        "AccountAlias",
        "Date",
        "Amount",
        ])

    # Does the Mint row contain:
    #     TransferMech2: Check 123
    #     AccountAlias:  PAYEE UNRECORDE 761
    # Return the number in the form Check 123 (the key to the BB map)  
    def rowContainsKey(self, row):
        key = str("KEYNOTFOUND")
        
        check_123 = 'Check [0-9]{3}'
        find_pattern = '^' + check_123 + '.*$'
        matches = re.match(find_pattern, row['TransferMech2'])
        if matches:
            #print row
            key = re.findall(check_123, row['TransferMech2'])[0]
            return matches, key
        
        unrecorded_123 = 'UNRECORDE [0-9]{1,3}'
        find_pattern = '^.*' + unrecorded_123 + '.*$'
        matches = re.match(find_pattern, row['AccountAlias'])
        if matches:
            #print row
            key = re.findall(unrecorded_123, row['AccountAlias'])[0]
            return matches, re.sub('UNRECORDE', 'Check', key)

        return matches, key
                              