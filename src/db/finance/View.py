'''
    View Db
'''
#===============================================================================
# imports
#===============================================================================
import os
from abc import abstractmethod
from helper import Container

from db.Db import Db, View
from db.finance.Model import ModelFinance

from html.finance.HtmlTableFinance import *

__all__ = list()

#===============================================================================
# ViewGeneric (may be instantiated)
#===============================================================================        
class ViewGeneric(View):
                
    # constructor
    def __init__(self, obj):
        self.master_fields = obj.fieldNames()
        View.__init__(self, obj)

    # implementations of abstract methods     
    def fieldNames(self):
        return list([ 'Count' ]) + self.master_fields
        
    def isSelectedRow(self, row):
        return True

    def initializeTransform(self):
        self.count_running = 0
    
    def transform(self, master_col, next_col):
        self.count_running = self.count_running+1
        subset_col = dict(master_col)
        subset_col['Count'] = self.count_running
        return True, subset_col

    def sortBeforeTransform(self): return list()

    def sortAfterTransform(self): return list()

    def collapseOnFields(self): return list()

    def subsectionChange(self): return list()

    def sectionChange(self): return list()

    def htmlPresentation(self, dirpath):
        HtmlGeneric(self, dirpath)
        return
                                                                           
#===============================================================================
# ViewFinance (may be instantiated) 
#
#    This is a standard way to present finance transactions. It includes
#    running totals for section and subsection to obtain every transaction
#    with subtotals for section year and subsection month.
#
#===============================================================================
class ViewFinance(View):
    
    @abstractmethod
    def sortBeforeTransform(self): pass 
        
    @abstractmethod
    def subsectionChange(self): pass

    @abstractmethod
    def sectionChange(self): pass
    
    # constructor
    def __init__(self, obj):
        #self.checkClass(obj, ViewFinance, MasterFinance)
        View.__init__(self, obj)

    def additionalFieldNames(self): return list([
        "CountRunning",
        "CountSection",
        "CountSubsection",
        
        "TotalRunning",
        "DebitRunning",
        
        "TotalSection",
        "DebitSection",
        
        "TotalSubsection",
        "DebitSubsection",
        
        "TotalYear",
        "DebitYear",
        
        "TotalMonth",
        "DebitMonth",
        
        "TotalCategory",
    ])

    # implementations of abstract methods     
    def fieldNames(self):
        return ModelFinance.field_names + self.additionalFieldNames() 

    def sortAfterTransform(self):
        return list([])

    def collapseOnFields(self):
        return list([])
   
    def initializeTransform(self):
        self.collapse = Db.Collapse(self.collapseOnFields()) 
         
        self.count_running = Db.Count([])
        self.total_running = Db.Total([])
        self.debit_running = Db.Debit([])
        
        self.count_section = Db.Count(self.sectionChange())
        self.total_section = Db.Total(self.sectionChange())
        self.debit_section = Db.Debit(self.sectionChange())
        
        self.count_subsection = Db.Count(self.subsectionChange())
        self.total_subsection = Db.Total(self.subsectionChange())
        self.debit_subsection = Db.Debit(self.subsectionChange())
        
        self.total_month = Db.Total(['YearMonth'])
        self.debit_month = Db.Debit(['YearMonth'])
        
        self.total_year = Db.Total(['Year'])
        self.debit_year = Db.Debit(['Year'])
        
        self.total_category = Db.Total(['Category'])
        return

    # FIXTHIS
    def isSelectedRow(self, row): 
        return True
        return row["Date"] > "2014-03-09" and row['Year'] == '2015'

    def transform(self, this_row, next_row):
        row_out = dict(this_row)

        if Db.Accumulation.monitor.fieldWillChange('Year'):
            if next_row == None:
                pass #print this_row['Year'], next_row
            else:
                pass #print this_row['Year'], next_row['Year']
        
        row_out['CountRunning'] = self.count_running.accumulate(this_row)
        row_out['CountSection'] = self.count_section.accumulate(this_row)
        row_out['CountSubsection'] = self.count_subsection.accumulate(this_row)

        if (not     (this_row["Category"] == "Credit Card" and this_row["Subcategory"] == "Pay Credit Card" and  this_row["Account"] == "Capital One")      
            and not (this_row["Category"] == "Credit Card" and this_row["Subcategory"] == "Pay Credit Card" and  this_row["Account"] == "Chase") ):    

            row_out['TotalRunning'] = self.total_running.accumulate(this_row)
            row_out['DebitRunning'] = self.debit_running.accumulate(this_row)

            row_out['TotalSection'] = self.total_section.accumulate(this_row)
            row_out['DebitSection'] = self.debit_section.accumulate(this_row)

            row_out['TotalSubsection'] = self.total_subsection.accumulate(this_row)
            row_out['DebitSubsection'] = self.debit_subsection.accumulate(this_row)

            row_out['TotalMonth'] = self.total_month.accumulate(this_row)
            row_out['DebitMonth'] = self.debit_month.accumulate(this_row)

            row_out['TotalYear'] = self.total_year.accumulate(this_row)
            row_out['DebitYear'] = self.debit_year.accumulate(this_row)

            row_out['TotalCategory'] = self.total_category.accumulate(this_row)

        else:

            print "Skipping", this_row["Category"], this_row["Subcategory"], this_row["Account"], this_row["Date"], this_row["Amount"]
            row_out['TotalRunning'] = self.total_running.get()
            row_out['DebitRunning'] = self.debit_running.get()

            row_out['TotalSection'] = self.total_section.get()
            row_out['DebitSection'] = self.debit_section.get()

            row_out['TotalSubsection'] = self.total_subsection.get()
            row_out['DebitSubsection'] = self.debit_subsection.get()

            row_out['TotalMonth'] = self.total_month.get()
            row_out['DebitMonth'] = self.debit_month.get()

            row_out['TotalYear'] = self.total_year.get()
            row_out['DebitYear'] = self.debit_year.get()

            row_out['TotalCategory'] = self.total_category.get()

        please_write = self.collapse.accumulate(this_row)
        return please_write, row_out

    def htmlPresentation(self, dirpath):
        HtmlModern(self, dirpath)
        return
                
