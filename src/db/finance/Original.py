'''
    Original Db
'''
#===============================================================================
# imports
#===============================================================================
import abc, re
from db.Db import Db, Original, Reference

__all__ = list()

#===============================================================================
# OrigGeneric (may be instantiated)
#===============================================================================
__all__ += ['OrigGeneric']
class OrigGeneric(Original):

    # constructor
    def __init__(self, csv_file, format=Db.CsvFormatBackquote):
        self.checkClass(csv_file, OrigGeneric, str)
        
        # since the fieldnames are unknown
        # must check to see how many columns
        number_columns_ok, self.number_columns = \
            self.numberFields(csv_file, format.dialect)

        Original.__init__(self, csv_file, format)
        
    # implementations of abstract methods     
    def fieldNames(self):
        return list([str(x) for x in range(0, self.number_columns)])

#===============================================================================
# OrigFinance (may be instantiated)
#===============================================================================
__all__ += ['OrigFinance']
class OrigFinance(Original):
    
    field_names = list([
        "Institution",
        "Date",
        "Amount",
        "TransferMech1",
        "TransferMech2",
        "AccountAlias",
    ])
    
    def fieldNames(self):
        return self.field_names

    # constructor
    def __init__(self, filename, format=Db.CsvFormatBackquote):
        self.checkClass(filename, OrigFinance, str)
        Original.__init__(self, filename, format)


#===============================================================================
# OrigBeyondBanking (may be instantiated)
#===============================================================================
__all__ += ['OrigBeyondBanking']
class OrigBeyondBanking(Reference):

    # constructor
    def __init__(self, filename, format=Db.CsvFormatBackquote):
        self.checkClass(filename, OrigBeyondBanking, str)
        Reference.__init__(self, filename, format)

    # implementations of abstract methods     
    def fieldNames(self): return list([
        "Trade Date",
        "Settlement Date",
        "Pending/Settled",
        "Account Nickname",
        "Account Registration",
        "Account #",
        "Type",
        "Description 1",
        "Description 2",
        "Symbol/CUSIP #",
        "Quantity",
        "Price ($)",
        "Amount ($)"
    ])

#===============================================================================
# OrigMint (may be instantiated)
#===============================================================================
__all__ += ['OrigMint']
class OrigMint(Original):

    # constructor
    def __init__(self, filename, format=Db.CsvFormatBackquote):
        self.checkClass(filename, OrigMint, str)
        Original.__init__(self, filename, format)

    # implementations of abstract methods     
    def fieldNames(self): return list([
        "Date",
        "Description",           # Mint's quess at the real account name
        "Original Description",  # original description of account
        "Amount",
        "Transaction Type",      # debit or credit
        "Category",              # Mint's quess at the category of the account
        "Account Name",          # the institution
        "Labels",
        "Notes",
    ])

'''    
#===============================================================================
# MapImport is an Original so it does not perform a transformation between
# databases. Rather, the csv file is imported in a loop to become a map.
# The Original csv file has useful data in columns and and a single key field.
#===============================================================================
class MapImportAbstract(Abstract):
    
    @abc.abstractmethod
    def rowContainsKey(self, row): pass

class MapImport(Original, MapImportAbstract):
                
    # constructor
    def __init__(self, db_in, format=Db.CsvFormatBackquote):
        Original.__init__(self, db_in, format)

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
'''                              