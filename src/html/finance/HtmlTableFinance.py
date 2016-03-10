'''
    Html_Finance_Subclass.py
'''

#===============================================================================
# imports
#===============================================================================
import abc, collections, string
from helper.Container import *
from abc import abstractmethod
from html.HtmlTable import Base, UsualDefaults
 
#===============================================================================
# public
#===============================================================================
__all__ = \
[
    "UsualDefaults",
    "HtmlModern",
    "HtmlModernNew",
    "HtmlModernAccounts",
    "HtmlModernCategory",
    "HtmlModernSubcategory",
    "HtmlModernSummary",
    "HtmlMonthSummary",
    "HtmlCategorySummary",
    "HtmlSubcategorySummary",
    "HtmlAccountSummary",
    "HtmlGeneric",
    "HtmlSimple",
    "Html_Finance_Default",
    "Html_Finance_Study",
    "Html_Monthly",
    "Html_Natural",
    "Html_NaturalMonth",
    "Html_NaturalCategory",
    "Html_NaturalSubcategory",
    "Html_NaturalCategoryYear",
    "Html_NaturalSubcategoryYear",
    "Html_NaturalAccountYear",
]
#===============================================================================
# HtmlModern 
#===============================================================================
__all__ +=  ['HtmlModern']      
class HtmlModern(UsualDefaults):

    def __init__(self, db, folder_html=None):
        self.db = db
        self.section_field = db.sectionChange()[-1] # year
        self.subsection_field = db.subsectionChange()[-1] # category
        UsualDefaults.__init__(self, db, False, folder_html)

    def summaryOnly(self):
        return False

    def titlePrecedingSection(self, first_row):
        self.writeRowsOfColor('white', 3)
        return

    def titlePrecedingSubsection(self, first_row):
        self.writeRowsOfColor('white', 1)
        return

    def tableHeadings(self):
        return Base.tableHeadings(self)

    def columns(self):
        nature_of_columns = ([
        self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
        self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
        #self.cfg('TotalMonth'         , 'TotalMonth'              ,   0,   'funds', '1.0' ),
        #self.cfg('TotalYear'          , 'TotalYear'               ,   0,   'funds', '1.0' ),
        self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
        self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),        
        #self.cfg('TransferMech1'      , 'Trans1'                  ,   0,  'whitel', '1.0' ),
        #self.cfg('TransferMech2'      , 'Trans2'                  ,   0,  'whitel', '1.0' ),
        #self.cfg('AccountAlias'       , 'Transaction Details'     ,   0,  'whitel', '1.0' ),
        ])
        return nature_of_columns

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        show_monthly = False             
        subsection_value = bottom_row_prev_section[self.subsection_field] 
        if self.subsection_field == 'YearMonth':
            subsection_value = convertStandardDateToYearMonth1(bottom_row_prev_section['Date']) 
        self.doSummaryFollowingSubsection(bottom_row_prev_section, is_final_row, subsection_value, ' ', show_monthly)
        return

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        show_monthly = False             
        section_value = bottom_row_prev_section[self.section_field] 
        if self.section_field == 'Year' and self.subsection_field == 'YearMonth':
            show_monthly = True             
            section_value = 'Year '+bottom_row_prev_section['Year']              
        self.doSummaryFollowingSection(bottom_row_prev_section, is_final_row,section_value, ' ', show_monthly)
        return

    def summaryAtEnd(self, bottom_row_prev_section):
        self.doSummaryAtEnd(bottom_row_prev_section)
        return
        
