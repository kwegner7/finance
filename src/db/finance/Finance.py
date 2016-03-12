'''
    Finance - the Model, Essence, Views and Originals
'''

#===============================================================================
# imports
#===============================================================================
from helper import Container
from db import Db
from db.finance import Original, Essence, View
from db.finance.helpers import Account, Db_Accounts

#===============================================================================
# Field Names
#===============================================================================
class FieldNames():
    
    essence = list([
        "Institution",
        "Date",
        "Amount",
        "TransferMech1",
        "TransferMech2",
        "AccountAlias",
    ])
    
    view = model = essence + list([        
        "Account",
        "Category",
        "Subcategory",
        "SimplifiedAlias",
        "Year",
        "YearMonth",
    ])
    
    beyond_banking = list([
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
    
    mint = list([
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
    
#===============================================================================
# Views of the Model
#===============================================================================
class ViewFinance(View.ViewFinance): pass

class ViewMonth(View.ViewMonth): pass
class ViewMonthSummary(View.ViewMonthSummary): pass

class ViewCategory(View.ViewCategory): pass
class ViewCategorySummary(View.ViewCategorySummary): pass

class ViewSubCategory(View.ViewSubCategory): pass
class ViewSubCategorySummary(View.ViewSubCategorySummary): pass

class ViewAccounts(View.ViewAccounts): pass
class ViewAccountsSummary(View.ViewAccountsSummary): pass

#===============================================================================
# Conversion from Essence to the Model
#===============================================================================
class Model(Db.Model):
                
    # constructor
    def __init__(self, obj):
        self.checkClass(obj, Model, Essence)
        self.accounts = Db_Accounts.Db_Accounts(
            '/home/orig/proj/git/finance/run/in/BeyondBanking/Accounts_All.csv')
        Db.Model.__init__(self, obj)

    # implementations of abstract methods     
    def fieldNames(self):
        return FieldNames.model

    def isSelectedRoww(self, row):
        partial_first_month = Container.convertStandardDateToYearMonth(self.first_row['Date'])
        ignore_partial_first_month = (partial_first_month == row["YearMonth"])
        return (
            not     (row["Category"] == "Banking" and row["Subcategory"] == "ML Internal Transfer") 
            and not (row["Category"] == "Banking" and row["Subcategory"] == "Wire In") 
            and not (row["Category"] == "Banking" and row["Subcategory"] == "Check Deposit" 
                and  row["Amount"] == "123,755.05") 
            and not (row["Category"] == "Charitable Donations" 
                and  row["Subcategory"] == "Wire Out" and  row["Amount"] == "-200,000.00") 
            and not (row["Category"] == "Credit Card" 
                and  row["Subcategory"] == "Pay Credit Card" and  row["Account"] == "Capital One")      
            and not (row["Category"] == "Credit Card" and row["Subcategory"] == "Pay Credit Card" 
                and  row["Account"] == "Chase" and  row["Date"] > "2013-07-19")      
            and not ignore_partial_first_month     
        )
        return True

    # FIXTHIS
    def isSelectedRow(self, row):
        return row['Year'] == '2015'
        return True
        return row["Date"] > "2014-03-09" and row['Year'] == '2015'

    def sortBeforeTransform(self): 
        return list([ 'Date', 'Amount' ])

    # horizontally, expand from the essence     
    def transform(self, essence_col, next_col):
        derived_col = dict(essence_col)  
        derived_col['Year'] = \
            Container.convertStandardDateToYear(essence_col['Date'])
        derived_col['YearMonth'] = \
            Container.convertStandardDateToYearMonth(essence_col['Date'])
        derived_col['SimplifiedAlias'], \
        derived_col['Account'],         \
        derived_col['Category'],        \
        derived_col['Subcategory'] =    \
            self.processAccountAlias(essence_col['AccountAlias'])
        return True, derived_col

    # helper
    def processAccountAlias(self, account_alias):
        simplified_alias = Account.simplifyAlias(account_alias)
        account_title = self.accounts.getAccountTitle(account_alias)
        subcategory = self.accounts.getSubcategory(account_title)
        category = self.accounts.getCategory(account_title)
        return simplified_alias, account_title, category, subcategory

#===============================================================================
# Conversions from Originals to Essence
#===============================================================================
class Essence(Db.Essence):
                        
    # constructor
    def __init__(self, original, institution = ''):
        self.original = original
        self.checkClass(original, Essence, Db.Reference)
        Db.Essence.__init__(self, original)

    # implementations of abstract methods     
    def fieldNames(self):
        return FieldNames.essence

    # common helpers 
    @classmethod       
    def normalizeAmountField(cls, amount_text):
        as_float = Container.getFloat(amount_text)
        return  Container.formatDollars(as_float)
    
    @classmethod       
    def normalizeDateField(cls, date_text):
        return Container.convertDateWithSlashes(date_text)
        
    # implementations of abstract methods     
    def transform(self, this_row, next_row):
        return self.original.transform(this_row, next_row)                

#===============================================================================
# Original Essence
#===============================================================================
class OrigEssence(Db.Reference):
    
    def fieldNames(self):
        return FieldNames.essence

    def transform(self, this_row, next_row):
        essence = dict(this_row)
        return True, essence
        
#===============================================================================
# Original Beyond Banking
#===============================================================================
class OrigBeyondBanking(Db.Reference):
    
    def fieldNames(self):
        return FieldNames.beyond_banking

    def transform(self, this_row, next_row):
        essence = dict()
        essence['Date'] = Essence.normalizeDateField(this_row['Settlement Date'])  
        essence['Amount'] = Essence.normalizeAmountField(this_row['Amount ($)'])
        essence['TransferMech1'] = this_row['Type']   
        essence['TransferMech2'] = this_row['Description 1']
        essence['AccountAlias'] = this_row['Description 2']   
        essence['Institution'] = 'Beyond Banking'
        return True, essence
        
#===============================================================================
# Original Mint
#===============================================================================
class OrigMint(Db.Reference):
    
    def fieldNames(self):
        return FieldNames.mint
        
    def transform(self, this_row, next_row):
        essence = dict()
        essence['Date'] = Essence.normalizeDateField(this_row['Date'])      
        if this_row['Transaction Type'] == 'debit':
            maybe_minus = "-"+this_row['Amount']
        elif this_row['Transaction Type'] == 'credit':
            maybe_minus = this_row['Amount']
        else:
            maybe_minus = '0.0'
            print "ERROR: Db_Raw_Finance_Mint: transaction type is not credit or debit"
        essence['Amount'] = Essence.normalizeAmountField(maybe_minus)
        essence['TransferMech1'] = this_row['Category']   
        essence['TransferMech2'] = this_row['Description']
        essence['AccountAlias'] = this_row['Original Description'] 
        if this_row['Account Name'] == 'VISA SIGNATURE':  
            essence['Institution'] = 'Mint Capital One'
        elif this_row['Account Name'] == 'CREDIT CARD':  
            essence['Institution'] = 'Mint Chase'
        else:
            essence['Institution'] = this_row['Account Name']
        return True, essence
                              