#===============================================================================
# Month/Year
#===============================================================================
__all__ += ["ViewMonth"]
class ViewMonth(ViewFinance):

    def sortBeforeTransform(self): 
        return list([ 'Year', 'YearMonth', 'Date' ])
        
    def subsectionChange(self):
        return list([ 'Year', 'YearMonth', ])

    def sectionChange(self):
        return list([ 'Year', ])

    def htmlPresentation(self, dirpath):
        HtmlMonthDetails(self, dirpath)
        return
                
__all__ += ["ViewMonthSummary"]
class ViewMonthSummary(ViewMonth):
        
    def htmlPresentation(self, dirpath):
        HtmlMonthSummary(self, dirpath)
        return
           
#===============================================================================
# Category
#===============================================================================
__all__ += ["ViewCategory"]
class ViewCategory(ViewFinance):

    def sortBeforeTransform(self): 
        return list([ 'Year', 'Category', 'Subcategory', 'Account', 'Date' ])
        
    def subsectionChange(self):
        return list([ 'Year', 'Category', ])

    def sectionChange(self):
        return list([ 'Year', ])

    def htmlPresentation(self, dirpath):
        HtmlCategoryDetails(self, dirpath)
        return
                
__all__ += ["ViewCategorySummary"]
class ViewCategorySummary(ViewCategory):
        
    def htmlPresentation(self, dirpath):
        HtmlCategorySummary(self, dirpath)
        return
       
#===============================================================================
# Subcategory
#===============================================================================
__all__ += ["ViewSubCategory"]
class ViewSubCategory(ViewFinance):

    def sortBeforeTransform(self): 
        return list([ 'Year', 'Category', 'Subcategory', 'Account', 'Date' ])
        
    def subsectionChange(self):
        return list([ 'Year', 'Category', 'Subcategory', ])

    def sectionChange(self):
        return list([ 'Year', ])

    def htmlPresentation(self, dirpath):
        HtmlSubcategoryDetails(self, dirpath)
        return
                
__all__ += ["ViewSubCategorySummary"]
class ViewSubCategorySummary(ViewSubCategory):
        
    def htmlPresentation(self, dirpath):
        HtmlSubCategorySummary(self, dirpath)
        return
    