#===============================================================================
# HtmlModernSummary 
#===============================================================================
__all__ +=  ['HtmlModernSummary']      
class HtmlModernSummary(HtmlModern):

    def __init__(self, db, folder_html):
        HtmlModern.__init__(self, db, folder_html)

    def summaryOnly(self):
        return True

    def columns(self):
        nature_of_columns = list()
        if True:
            nature_of_columns.append(self.cfg('Category'     , self.sectionTitle()    , 0, 'nowrapl', '1.0' ))
        if True:
            nature_of_columns.append(self.cfg('Subcategory'  , self.subsectionTitle() , 0, 'nowrapl', '1.0' ))
            nature_of_columns.append(self.cfg('Amount'       , 'Credit'              , 0,   'funds', '1.0' ))
            nature_of_columns.append(self.cfg('DebitRunning' , 'Debit'               , 0,   'funds', '1.0' ))
            nature_of_columns.append(self.cfg('TotalRunning' , 'Balance'             , 0,   'funds', '1.0' ))
            nature_of_columns.append(self.cfg('CountRunning' , 'Transactions'        , 0, 'nowrapr', '1.0' ))
        return nature_of_columns
        
    # Aug 2014     4,913.70     -10,518.45     -5,604.75     193 transactions
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        color = self.background_color
        cols = self.orderedHtmlColumns()
        section_value = bottom_row_prev_section[self.section_field]
        subsection_value = bottom_row_prev_section[self.subsection_field] 
        stuff = self.blankColumns()
        
        
        stuff['Category'] =  section_value
        stuff['Subcategory'] = subsection_value
        
        # you may want to display the section or sub-section titles in special way
        if self.subsection_field == 'YearMonth':
            stuff['Subcategory'] = convertStandardDateToMonth(bottom_row_prev_section['Date'])              
        
        stuff['Amount'] = subtractStrings( 
                                bottom_row_prev_section['TotalSubsection'],
                                bottom_row_prev_section['DebitSubsection'])    
        stuff['DebitRunning'] = bottom_row_prev_section['DebitSubsection']
        stuff['TotalRunning'] = bottom_row_prev_section['TotalSubsection']
        stuff['CountRunning'] = bottom_row_prev_section['CountSubsection']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')              
        return

    # Year 2014     5,960.55     -101,636.27     -34,169.99     1441 transactions
    # Month Ave     -2,847.50     -2,847.50     -2,847.50      
    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        CreditRunning = subtractStrings( 
            bottom_row_prev_section['TotalRunning'],
            bottom_row_prev_section['DebitRunning'])    
        CreditSection = subtractStrings( 
            bottom_row_prev_section['TotalSection'],
            bottom_row_prev_section['DebitSection'])    
        CreditSubsection = subtractStrings( 
            bottom_row_prev_section['TotalSubsection'],
            bottom_row_prev_section['DebitSubsection'])    
        
        stuff = self.blankColumns()
        stuff['Category'] =     bottom_row_prev_section[self.db.sectionChange()[-1]]
        stuff['Subcategory'] =  '&nbsp;'
        stuff['Amount'] = CreditSection 
        stuff['DebitRunning'] = bottom_row_prev_section['DebitSection']
        stuff['TotalRunning'] = bottom_row_prev_section['TotalSection']
        stuff['CountRunning'] = bottom_row_prev_section['CountSection']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')  
     
        if self.subsection_field == 'YearMonth':
            stuff = self.blankColumns()
            stuff['Category'] =  bottom_row_prev_section[self.db.sectionChange()[-1]]
            stuff['Subcategory'] =  '&nbsp;'
            stuff['Amount'] = avePerMonth(
                CreditSection,
                CreditSubsection,
                bottom_row_prev_section['YearMonth'],
                self.db.master_first_row,
                self.db.master_last_row
            )
            stuff['DebitRunning'] = avePerMonth(
                bottom_row_prev_section['DebitSection'],
                bottom_row_prev_section['DebitSubsection'],
                bottom_row_prev_section['YearMonth'],
                self.db.master_first_row,
                self.db.master_last_row
            )
            stuff['TotalRunning'] = avePerMonth(
                bottom_row_prev_section['TotalSection'],
                bottom_row_prev_section['TotalSubsection'],
                bottom_row_prev_section['YearMonth'],
                self.db.master_first_row,
                self.db.master_last_row
            )
            stuff['CountRunning'] = 'Ave per month'
            self.insertOneSummaryRecord(stuff, color, 'normal')              
        
        return
        
     # Total     349,935.38     -538,920.58     -188,985.20     4580 transactions
    def summaryAtEnd(self, bottom_row_prev_section):
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Category'] = ''
        stuff['Subcategory'] = 'Total'
        stuff['Amount'] = subtractStrings( 
                                bottom_row_prev_section['TotalRunning'],
                                bottom_row_prev_section['DebitRunning'])    
        stuff['DebitRunning'] = bottom_row_prev_section['DebitRunning']
        stuff['TotalRunning'] = bottom_row_prev_section['TotalRunning']
        stuff['CountRunning'] = bottom_row_prev_section['CountRunning']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')              
        self.writeRowsOfColor(color, 1, False)
        return 

        
    # Month     Credit     Debit     Balance     Transactions
    def beginSection(self, writer, first_row):
        self.first_row_of_section = True
        writer.write( self.tableBegin() )
        writer.write( self.tableWidths() )
        self.titlePrecedingSection(first_row)
        if True:
            writer.write( self.tableHeadings() )
            self.background_color = self.getRowColor(first_row)
        return None

    def beginSubsection(self, writer, row, bookmark):
        if self.first_row_of_section:       
            writer.write( self.bookmark(bookmark) )
        self.first_row_of_section = False
        return None

__all__ +=  ['HtmlModernSummary']      
class HtmlMonthSummary(HtmlModernSummary):

    def __init__(self, db, folder_html):
        HtmlModernSummary.__init__(self, db, folder_html)

    def sectionTitle(self): return 'Year'
    def subsectionTitle(self): return 'Month'


       
