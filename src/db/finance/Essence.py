'''
    Essence Db
'''
#===============================================================================
# imports
#===============================================================================
import os
from helper import Container

from db.Db import Db, Essence
from db.finance.Original import OrigFinance, OrigBeyondBanking, OrigMint
from db.finance.ReferenceMap import ImportMapBillPay, ImportMapCheckNumber


__all__ = list()
                     
#===============================================================================
# EssenceGeneric (may be instantiated)
#===============================================================================
__all__ += ['EssenceGeneric']
class EssenceGeneric(Essence):
    
    # constructor
    def __init__(self, obj):
        self.orig_fields = obj.fieldNames()
        Essence.__init__(self, obj)
        
    # implementations of abstract methods     
    def fieldNames(self):
        return self.orig_fields

    def transform(self, orig_col, next_col):
        essence_col = dict(orig_col)
        return True, essence_col

#===============================================================================
# EssenceFinance (abstract)
#===============================================================================
__all__ += ['EssenceFinance']
class EssenceFinance(Essence):
    
    field_names = OrigFinance.field_names
                    
    # constructor
    def __init__(self, db_orig, institution = ''):
        self.db_orig = db_orig
        self.checkClass(db_orig, EssenceFinance, Db)
        Essence.__init__(self, db_orig)

    # implementations of abstract methods     
    def fieldNames(self):
        return self.field_names

    # common helpers    
    def normalizeAmountField(self, amount_text):
        as_float = Container.getFloat(amount_text)
        return  Container.formatDollars(as_float)
    
    def normalizeDateField(self, date_text):
        return Container.convertDateWithSlashes(date_text)
        
    # implementations of abstract methods     
    def transform(self, this_row, next_row):
        if isinstance(self.db_orig, OrigBeyondBanking):
            return self.transformBeyondBanking(this_row, next_row)
        if isinstance(self.db_orig, OrigMint):
            return self.transformMint(this_row, next_row)
        return True, this_row
        
    def transformBeyondBanking(self, orig_col, next_col):
        essence_col = dict()
        essence_col['Date'] = self.normalizeDateField(orig_col['Settlement Date'])  
        essence_col['Amount'] = self.normalizeAmountField(orig_col['Amount ($)'])
        essence_col['TransferMech1'] = orig_col['Type']   
        essence_col['TransferMech2'] = orig_col['Description 1']
        essence_col['AccountAlias'] = orig_col['Description 2']   
        essence_col['Institution'] = 'Beyond Banking'
        return True, essence_col
        
    def transformMint(self, orig_col, next_col):
        essence_col = dict()
        essence_col['Date'] = self.normalizeDateField(orig_col['Date'])      
        if orig_col['Transaction Type'] == 'debit':
            maybe_minus = "-"+orig_col['Amount']
        elif orig_col['Transaction Type'] == 'credit':
            maybe_minus = orig_col['Amount']
        else:
            maybe_minus = '0.0'
            print "ERROR: Db_Raw_Finance_Mint: transaction type is not credit or debit"
        essence_col['Amount'] = self.normalizeAmountField(maybe_minus)
        essence_col['TransferMech1'] = orig_col['Category']   
        essence_col['TransferMech2'] = orig_col['Description']
        essence_col['AccountAlias'] = orig_col['Original Description']   
        essence_col['Institution'] = 'Mint Capital One'
        return True, essence_col
        
        

__all__ += ["EssenceFinanceSorted"]
class EssenceFinanceSorted (EssenceFinance):
    
    # constructor
    def __init__(self, obj):
        EssenceFinance.__init__(self, obj)

    def sortAfterTransform(self): 
        return list([ 'Date', 'Amount' ])

__all__ += ["EssenceBeyondBankingSorted"]
class EssenceBeyondBankingSorted (EssenceFinance):
    
    # constructor
    def __init__(self, obj):
        EssenceFinance.__init__(self, obj)

    def sortAfterTransform(self): 
        return list([ 'Date', 'Amount' ])
        