#===============================================================================
# Accounts
#===============================================================================
__all__ += ["ViewAccounts"]
class ViewAccounts(ViewFinance):

    def sortBeforeTransform(self): 
        return list([ 'Year', 'Category', 'Subcategory', 'Account', 'Date' ])
        
    def subsectionChange(self):
        return list([ 'Year', 'Category', 'Subcategory', 'Account',  ])

    def sectionChange(self):
        return list([  'Year', ])

    def htmlPresentation(self, dirpath):
        HtmlAccountsDetails(self, dirpath)
        return
                
__all__ += ["ViewAccountsSummary"]
class ViewAccountsSummary(ViewAccounts):
        
    def htmlPresentation(self, dirpath):
        HtmlAccountsSummary(self, dirpath)
        return
         
        
#===============================================================================
# ViewYearSummary (may be instantiated) 
#===============================================================================
__all__ += ["ViewYearSummary"]
class ViewYearSummary(ViewFinance):

    def sortBeforeTransform(self): 
        return list([ 'Year', 'YearMonth', 'Date' ])
        
    def subsectionChange(self):
        return list([ 'Year' ])

    def sectionChange(self):
        return list([])
        
    def htmlPresentation(self, dirpath):
        HtmlYearSummary(self, dirpath)
        return











'''

__all__ += ["ViewFinanceNew"]
class ViewFinanceNew(ViewFinance):
    
    # reimplementations of abstract methods     
    def sortBeforeTransform(self): return list([ 
        "Year",
        "YearMonth",
        "Category",
        "Subcategory",
        "Account",
    ])
    
    def subsectionChange(self): return list([ 
        "Year",
        "YearMonth",
        "Category",
        "Subcategory",
    ])

    def sectionChange(self): return list([ 
        "Year",
        "YearMonth",
    ])

    def collapseOnFields(self):
        return list([ ])

    def htmlPresentation(self, dirpath):
        HtmlModernNew(self, dirpath)
        return
        
        
#===============================================================================
# ViewMonths (may be instantiated) 
#
#    This reorders the standard to obtain every transaction with subtotals
#    for section category and subsection year.
#
#===============================================================================
__all__ += ["ViewMonths"]
class ViewMonths(ViewFinance):
    
    def sortBeforeTransform(self): 
        return list([ 'Year', 'YearMonth', 'Date' ])

    def sortAfterTransform(self): return list()
        
    def subsectionChange(self):
        return list([ 'Year', 'YearMonth', ])

    def sectionChange(self):
        return list([ 'Year', ])
    
    def htmlPresentation(self, dirpath):
        HtmlModern(self, dirpath)
        return
        
#===============================================================================
# ViewCategory (may be instantiated) 
#
#    This reorders the standard to obtain every transaction with subtotals
#    for section category and subsection year.
#
#===============================================================================

class ViewCategoryy(ViewFinance):
    
    # reimplementations of abstract methods     
    def sortBeforeTransform(self): return list([ 
        "Category",
        "Year",
        "Subcategory",
        "Account",
    ])
    
    def subsectionChange(self): return list([ 
        "Category",
        "Year",
    ])

    def sectionChange(self): return list([ 
        "Category",
    ])

    def collapseOnFields(self):
        return list([ ])

    def htmlPresentation(self, dirpath):
        HtmlModernCategory(self, dirpath)
        return
                
        
#===============================================================================
# ViewSubcategory (may be instantiated) 
#
#    This reorders the standard to obtain every transaction with subtotals
#    for section subcategory and subsection year.
#
#===============================================================================
__all__ += ["ViewSubcategory"]
class ViewSubcategory(ViewFinance):
    
    # reimplementations of abstract methods     
    def sortBeforeTransform(self): return list([ 
        "Category",
        "Subcategory",
        "Year",
        "Account",
    ])
    
    def subsectionChange(self): return list([ 
        "Category",
        "Subcategory",
        "Year",
    ])

    def sectionChange(self): return list([ 
        "Category",
        "Subcategory",
    ])

    def collapseOnFields(self):
        return list([ ])

    def htmlPresentation(self, dirpath):
        HtmlModernSubcategory(self, dirpath)
        return

#===============================================================================
# ViewAccounts (may be instantiated) 
#
#    This reorders the standard to obtain every transaction with subtotals
#    for section Account and subsection Account.
#
#===============================================================================
__all__ += ["ViewAccounts"]
class ViewAccounts(ViewFinance):
    
    # reimplementations of abstract methods     
    def sortBeforeTransform(self): return list([ 
        "Category",
        "Subcategory",
        "Account",
        "Date",
    ])
    
    def subsectionChange(self):
        return list([ ])

    def sectionChange(self):
        return list([ ])

    def collapseOnFields(self):
        return list([ ])
        return list([ 'SimplifiedAlias' ])

    def htmlPresentation(self, dirpath):
        HtmlModernAccounts(self, dirpath)
        return
        
#===============================================================================
# ViewCategorySummary (may be instantiated) 
#===============================================================================
__all__ += ["ViewCategorySummary"]
class ViewCategorySummary(ViewCategory):
        
    def htmlPresentation(self, dirpath):
        HtmlCategorySummary(self, dirpath)
        return
        
        
#===============================================================================
# ViewSubcategorySummary (may be instantiated) 
#===============================================================================
__all__ += ["ViewSubcategorySummary"]
class ViewSubcategorySummary(ViewSubcategory):
        
    def htmlPresentation(self, dirpath):
        HtmlSubcategorySummary(self, dirpath)
        return
        
#===============================================================================
# ViewAccountSummary (may be instantiated) 
#===============================================================================
__all__ += ["ViewAccountSummary"]
class ViewAccountSummary(ViewSubcategory):

    def sortBeforeTransform(self): return list([ 
        "Category",
        "Subcategory",
        "Account",
        "Year",
    ])
    
    def subsectionChange(self): return list([ 
        "Category",
        "Subcategory",
        "Account",
        "Year",
    ])

    def sectionChange(self): return list([ 
        "Category",
        "Subcategory",
        #"Account",
    ])
        
    def htmlPresentation(self, dirpath):
        HtmlAccountSummary(self, dirpath)
        return
        
#===============================================================================
# ViewYearAccountSummary (may be instantiated) 
#===============================================================================
__all__ += ["ViewYearAccountSummary"]
class ViewYearAccountSummary(ViewSubcategory):

    def sortBeforeTransform(self): return list([ 
        "Year",
        "Category",
        "Subcategory",
        "Account",
    ])
    
    def subsectionChange(self): return list([ 
        "Year",
        "Category",
        #"Subcategory",
        #"Account",
    ])

    def sectionChange(self): return list([ 
        "Year",
        #"Category",
        #"Subcategory",
        #"Account",
    ])
        
    def htmlPresentation(self, dirpath):
        HtmlCategorySummary(self, dirpath)
        return
        

#===============================================================================
# ViewCheckMint 
#===============================================================================
__all__ += ["ViewCheckMint"]        
class ViewCheckMint(View):
    
    # constructor
    def __init__(self, obj):
        self.checkClass(obj, ViewFinance, MasterFinance)
        View.__init__(self, obj)

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
    def normalizeDateField(self, date_text):
        return Container.convertDateWithSlashes(date_text)
    def normalizeAmountField(self, amount_text):
        as_float = Container.getFloat(amount_text)
        return  Container.formatDollars(as_float)

    def sortBeforeTransform(self):  return list([
        "Date",
        "Amount",
    ])

    def sortAfterTransform(self):  return list([
        "Date",
        "Amount",
    ])
        
    def subsectionChange(self):
        return list([ 'Date', 'Amount', ])

    def sectionChange(self):
        return list([ ])

    def collapseOnFields(self):
        return list([])
   
    def initializeTransform(self):
        return

    def isSelectedRow(self, row):
        return True

    def transform(self, this_row, next_row):
        row_out = dict(this_row)
        if this_row['Date'] == 'Date':
            return False, row_out
        if this_row['Transaction Type'] == 'debit':
            maybe_minus = "-"+this_row['Amount']
        elif this_row['Transaction Type'] == 'credit':
            maybe_minus = this_row['Amount']
        else:
            maybe_minus = '0.0'
            print "ERROR: Db_Raw_Finance_Mint: transaction type is not credit or debit"
        row_out['Amount'] = self.normalizeAmountField(maybe_minus)

        row_out['Date'] = self.normalizeDateField(this_row['Date'])              
        return True, row_out
        
    def htmlPresentation(self, dirpath):
        HtmlCheckMint(self, dirpath)
        return

'''                              