################################################################################
# rest is obsolete
################################################################################
'''        
stuff[cols[0]] = 'Month Ave'
#print bottom_row_prev_section['Date']
#print convertStandardDateToMonth(bottom_row_prev_section['Date'])
#print convertStandardDateToDay(bottom_row_prev_section['Date'])

#stuff[cols[1]] = avePerMonth(subtractStrings( 
#                 bottom_row_prev_section['TotalSubsection'],
#                 bottom_row_prev_section['DebitSubsection']), bottom_row_prev_section['Date'])  
stuff[cols[1]] = avePerMonth(
                  bottom_row_prev_section['TotalYear'], 
                  bottom_row_prev_section['TotalMonth'], 
                  bottom_row_prev_section['YearMonth']
                  )
stuff[cols[2]] = avePerMonth(
                  bottom_row_prev_section['TotalYear'], 
                  bottom_row_prev_section['TotalMonth'], 
                  bottom_row_prev_section['YearMonth']
                  )
stuff[cols[3]] = avePerMonth(
                  bottom_row_prev_section['TotalYear'], 
                  bottom_row_prev_section['TotalMonth'], 
                  bottom_row_prev_section['YearMonth']
                  )

#stuff[cols[2]] = avePerMonth(bottom_row_prev_section['DebitSection'], bottom_row_prev_section['Date'])
#stuff[cols[3]] = avePerMonth(bottom_row_prev_section['TotalSection'], bottom_row_prev_section['Date'])

stuff[cols[4]] = '&nbsp;'
#self.insertOneSummaryRecord(stuff, color, 'normal')              
return
'''

class HtmlModernNew(UsualDefaults):

    def __init__(self, db, folder_html=None):
        UsualDefaults.__init__(self, db, False, folder_html)

    def summaryOnly(self):
        return False
        
    def beginSubsection(self, writer, row, bookmark):
        #self.writeRowsOfColor('white', 1)
        self.first_row_of_section = False
        return None

    def titlePrecedingSection(self, first_row):
        self.writeRowsOfColor('white', 3)
        return

    def titlePrecedingSubsection(self, first_row):
        #self.writeRowsOfColor('white', 1)
        return

    def tableHeadings(self):
        return ''
        return Base.tableHeadings(self)

    def columns(self):
        nature_of_columns = ([
        self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
        self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
        self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
        self.cfg('TotalSection'       , 'TotalSection'            ,   0,   'funds', '1.0' ),
        self.cfg('YearMonth'          , 'YearMonth'               ,   0, 'nowrapl', '1.0' ),
        self.cfg('TotalCategory'      , 'TotalCategory'           ,   0,   'funds', '1.0' ),
        self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
        self.cfg('TotalSubsection'    , 'TotalSubsection'         ,   0,   'funds', '1.0' ),
        self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),  
        ])
        return nature_of_columns

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        return
        self.doSummaryFollowingSubsection(bottom_row_prev_section, is_final_row,
            'Year '+bottom_row_prev_section['Year'],
            convertStandardDateToYearMonth1(bottom_row_prev_section['Date']),
            False)
        return

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        return
        self.doSummaryFollowingSection(bottom_row_prev_section, is_final_row,
            'Year '+bottom_row_prev_section['Year'],
            ' ',
            True)
        return

    def summaryAtEnd(self, bottom_row_prev_section):
        return
        self.doSummaryAtEnd(bottom_row_prev_section)
        return

__all__ += ['HtmlCheckMint']       
class HtmlCheckMint(UsualDefaults):

    def __init__(self, db, folder_html=None):
        UsualDefaults.__init__(self, db, False, folder_html)

    def summaryOnly(self):
        return False
        
    def beginSubsection(self, writer, row, bookmark):
        self.writeRowsOfColor('white', 1)
        self.first_row_of_section = False
        return None

    def titlePrecedingSection(self, first_row):
        self.writeRowsOfColor('white', 3)
        return

    def titlePrecedingSubsection(self, first_row):
        self.writeRowsOfColor('white', 1)
        return

    def tableHeadings(self):
        return Base.tableHeadings(self)

    def columns(self):
        nature_of_columns = ([
        self.cfg('Date'        , 'Date'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Amount'        , 'Amount'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Description'        , 'Description'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Original Description'        , 'Original Description'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Transaction Type'        , 'Transaction Type'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Category'        , 'Category'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Account Name'        , 'Account Name'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Labels'        , 'Labels'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Notes'        , 'Notes'             ,   0, 'nowrapl', '1.0' ),
        ])
        return nature_of_columns
        

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False): return

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False): return

    def summaryAtEnd(self, bottom_row_prev_section):
        return