'''
#===============================================================================
# EssenceBeyondBanking (may be instantiated)
#===============================================================================
__all__ += ['EssenceBeyondBanking']
class EssenceBeyondBanking(EssenceFinance):
    
    # constructor
    def __init__(self, obj):
        EssenceFinance.__init__(self, obj)
        
    # implementations of abstract methods     
    def transform(self, orig_col, next_col):
        essence_col = dict()
        essence_col['Date'] = self.normalizeDateField(orig_col['Settlement Date'])  
        essence_col['Amount'] = self.normalizeAmountField(orig_col['Amount ($)'])
        essence_col['TransferMech1'] = orig_col['Type']   
        essence_col['TransferMech2'] = orig_col['Description 1']
        essence_col['AccountAlias'] = orig_col['Description 2']   
        essence_col['Institution'] = 'Beyond Banking'
        return True, essence_col

__all__ += ["EssenceBeyondBankingSorted"]
class EssenceBeyondBankingSorted (EssenceBeyondBanking):
    
    # constructor
    def __init__(self, obj):
        EssenceBeyondBanking.__init__(self, obj)

    def sortAfterTransform(self): 
        return list([ 'Date', 'Amount' ])
       
#===============================================================================
# EssenceMint (may be instantiated)
#===============================================================================
__all__ += ['EssenceMint']
class EssenceMint(EssenceFinance):

    # constructor
    def __init__(self, orig_db, institution):
        self.institution = institution
        self.map_bill_pay = ImportMapBillPay(os.getcwd()+'/in/maps/billpay.csv')
        self.map_check_number = ImportMapCheckNumber(os.getcwd()+'/in/maps/checknumber.csv')
        EssenceFinance.__init__(self, orig_db)
        return

    # This applies the Mint Beyond Banking only
    def determineAccountAlias(self, row):
        new_account_alias = row['AccountAlias'] 
        return new_account_alias

        row_contains_key, fields_from_map = self.map_bill_pay.searchForKeyAndObtainMapFields(row) 
        if row_contains_key:
            new_account_alias = fields_from_map['AccountAlias']
            if (fields_from_map['Date'] == row['Date']
            and fields_from_map['Amount'] == row['Amount']):
                print "From Mint database row, found key", row_contains_key, "which maps to", fields_from_map
            else:
                print "ERROR: Date and Amount do not match:"
                print "      BB indicates:", fields_from_map['Date'], fields_from_map['Amount'], fields_from_map['AccountAlias']
                print "    Mint indicates:", row['Date'], row['Amount'], row['AccountAlias']

        row_contains_key, fields_from_map = self.map_check_number.searchForKeyAndObtainMapFields(row) 
        if row_contains_key:
            new_account_alias = fields_from_map['AccountAlias']
            print "From Mint database row, found key", key, "which maps to", fields_from_map
                             
        return new_account_alias
      
    # implementations of abstract methods     
    def transform(self, orig_col, next_col):
        essence_col = dict()
        essence_col['Date'] = self.normalizeDateField(orig_col['Date'])      
        if orig_col['Transaction Type'] == 'debit':
            maybe_minus = "-"+orig_col['Amount']
        elif orig_col['Transaction Type'] == 'credit':
            maybe_minus = orig_col['Amount']
        else:
            maybe_minus = '0.0'
            print "ERROR: Db_Raw_Finance_Mint: transaction type is not credit or debit"
        essence_col['Amount'] = self.normalizeAmountField(maybe_minus)
        essence_col['TransferMech1'] = orig_col['Category']   
        essence_col['TransferMech2'] = orig_col['Description']
        essence_col['AccountAlias'] = orig_col['Original Description']   
        essence_col['Institution'] = self.institution
        
        account_alias = self.determineAccountAlias(essence_col)   
        essence_col['AccountAlias'] = account_alias   
        return True, essence_col
'''                             