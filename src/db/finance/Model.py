'''
    Model Db - This is a master database with complete, useful fields
'''
#===============================================================================
# imports
#===============================================================================
from helper import Container

from db.Db import Model
from db.finance.Essence import EssenceFinance

from db.finance.helpers.Db_Accounts import Db_Accounts
import db.finance.helpers.Account

__all__ = list()

#===============================================================================
# ModelGeneric (may be instantiated)
#===============================================================================
__all__ += ['ModelGeneric']
class ModelGeneric(Model):
                
    # constructor
    def __init__(self, obj):
        self.essence_fields = obj.fieldNames()
        Model.__init__(self, obj)

    # implementations of abstract methods     
    def fieldNames(self):
        return self.essence_fields
    
    def transform(self, essence_col, next_col):
        derived_col = dict(essence_col)  
        return True, derived_col

#===============================================================================
# ModelFinance (may be instantiated)
#===============================================================================
__all__ += ['ModelFinance']
class ModelFinance(Model):

    
    field_names = EssenceFinance.field_names + list([        
        "Account",
        "Category",
        "Subcategory",
        "SimplifiedAlias",
        "Year",
        "YearMonth",
    ])
                
    # constructor
    def __init__(self, obj):
        #self.checkClass(obj, ModelFinance, EssenceFinance)
        self.accounts = Db_Accounts(
            '/home/orig/proj/git/finance/run/in/BeyondBanking/Accounts_All.csv')
        Model.__init__(self, obj)

    # implementations of abstract methods     
    def fieldNames(self):
        return self.field_names

    def isSelectedRow(self, row):
        partial_first_month = Container.convertStandardDateToYearMonth(self.first_row['Date'])
        ignore_partial_first_month = (partial_first_month == row["YearMonth"])
        return (
            not     (row["Category"] == "Banking" and row["Subcategory"] == "ML Internal Transfer") 
            and not (row["Category"] == "Banking" and row["Subcategory"] == "Wire In") 
            and not (row["Category"] == "Banking" and row["Subcategory"] == "Check Deposit" and  row["Amount"] == "123,755.05") 
            and not (row["Category"] == "Charitable Donations" and row["Subcategory"] == "Wire Out" and  row["Amount"] == "-200,000.00") 
            and not (row["Category"] == "Credit Card" and row["Subcategory"] == "Pay Credit Card" and  row["Account"] == "Capital One")      
            and not (row["Category"] == "Credit Card" and row["Subcategory"] == "Pay Credit Card" and  row["Account"] == "Chase" and  row["Date"] > "2013-07-19")      
            and not ignore_partial_first_month     
        )
        return True

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
        simplified_alias = db.finance.helpers.Account.simplifyAlias(account_alias)
        account_title = self.accounts.getAccountTitle(account_alias)
        subcategory = self.accounts.getSubcategory(account_title)
        category = self.accounts.getCategory(account_title)
        return simplified_alias, account_title, category, subcategory



