#2A
class HtmlModernCategory(HtmlModern):

    def __init__(self, db, folder_html=None):
        HtmlModern.__init__(self, db, folder_html)

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        self.doSummaryFollowingSubsection(bottom_row_prev_section, is_final_row,
            'Category: '+bottom_row_prev_section['Category'],
            'Year ' + bottom_row_prev_section['Year'],
            True )
        return

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        self.doSummaryFollowingSection(bottom_row_prev_section, is_final_row,
            'Category: '+bottom_row_prev_section['Category'],
            ' ' ,
            False )
        return

#3A
class HtmlModernSubcategory(HtmlModern):

    def __init__(self, db, folder_html=None):
        HtmlModern.__init__(self, db, folder_html)

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        self.doSummaryFollowingSubsection(bottom_row_prev_section, is_final_row,
            'Subcategory: '+bottom_row_prev_section['Subcategory'],
            'Year ' + bottom_row_prev_section['Year'],
            True )
        return

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        self.doSummaryFollowingSection(bottom_row_prev_section, is_final_row,
            'Subcategory: '+bottom_row_prev_section['Subcategory'],
            ' ' ,
            False )
        return

#1B
__all__ +=  ['HtmlYearSummary']      
class HtmlYearSummary(HtmlModernSummary):

    def __init__(self, db, folder_html=None):
        HtmlModernSummary.__init__(self, db, folder_html)

    def columns(self):
        nature_of_columns = ([
        self.cfg('Year'               , 'Year'                ,   0,    'date', '1.0' ),
        self.cfg('Amount'             , 'Credit'              ,   0,   'funds', '1.0' ),
        self.cfg('Category'           , 'Debit'               ,   0,   'funds', '1.0' ),
        self.cfg('Subcategory'        , 'Balance'             ,   0,   'funds', '1.0' ),
        self.cfg('TotalYear'        , 'TotalYear'             ,   0,   'funds', '1.0' ),
        self.cfg('CountSection' , 'Transactions'        ,   0, 'nowrapr', '1.0' ),
        ])
        return nature_of_columns
        
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        color = self.background_color
        cols = self.orderedHtmlColumns()
        
        stuff = self.blankColumns()
        stuff[cols[0]] = bottom_row_prev_section['Year']
        stuff[cols[1]] = subtractStrings( 
                         bottom_row_prev_section['TotalSubsection'],
                         bottom_row_prev_section['DebitSubsection'])    
        stuff[cols[2]] = bottom_row_prev_section['DebitSubsection']
        stuff[cols[3]] = bottom_row_prev_section['TotalSubsection']
        stuff[cols[4]] = avePerMonth(
                          bottom_row_prev_section['TotalYear'], 
                          bottom_row_prev_section['TotalMonth'], 
                          bottom_row_prev_section['YearMonth']
                          )
        stuff[cols[5]] = bottom_row_prev_section['CountSubsection']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')              
        return
        
    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False): return

#2B
class HtmlCategorySummary(HtmlModernSummary):

    def __init__(self, db, folder_html=None):
        HtmlModernSummary.__init__(self, db, folder_html)

    def titlePrecedingSection(self, first_row):
        self.writeRowsOfColor('white', 1)
        return
        
    def columns(self, include_subcategory=False, include_account=False):

        nature_of_columns = list()
        nature_of_columns.append(self.cfg('Category'        , padr('Category',20)    , 0, 'nowrapl', '1.0'))
        if include_subcategory:
             nature_of_columns.append(
                                 self.cfg('Subcategory'     , padr('Subcategory',31) , 0, 'nowrapl', '1.0'))
        if include_account:
             nature_of_columns.append(
                                 self.cfg('Account'         , padr('Account',34)     , 0, 'nowrapl', '1.0'))
        nature_of_columns.append(self.cfg('Year'            ,          'Year'        , 0, 'nowrapl', '1.0'))
        nature_of_columns.append(self.cfg('CreditSubsection', padl('Credit',11)      , 0,   'funds', '1.0'))
        nature_of_columns.append(self.cfg('DebitSubsection' , padl('Debit',11)       , 0,   'funds', '1.0'))
        nature_of_columns.append(self.cfg('TotalSubsection' , padl('Balance',11)     , 0,   'funds', '1.0'))
        nature_of_columns.append(self.cfg('Amount'          , padl('Ave Month',11)   , 0,   'funds', '1.0'))
        nature_of_columns.append(self.cfg('CountSubsection' , padl('Transactions',17), 0, 'nowrapr', '1.0'))
        return nature_of_columns
        
    def summaryFollowingSubsection(self, 
        bottom_row_prev_section, is_final_row=False,
        include_subcategory=False, include_account=False):
            
        color = self.background_color
        cols = self.orderedHtmlColumns()
        
        stuff = self.blankColumns()
        stuff['Category'] = bottom_row_prev_section['Category']
        if include_subcategory:
            stuff['Subcategory'] = bottom_row_prev_section['Subcategory']
        if include_account:
            stuff['Account'] = bottom_row_prev_section['Account']
        stuff['Year'] = bottom_row_prev_section['Year']
        stuff['CreditSubsection'] = subtractStrings( 
                         bottom_row_prev_section['TotalSubsection'],
                         bottom_row_prev_section['DebitSubsection'])    
        stuff['DebitSubsection'] = bottom_row_prev_section['DebitSubsection']
        stuff['TotalSubsection'] = bottom_row_prev_section['TotalSubsection']
        #stuff['Amount'] = avePerMonth(bottom_row_prev_section['TotalSubsection'], bottom_row_prev_section['Date'])
        if True:
            stuff['Amount'] = avePerMonth(
                              bottom_row_prev_section['TotalYear'], 
                              bottom_row_prev_section['TotalMonth'], 
                              bottom_row_prev_section['YearMonth']
                              )
        stuff['CountSubsection'] = str(bottom_row_prev_section['CountSubsection'])+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')              
        return

    def summaryFollowingSection(self, 
        bottom_row_prev_section, is_final_row=False,
        include_subcategory=False, include_account=False):
            
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Category'] = bottom_row_prev_section['Category']
        if include_subcategory:
            stuff['Subcategory'] = bottom_row_prev_section['Subcategory']
        if include_account:
            stuff['Account'] = bottom_row_prev_section['Account']
        stuff['CreditSubsection'] = bottom_row_prev_section['CreditSection']       
        stuff['DebitSubsection'] = bottom_row_prev_section['DebitSection']
        stuff['TotalSubsection'] = bottom_row_prev_section['TotalSection']
        stuff['CountSubsection'] = str(bottom_row_prev_section['CountSection'])+' transactions'

        self.insertOneSummaryRecord(stuff, color, 'normal')              
        return

    def summaryFollowingSection(self, 
        bottom_row_prev_section, is_final_row=False,
        include_subcategory=False, include_account=False): return
        
    def summaryAtEnd(self, bottom_row_prev_section):
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Category'] = 'Grand Total '
        #stuff['Subcategory'] = 'Grand Total '
        stuff['CreditSubsection'] = subtractStrings( 
                         bottom_row_prev_section['TotalRunning'],
                         bottom_row_prev_section['DebitRunning'])           
        stuff['DebitSubsection'] = bottom_row_prev_section['DebitRunning']
        stuff['TotalSubsection'] = bottom_row_prev_section['TotalRunning']
        stuff['CountSubsection'] = bottom_row_prev_section['CountRunning']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')              
        self.writeRowsOfColor(color, 1, False)
        return
#3B
class HtmlSubcategorySummary(HtmlCategorySummary):

    def __init__(self, db, folder_html=None):
        HtmlCategorySummary.__init__(self, db, folder_html)

    def columns(self):
        return HtmlCategorySummary.columns(self, True, False)

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        return HtmlCategorySummary.summaryFollowingSubsection(self, 
            bottom_row_prev_section, is_final_row, True, False)

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        return HtmlCategorySummary.summaryFollowingSection(self, 
            bottom_row_prev_section, is_final_row, True, False)

class HtmlAccountSummary(HtmlCategorySummary):

    def __init__(self, db, folder_html=None):
        HtmlCategorySummary.__init__(self, db, folder_html)

    def columns(self):
        return HtmlCategorySummary.columns(self, True, True)

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        return HtmlCategorySummary.summaryFollowingSubsection(self, 
            bottom_row_prev_section, is_final_row, True, True)

    def summaryFollowingSection(self, bottom_row_prev_section, is_final_row=False):
        return HtmlCategorySummary.summaryFollowingSection(self, 
            bottom_row_prev_section, is_final_row, True, True)















        
class HtmlModernAccounts(HtmlModern):

    def __init__(self, db, folder_html=None):
        HtmlModern.__init__(self, db, folder_html)

    def columns(self):
        nature_of_columns = ([
        self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),        
        self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
        self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
        self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
        self.cfg('AccountAlias'       , 'Transaction Details'     ,   0,  'whitel', '1.0' ),
        self.cfg('TransferMech1'      , 'Trans1'                  ,   0,  'whitel', '1.0' ),
        self.cfg('TransferMech2'      , 'Trans2'                  ,   0,  'whitel', '1.0' ),
        self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
        ])
        return nature_of_columns
        