'''
#===============================================================================
# GenerateMapBillPay (may be instantiated) 
#
#    Reads from the CSV file .../in/BeyondBanking/ALLBB.csv
#    These are all of the downloads from the ML website
#
#    In the AccountAlias field search for 0088dddd anywhere
#    Produces a new csv file with columns:
#           BillPayId        AccountAlias
#            00880303    YEKOPE MINISTRIE00880303
#
#===============================================================================
__all__ += ["GenerateMapBillPay"]

class GenerateMapBillPay(MapGenerate):
    
    # 7 implementations of abstract methods     
    def fieldNames(self): return list([
        "BillPayId",
        "AccountAlias",
        ])

    def rowContainsKey(self, row):
        key = str("KEYNOTFOUND")
        eight_digits = '0088[0-9]{4}'
        find_pattern = '^.*' + eight_digits + '.*$'
        matches = re.match(find_pattern, row['AccountAlias'])
        if matches:
            key = re.findall(eight_digits, row['AccountAlias'])[0]
        return matches, key

    def sortBeforeTransform(self): 
        return list([])

    def sortAfterTransform(self):
        return list([ 'BillPayId' ])
        
    def isSelectedRow(self, row):
        return len(row['BillPayId']) > 0

    def transform(self, row_in, next_row):
        row_out = dict()

        row_out["AccountAlias"] = row_in["AccountAlias"]
        row_contains_key, key = self.rowContainsKey(row_in)            
        if row_contains_key:
            row_out['BillPayId'] = key
        else:
            row_out['BillPayId'] = str('')

        return True, row_out

    def htmlPresentation(self, dirpath):
        HtmlModern(self, dirpath)
        return

#===============================================================================
# GenerateMapCheckNumber (may be instantiated) 
#===============================================================================
__all__ += ["GenerateMapCheckNumber"]

class GenerateMapCheckNumber(MapGenerate):

    # implementations of abstract methods     
    def fieldNames(self): return list([
        "CheckNumber",
        "AccountAlias",
        ])
        
    def rowContainsKey(self, row):
        key = str("KEYNOTFOUND")
        check_123 = 'Check [0-9]{3}'
        find_pattern = '^' + check_123 + '.*$'
        matches = re.match(find_pattern, row['TransferMech2'])
        if matches:
            #print row['TransferMech2']
            key = re.findall(check_123, row['TransferMech2'])[0]
            return matches, key            
        return matches, key
    
    def sortBeforeTransform(self): 
        return list([])

    def sortAfterTransform(self):
        return list([ 'CheckNumber' ])
        
    def isSelectedRow(self, row):
        return len(row['CheckNumber']) > 0

    def transform(self, row_in, next_row):
        row_out = dict()
        
        row_out["AccountAlias"] = row_in["AccountAlias"]
        row_contains_key, key = self.rowContainsKey(row_in)            
        if row_contains_key:
            row_out['CheckNumber'] = key
        else:
            row_out['CheckNumber'] = str('')

        return True, row_out

    def htmlPresentation(self, dirpath):
        HtmlModern(self, dirpath)
        return
'''