#==============================================================================
# HtmlGeneric
#==============================================================================
class HtmlGeneric(UsualDefaults):
    
    def __init__(self, db, folder_html=None):
        UsualDefaults.__init__(self, db, False, folder_html)

    def mapFieldnameToStyle(self, fieldname):
        if fieldname == 'Count': return 'whiter'
        return 'nowrapl'
                                   
    def columns(self):
        nature_of_columns = list()
        for fieldname in self.db_in.fieldnames:
            style = self.mapFieldnameToStyle(fieldname)
            next = self.cfg(fieldname, fieldname, 0, style, '1.0')
            nature_of_columns.append(next)            
        return nature_of_columns

    def summaryFollowingSubsection__(self, bottom_row_prev_section, is_final_row=False):
        self.writeRowsOfColor(self.background_color, 1, False)
        
        column = 0
        stuff = dict()
        for fld in self.orderedHtmlColumns():
            column = column + 1
            stuff[fld] = '&nbsp;'
            if column == 1: stuff[fld] = 'Nary'
            if column == 2: stuff[fld] = 'Love'
               
        self.insertOneSummaryRecord(stuff, self.background_color, 'normal')          
        self.writeRowsOfColor(self.background_color, 1, False)
        return None
        
#==============================================================================
# HTML table showing all columns of the csv file
#==============================================================================
class HtmlSimple(UsualDefaults):
    
    def __init__(self, db, folder_html=None):
        UsualDefaults.__init__(self, db, False, folder_html)

    def mapFieldnameToStyle(self, fieldname):
        if fieldname == 'Amount':     return 'funds'
        if fieldname == 'Running':    return 'funds'
        if fieldname == 'Section':    return 'funds'
        if fieldname == 'Subsection': return 'funds'
        if fieldname == 'Date':       return 'date'
        if fieldname == 'Count':      return 'whiter'
        return 'nowrapl'
                                   
    def columns(self):
        nature_of_columns = list()
        for fieldname in self.db_in.fieldnames:
            style = self.mapFieldnameToStyle(fieldname)
            next = self.cfg(fieldname, fieldname, 0, style, '1.0')
            nature_of_columns.append(next)            
        return nature_of_columns

    def summaryFollowingSubsectionn(self, bottom_row_prev_section, is_final_row=False):
        self.writeRowsOfColor(self.background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'
        blank_fields['Date']        = convertStandardDateToYearMonth1(bottom_row_prev_section['Date'])
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        
        blank_fields['Amount']      = bottom_row_prev_section['Subsection']
        blank_fields['Account']     = 'Month---Total of '+bottom_row_prev_section['SubsectionCount']+' transactions'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  

        blank_fields['Amount']      = bottom_row_prev_section['Section']
        blank_fields['Account']     = 'Year----Total of '+bottom_row_prev_section['SectionCount']+' transactions'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['Running']
        blank_fields['Account']     = 'Running Total of '+bottom_row_prev_section['Count']+' transactions'

        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None

__all__ += ['Html_Finance_Default']        
class Html_Finance_Default(UsualDefaults):
    #def __init__(self, db, folder_html=None):
    #    UsualDefaults.__init__(self, db, False, folder_html)
                      
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        
        if self.hide_detail_columns:
            nature_of_columns = ([
            self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
            self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
            self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
            self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
            self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),        
            ])
        else:
            nature_of_columns = ([
            self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
            self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
            self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
            self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
            self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
            self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),        
            #self.cfg('NumberTransactions' , ''                        ,   0,  'whiter', '1.0' ),
            #self.cfg('RunningTotal'       , 'Running'                 ,   0,   'funds', '1.0' ),
            self.cfg('TransferMech1'      , 'Trans1'         ,   0,  'whitel', '1.0' ),
            self.cfg('TransferMech2'      , 'Trans2'         ,   0,  'whitel', '1.0' ),
            #self.cfg('SimplifiedAlias'    , 'SimplifiedAlias Details' ,   0,  'whitel', '1.0' ),
            self.cfg('AccountAlias'       , 'Transaction Details'     ,   0,  'whitel', '1.0' ),
            ])
                
        return nature_of_columns

    def columnsHistorical(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        if True:
            nature_of_columns = ([
            self.cfg('AccountAlias'           , 'AccountAlias'                ,   0, 'nowrapl', '1.0' ),
            self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
            self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
            self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
            ])
        return nature_of_columns

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'         

        self.writeRowsOfColor(self.background_color, 1, False)
         
        blank_fields['Amount']      = bottom_row_prev_section['RunningCredit']
        blank_fields['Account']     = 'Credit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningDebit']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningTotal']
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['NumberTransactions']+' transactions'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        self.writeRowsOfColor(self.background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = convertStandardDateToYearMonth1(bottom_row_prev_section['Date'])
        blank_fields['Date']        = '&nbsp;'
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['CreditSection']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['DebitSection']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['TotalSection']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['CountSection']+' transactions'

        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None

               
class Html_Finance_Study(Html_Finance_Default):
                      
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        
        nature_of_columns = ([
        self.cfg('Institution'        , 'Institution'             ,   0, 'nowrapl', '1.0' ),
        self.cfg('Date'               , 'Date'                    ,   0,    'date', '1.0' ),
        self.cfg('Category'           , 'Category'                ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'        , 'Subcategory'             ,   0, 'nowrapl', '1.0' ),        
        self.cfg('Amount'             , 'Amount'                  ,   0,   'funds', '1.0' ),
        self.cfg('Account'            , 'Account Name'            ,   0, 'nowrapl', '1.0' ),
        self.cfg('TransferMech2'      , 'Mint Category'           ,   0,  'whitel', '1.0' ),
        self.cfg('SimplifiedAlias'    , 'Simple Alias'            ,   0,  'whitel', '1.0' ),
        self.cfg('AccountAlias'       , 'Transaction Details'     ,   0,  'whitel', '1.0' ),
        ])
                
        return nature_of_columns

class Html_Natural(Html_Finance_Default):

    def titlePrecedingSection(self, first_row):
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Account'] = 'BEGIN ANOTHER YEAR'
        
        self.writeRowsOfColor('white', 1, False)
        self.insertOneTitleRecord(blank_fields, 'white', 'normal')  
        self.writeRowsOfColor('white', 1, False)
        return None

    def titlePrecedingSubsection(self, first_row):
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Account'] = 'BEGIN ANOTHER MONTH'
        
        self.writeRowsOfColor('white', 1, False)
        self.insertOneTitleRecord(blank_fields, 'white', 'normal')  
        self.writeRowsOfColor('white', 1, False)
        return None
                      
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_last_row=False):
        self.writeRowsOfColor(self.background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = convertStandardDateToYearMonth1(bottom_row_prev_section['Date'])
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['SubCreditSection']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['SubDebitSection']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['SubTotalSection']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['NumberTransSubSection']+' transactions'

        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        self.writeRowsOfColor(color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = bottom_row_prev_section['Year']
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['CreditSection']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['DebitSection']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['TotalSection']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['CountSection']+' transactions'

        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        self.writeRowsOfColor(color, 1, False)
        return None
        
    def summaryAtEnd(self, bottom_row_prev_section):
        color = 'white'
        self.writeRowsOfColor(color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = 'Running Total'
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['RunningCredit']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningDebit']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningTotal']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['NumberTransactions']+' transactions'

        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        
        self.writeRowsOfColor(color, 1, False)
        return None

class Html_NaturalMonth(Html_Natural):

    def beginSection(self, writer, first_row):
        self.first_row_of_section = True
        writer.write( self.tableBegin() )
        writer.write( self.tableWidths() )
        self.titlePrecedingSection(first_row)
        writer.write( self.tableHeadings() )
        self.background_color = self.getRowColor(first_row)
        return None

    def titlePrecedingSection(self, first_row):
        self.writeRowsOfColor('white', 2)
        return None
    
    def beginSubsection(self, writer, row, bookmark):
        self.first_row_of_section = False
        return None

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        return None
    
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('YearMonth'             , ''             ,   0, 'date', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'funds', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'funds', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['YearMonth']        = 'Year '+bottom_row_prev_section['Year']
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

    def summaryAtEnd(self, bottom_row_prev_section):
        color = 'white'
        self.writeRowsOfColor(color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['YearMonth']        = 'Total'
        blank_fields['SubCreditSection'] = bottom_row_prev_section['RunningCredit']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['RunningDebit']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['RunningTotal']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['NumberTransactions']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

class Html_NaturalCategory(Html_NaturalMonth):
    
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('YearMonth'             , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'fundsg', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'fundsr', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['YearMonth']        = bottom_row_prev_section['YearMonth']
        blank_fields['Category']         = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

class Html_NaturalCategoryYear(Html_NaturalCategory):
    
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('Year'                  , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'fundsg', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'fundsr', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Year']             = bottom_row_prev_section['Year']
        blank_fields['Category']         = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None


class Html_NaturalSubcategory(Html_NaturalMonth):
    
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('YearMonth'             , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'           , 'Subcategory'  ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'fundsg', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'fundsr', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['YearMonth']        = bottom_row_prev_section['YearMonth']
        blank_fields['Category']         = ''
        blank_fields['Subcategory']      = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

class Html_NaturalSubcategoryYear(Html_NaturalSubcategory):
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('Year'                  , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'           , 'Subcategory'  ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'fundsg', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'fundsr', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Year']             = bottom_row_prev_section['Year']
        blank_fields['Category']         = ''
        blank_fields['Subcategory']      = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

class Html_NaturalAccountYear(Html_NaturalSubcategory):
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('Year'                  , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'           , 'Subcategory'  ,   0, 'nowrapl', '1.0' ),
        self.cfg('Account'               , 'Account'      ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'fundsg', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'fundsr', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Year']             = bottom_row_prev_section['Year']
        blank_fields['Category']         = ''
        blank_fields['Subcategory']      = ''
        blank_fields['Account']      = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None

class Html_NaturalAccount(Html_NaturalMonth):
    
    def columns(self):
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize' )
        return ([
        self.cfg('YearMonth'             , ''             ,   0, 'date', '1.0' ),
        self.cfg('Category'              , 'Category'     ,   0, 'nowrapl', '1.0' ),
        self.cfg('Subcategory'           , 'Subcategory'  ,   0, 'nowrapl', '1.0' ),
        self.cfg('Account'               , 'Account    '  ,   0, 'nowrapl', '1.0' ),
        self.cfg('SubTotalSection'       , 'Balance'      ,   0, 'funds', '1.0' ),        
        self.cfg('SubCreditSection'      , 'Credit'       ,   0, 'funds', '1.0' ),        
        self.cfg('SubDebitSection'       , 'Debit'        ,   0, 'funds', '1.0' ),        
        self.cfg('NumberTransSubSection' , 'Transactions' ,   0, 'nowrapr', '1.0' ),        
        ])
        
    def summaryFollowingSection(self, bottom_row_prev_section):
        color = 'white'
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['YearMonth']        = bottom_row_prev_section['YearMonth']
        blank_fields['Category']         = ''
        blank_fields['Subcategory']      = ''
        blank_fields['Account']          = ''
        blank_fields['SubCreditSection'] = bottom_row_prev_section['CreditSection']
        blank_fields['SubDebitSection']  = bottom_row_prev_section['DebitSection']
        blank_fields['SubTotalSection']  = bottom_row_prev_section['TotalSection']
        blank_fields['NumberTransSubSection']  = bottom_row_prev_section['CountSection']
        self.insertOneSummaryRecord(blank_fields, color, 'normal')  
        return None


class Html_Monthly(Html_Finance_Default):
                      
    def summaryFollowingSubsection0(self, bottom_row_prev_section):
        self.writeRowsOfColor(self.background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = convertStandardDateToYearMonth1(bottom_row_prev_section['Date'])
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['CreditSection']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['DebitSection']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['TotalSection']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['CountSection']+' transactions'

        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None

    def grandTotals(self, bottom_row_prev_section):
        background_color = 'white'
        self.writeRowsOfColor(background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = 'Running Total'
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['RunningCredit']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningDebit']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningTotal']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['NumberTransactions']+' transactions'

        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        self.writeRowsOfColor(background_color, 1, False)
        return None

                  
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_last_row=False):
        self.summaryFollowingSubsection0(bottom_row_prev_section)
        if is_last_row:
            self.grandTotals(bottom_row_prev_section)
                        

class Html_Category(Html_Finance_Default):
    
    def __init__(self, db_in, hide_detail_columns=False):
        self.sectionChange = db_in.sectionChange()        
        self.subsectionChange = db_in.subsectionChange()        
        self.folder_out = db_in.folder
        Html_Finance_Default.__init__(self, db_in, hide_detail_columns)
        return None
        
    def summaryOnly(self): return True
                      
    def summaryFollowingSubsection0(self, bottom_row_prev_section):
        self.writeRowsOfColor(self.background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = convertStandardDateToYearMonth1(bottom_row_prev_section['Date'])
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['CreditSection']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = bottom_row_prev_section['Category']
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['DebitSection']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['TotalSection']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['CountSection']+' transactions'

        self.insertOneSummaryRecord(blank_fields, self.background_color, 'normal')  
        
        self.writeRowsOfColor(self.background_color, 1, False)
        return None

    def grandTotals(self, bottom_row_prev_section):
        background_color = 'white'
        self.writeRowsOfColor(background_color, 1, False)
        blank_fields = dict()
        for fld in self.orderedHtmlColumns(): blank_fields[fld] = '&nbsp;'  
        blank_fields['Date']        = 'Running Total'
        blank_fields['Mechanism']   = '&nbsp;'
        blank_fields['Amount']      = bottom_row_prev_section['RunningCredit']
        blank_fields['Account']     = 'Credit'
        blank_fields['Category']    = '&nbsp;'
        blank_fields['Subcategory'] = '&nbsp;'
        blank_fields['NumberTransactions'] = '&nbsp;'
        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningDebit']
        blank_fields['Account']     = 'Debit'
        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        blank_fields['Amount']      = bottom_row_prev_section['RunningTotal']
        blank_fields['Account']     = 'Net'
        blank_fields['Account']     = 'Balance of '+bottom_row_prev_section['NumberTransactions']+' transactions'

        self.insertOneSummaryRecord(blank_fields, background_color, 'normal')  
        
        self.writeRowsOfColor(background_color, 1, False)
        return None

                  
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_last_row=False):
        self.summaryFollowingSubsection0(bottom_row_prev_section)
        if is_last_row:
            self.grandTotals(bottom_row_prev_section)