'''

#===============================================================================
# SubsetGeneric0 
#===============================================================================
class SubsetGeneric0(Subset):
    
    def __init__(self, obj):
        self.checkClass(obj, SubsetGeneric, Db)
        Subset.__init__(self, obj)

    def initializeTransform(self):
        self.count = 0
        self.running_totals = Container.RunningTotals()
        self.section_totals = Container.RunningTotals()
        self.subsection_totals = Container.RunningTotals()
        
    def subsectionChange(self):
        return list([ '1', '2', ])

    def sectionChange(self):
        return list([ '1', ])
               
    def additionalFieldNames(self): return list([
        "Count",
        "SectionCount",
        "SubsectionCount",
    ])
        
    def transform(self, row_in):
        row_out = dict(row_in)

        Container.RunningTotals.monitor.slideFieldValues(row_in)
        
        change_section = self.sectionChange()
        change_subsection = self.subsectionChange()
        
        self.running_totals.accumulate(    '0.00',                [])
        self.section_totals.accumulate(    '0.00',    change_section)
        self.subsection_totals.accumulate( '0.00', change_subsection)
        
        row_out['Count'] = self.running_totals.getNumberTransactions()  
        row_out['SectionCount'] = self.section_totals.getNumberTransactions()
        row_out['SubsectionCount'] = self.subsection_totals.getNumberTransactions()
        
        return True, row_out


#===============================================================================
# These are the fields of Beyond Banking transactions downloaded from Mint
#===============================================================================
class MintBeyondBanking(Original):

    def fieldNames(self, default): return list([
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
# DbCheckStandard
#    Construct this from a file name
#    The action will check each row and print information
#===============================================================================
class DbCheckStandard(Db):

    def action(self):
        print "in DbCheckStandard"
        self.text()
        first_row = True
        self.openRead()
        for row in self.reader:
            number_fields = len(row)
            #print "Row size is", number_fields
        self.closeRead()
        return self
        
#===============================================================================
# DbAppendManyStandard
#    Construct this from a list of standard csv files
#    The action will return a new standard Db consisting of all of the files
#===============================================================================
class DbAppendManyStandard(Db):

    def action(self):
        self.text()
        first_row = True
        self.openRead()
        for row in self.reader:
            filename = row['0']
            print filename
            if first_row:
                first_row = False
                collect = DbStandard(filename)
            else:
                next = DbStandard(filename)
                if next.seemsToHaveHeader(next.filename) and len(next.fieldnames) == 13:
                    next.text()
                    collect.append(next)
        self.closeRead()
        collect.export('/home/kurt/checked-out/apps/finance/svn-run/in/BeyondBanking/ALLBB.csv')
        print "ALL BEYOND BANKING AT:",collect.filename
        return collect

#===============================================================================
# ModelFinance - Create a map from check ID to account title and categories
#===============================================================================
class MapCheckNumber_From_BeyondBanking(ModelFinance_From_BeyondBanking):

    map_info = list([
        "CheckNumber",
        "Institution",
        "Date",
        "Amount",
        "TransferMech1",
        "TransferMech2",
        "AccountAlias",
    ])
        
    def isSelectedRow(self, row):
        return len(row['BillPayId']) > 0
        
    def forEachRow(self, db_in, db_out):
        self.initializeTransform()
        db_in.openRead(); db_out.openWrite();
        for row in db_in.reader:
            please_write_row, row_out = self.transform(row)
            if please_write_row and self.isSelectedRow(row_out):
                db_out.writer.writerow(
                    [row_out[x] for x in MapCheckNumber_From_BeyondBanking.map_info])
        db_in.closeRead(); db_out.closeWrite();
        if set(row_out.keys()) != set(db_out.fieldnames):
            print "ERROR: Transform method is not producing correct fields" 
        return None
'''        
'''    
###############################################################################
# RunningTotals
###############################################################################
class RunningTotals():

    # static
    monitor = MonitorField()
               
    def __init__(self, beginning_balance = 0.0):
        self.count_records = 0
        self.sub_total = beginning_balance     
        self.sub_credit = 0
        self.sub_debit = 0
        pass

    def accumulate(self, row, list_of_fields):
        field_has_changed = self.monitor.fieldHasChanged(list_of_fields)
        self.accumulateRows(field_has_changed)
        self.accumulateTotal(row['Amount'],  field_has_changed)
        self.accumulateCredit(row['Amount'], field_has_changed)
        self.accumulateDebit(row['Amount'],  field_has_changed)
        return None



    def accumulateRows(self, field_has_changed):
        if field_has_changed:
            self.count_records = 1
        else:
            self.count_records += 1      
        return None

    def getNumberRows(self):
        return str(self.count_records)

    def accumulateTotal(self, amount, field_has_changed):
        if field_has_changed:
            self.sub_total = Container.getFloatNoCommas(amount)
            self.count_records = 1
        else:
            self.sub_total += Container.getFloatNoCommas(amount) 
            self.count_records += 1      
        return None

    def getTotal(self):
        return Container.formatDollars(self.sub_total)

    def accumulateCredit(self, amount, field_has_changed):
        money = Container.getFloatNoCommas(amount)
        if field_has_changed:
            if money >= 0.0: self.sub_credit = money
            else:            self.sub_credit = 0.0
        else:
            if money >= 0.0: self.sub_credit += money
        return None

    def getCredit(self):
        return formatDollars(self.sub_credit)


    def accumulateDebit(self, amount, field_has_changed):
        money = Container.getFloatNoCommas(amount)
        if field_has_changed:
            if money < 0.0: self.sub_debit = money
            else:           self.sub_debit = 0.0
        else:
            if money < 0.0: self.sub_debit += money
        return None

    def getDebit(self):
        return formatDollars(self.sub_debit)
'''
                              
