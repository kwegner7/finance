'''
    AbstractMethods
    Base
    UsualDefaults
'''

import sys, os, re, collections, abc
from helper.Container import *
from html.helpers.Html import Style

########################################################################
# AbstractMethods which determine the class tree
########################################################################
class AbstractMethods(object):
    __metaclass__ = abc.ABCMeta
        
    @abc.abstractmethod
    def summaryOnly(self): pass
            
    @abc.abstractmethod
    def splitSectionsIntoSeparateFiles(self): pass
    
    # the first few rows of the table are a title for the section
    # by default each field is blank white
    @abc.abstractmethod
    def titlePrecedingSection(self, first_row): pass

    # begin a new table, each section is a separate table
    @abc.abstractmethod
    def beginSection(self, writer, first_row): pass

    # the first few rows of a new subsection are a title for the subsection
    # by default this is not used
    @abc.abstractmethod
    def titlePrecedingSubsection(self, first_row): pass

    # a subsection is a continuation of the section table
    # possibly a bookmark is placed here and the table headings are printed
    @abc.abstractmethod
    def beginSubsection(self, writer, row, bookmark): pass

    # each row of the table is written
    @abc.abstractmethod
    def columns(self): pass

    @abc.abstractmethod
    def endSubsection(self, writer, monitor, is_final_row): pass

    # the last few rows of the subsection are subtotals
    @abc.abstractmethod
    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row): pass

    # this prints subtotals for section then closes the table
    @abc.abstractmethod
    def endSection(self, writer, last_row, end_of_file): pass

    # the last few rows of the section are subtotals
    @abc.abstractmethod
    def summaryFollowingSection(self, bottom_row_prev_section): pass

    @abc.abstractmethod
    def summaryAtEnd(self, bottom_row_prev_section): pass


########################################################################
# HtmlTable.Base
#    These are the fixed final common protected methods
########################################################################
class Base(AbstractMethods):

    def __init__(self, db_in, hide_detail_columns=False, htmlfullpath=None):
        self.db_in = db_in
        self.htmlfullpath = htmlfullpath
        self.sectionChange = db_in.sectionChange()        
        self.subsectionChange = db_in.subsectionChange()        
        self.hide_detail_columns = hide_detail_columns
        self.csv_special_fields = db_in
        self.tablename = 'CsvTable'
        self.fieldsDeterminingSection = self.sectionChange
        self.fieldsDeterminingSubsection = self.subsectionChange
        self.colors = Colors()
        self.heading_account = self.headingAccount()
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple('ConfigureColumns',
            'fieldname,heading, width, CellStyle, fontsize')
        self.createHtmlTables(db_in)
        pass
    
    ########################################################################
    # These are the fixed final common protected methods of the Base class
    ########################################################################
    def subfolder(self):
        return '/html'

    def headingAccount(self):
        return 'Account'
    
    def getRowColor(self, row):
        return self.colors.getCyclicColors()

    def bookmark(self, text='RaynaAndLevi'):
        text = '<a name='+text+'></a>\n'    
        return text
    
    def tableHeadings(self):
        text = '<tr>\n'
        
        for next in self.columns():
            invisible = False
            background_white = False
            if next.CellStyle in ['funds','fundsg','fundsr']:
                align = 'right; '
            elif next.CellStyle in ['date']:
                align = 'right; '
                background_white = True
                background_white = False
            elif next.CellStyle in ['nowrapr', 'green']:
                align = 'right; '
            elif next.CellStyle in ['nowrapc']:
                align = 'center; '
            elif next.CellStyle in ['hide']:
                align = 'right; '
                invisible = True
            else:
                align = 'left; '

            text += (
                '   <th style="' +
                'font-size:' + next.fontsize+'em; ' +
                'text-align:' + align + 
                'white-space:nowrap;'
                )

            if background_white: text += (
                'background-color:white; ')

            if invisible: text += (
                'background-color:white; ' +
                'visibility:hidden; ')

            text += (
                '">' +
                next.heading +
                '</th>\n')

        text += '</tr>\n'
        return text
            
    def monthlyYearly(self):
        if 'Year' in self.fieldsDeterminingSubsection: return 'Year'
        if 'YearMonth' in self.fieldsDeterminingSubsection: return 'YearMonth'
        return ''
    
    def orderedHtmlColumns(self):
        fieldnames = [ cell.fieldname for cell in self.columns() ]
        return fieldnames
    
    def pleaseSortUnique(self):
        return False

    def hideRunningTotalColumn(self, cell):
        return cell.fieldname == 'RunningTotal' and cell.CellStyle == 'hide' 
    
    def determineBookmark(self, row):
        if len(self.fieldsDeterminingSection) == 0:
            section_name = ''
        else:
            section_name = ''
            first_time = True
            for next in self.fieldsDeterminingSection:
                if first_time:
                    first_time = False
                    section_name = row[next]
                else:
                    section_name = section_name + '-' + row[next]
        return String(section_name).removeBlanksAndSlashes()
            
    def determineFilename(self, html_filename, row):
        if len(self.fieldsDeterminingSection) == 0:
            section_name = ''
        else:
            section_name = ''
            for next in self.fieldsDeterminingSection:
                section_name = section_name + '-' + row[next]
        if self.splitSectionsIntoSeparateFiles():
            return String(
                re.sub('\.html', section_name+'.html', html_filename)).removeBlanks()
        else:
            return String(html_filename).removeBlanks()

    
    def fillTheTitleFields(self, row, bkg_color, font_weight='normal'):
        lines = list()
        color = bkg_color
        
        # set the background color for the whole row
        lines.append('<tr style=background-color:' + color + '>')
        
        # for each field in the row
        for cell in self.columns():
            contents_of_field = row[cell.fieldname]
            lines.append('  <td class=' +'nowrapl' + '>' + contents_of_field + '</td>')
        lines.append('</tr>' )
        return lines
    
    def fillTheFields(self, row, bkg_color, font_weight='normal'):
        lines = list()
        color = bkg_color
        # set the background color for the whole row
        lines.append('<tr style=background-color:' + color + '>')
        for cell in self.columns():
            #if not cell.fieldname in row.keys(): return lines
            contents_of_field = row[cell.fieldname]
            #if contents_of_field == 'null': return lines
            if self.hideRunningTotalColumn(cell):
                lines.append('  <td style=background-color:white>&nbsp;</td>')
            elif ( cell.CellStyle in ['green', 'funds'] ):
                amount_no_commas = getFloatNoCommas(contents_of_field)
                if   ( amount_no_commas > 0.0 ):           color = 'green'
                elif ( amount_no_commas < 0.0 ):           color = 'red'
                #elif ( cell.fieldname == 'DebitSection' ): color = 'green'
                else:                                      color = 'green'
                lines.append('  <td class=' + color + '>' + contents_of_field + '</td>')
            else:
                lines.append('  <td class=' + cell.CellStyle + '>' + contents_of_field + '</td>')
        lines.append('</tr>' )
        return lines
    
    #===========================================================================    
    # sets the background color and font weight for the whole row  
    #===========================================================================    
    def fillTheSummaryFields(self, row, bkg_color, font_weight='normal'):
        lines = list()
        color = bkg_color
        
        # set the default background for the whole row
        lines.append(
            '<tr style="font-weight:' + font_weight +
            ';background-color:' + color + ';">')

        # set the color of the font for each cell
        # set the color of the background for each cell
        for cell in self.columns():
            contents_of_field = row[cell.fieldname]
            if contents_of_field == 'null': return lines # I think this is for Special Camp
            if self.hideRunningTotalColumn(cell):
                lines.append('  <td style=background-color:white>&nbsp;</td>')
            elif ( contents_of_field == '&nbsp;' ):
                lines.append('  <td class=' + 'nowrapl' + '>' + contents_of_field + '</td>')
            elif ( cell.CellStyle in ['green', 'funds'] ):
                amount_no_commas = getFloatNoCommas(contents_of_field)
                if ( amount_no_commas > 0.0 ):        color = 'green'
                elif ( amount_no_commas < 0.0 ):        color = 'red'
                else:                                   color = 'green'
                lines.append('  <td class=' + color + '>' + contents_of_field + '</td>')
            else:
                lines.append('  <td class=' + cell.CellStyle + '>' + contents_of_field + '</td>')
        lines.append('</tr>' )
        return lines


    #===========================================================================
    # If transition to a new section (not end of csv file yet)
    #    endSubsection
    #    endSection
    #    beginSubsection
    #    beginSection
    # else if transition to a new subsection
    #    endSubsection
    #    beginSubsection
    # insert this row into the table (if not summary only)
    #===========================================================================
    def writeRowsOfTable(self, row, prev_row, html_filename):

        #########################################################
        # Determine if section or subsection has changed
        #########################################################
        self.monitor.slideFieldValues(row)
        self.section_has_changed = bool(
            self.monitor.fieldHasChanged(self.fieldsDeterminingSection))
        self.subsection_has_changed = bool(
            self.monitor.fieldHasChanged(self.fieldsDeterminingSubsection))

        #########################################################
        # if main section has changed
        #   write sub-totals for previous sub-section
        #   if splitting
        #       write html commands to end the table
        #       close file
        #       open new file with name based on main sort field
        #       write top html commands
        #   write headings for new section and new sub-section
        #   change the background color for the next sub-section
        #########################################################
        if self.section_has_changed:

            # what to do at the end of a subsection
            self.endSubsection(self.writer, self.monitor, False)
            
            # what to do at the end of a section
            self.endSection(self.writer, prev_row)
            
            if self.splitSectionsIntoSeparateFiles():
                self.endBodyAndHtml()
                self.closeTable()
                
                self.openTable(self.determineFilename(html_filename, row))
                self.beginHtml(row)
                self.defineStyles(row)
                self.beginBody(row)
                
            # what to do at the beginning of a section
            self.beginSection(self.writer, row)

            # what to do at the beginning of a subsection
            bookmark = String(self.determineBookmark(row)).removeBlanksAndSlashes()
            self.beginSubsection(self.writer, row, bookmark)
            
            # advance the color
            #self.background_color = self.getRowColor(row)

        #########################################################
        # Else if sub-section has changed
        #   write sub-totals for previous sub-section
        #   write headings for new sub-section
        #   change the background color for the next sub-section
        #########################################################
        elif self.subsection_has_changed:

            # what to do at the end of a subsection
            self.endSubsection(self.writer, self.monitor, False)

            # what to do at the beginning of the next subsection
            bookmark = String(self.determineBookmark(row)).removeBlanksAndSlashes()
            self.beginSubsection(self.writer, row, bookmark)
 
            # advance the color            
            #self.background_color = self.getRowColor(row)

        #########################################################
        # write the row (this may be under a new section or subsection)
        #########################################################
        if not self.summaryOnly():
            self.insertOneRecord(row, self.background_color, 'normal')

        return None

    #===========================================================================
    # This is the main entry point to write the HTML code
    #
    # Loop over each row of the ordered, accumulated CSV file
    #    If this is the first row
    #        write the HTML code including styles at the top of the file
    #        write HTML code to beginSection
    #        write HTML code to beginSubsection
    #    write one row of the table (based on previous row)
    #
    # Write endSection
    # Write endSubsection
    # Write HTML code at bottom of file      
    #===========================================================================
    def createHtmlTables(self, csv_file):

        html_fullpath = self.htmlfullpath
        html_folder =  os.path.dirname(html_fullpath)

        touchFolder(html_folder)

        # loop over the csv file
        csv_file.openRead() 
        first_row = True
        for row in csv_file.reader:
            if first_row:
                first_row = False
                prev_row = row
                
                # initialize color of table cells
                self.background_color = self.getRowColor(row)
                
                # we must detect when section and subsection changes
                self.monitor = MonitorField()

                # top of the html file, begin section, begin subsection                
                self.openTable(self.determineFilename(html_fullpath, row))
                self.beginHtml(row)
                self.defineStyles(row)
                self.beginBody(row)
                
                # what to do when a new section begins
                self.beginSection(self.writer, row)
                
                # what to do when a new subsection begins
                bookmark = String(self.determineBookmark(row)).removeBlanksAndSlashes()
                self.beginSubsection(self.writer, row, bookmark)

            # write rows and sub-totals and begin new sections and subsections                
            self.writeRowsOfTable(row, prev_row, html_fullpath)
            prev_row = row
            pass
        
        # done writing html, end last subsection and last section
        if not first_row:
            
            # what to do at the end of a subsection
            self.endSubsection(self.writer, self.monitor, True)
            
            # what to do at the end of a section
            self.endSection(self.writer, prev_row, True)
            
            # finish the html file
            self.endBodyAndHtml()
            self.closeTable()
        csv_file.closeRead()
        print "    HTML IS AT:", html_fullpath   
        self.html_fullpath = html_fullpath
             
    ####################################################################
    # helpers
    ####################################################################

    def blankColumns(self):
        blanks = dict();
        for fld in self.orderedHtmlColumns(): blanks[fld] = '&nbsp;' 
        return blanks

    def writeln(self, line):
        self.writer.write( line+'\n' )
        return None
    
    def writeRowsOfColor(self, color, how_many, date_is_white=False):
        for i in range(how_many):
            self.writeln( '<tr>' )
            for next in self.columns():
                if date_is_white and next.fieldname in ['Amount']:
                    self.writeln('  <td style="background-color:' +'white'+ '; border-style:none">&nbsp;</td>')
                else:
                    self.writeln('  <td style="background-color:' +color+ '; border-style:none">&nbsp;</td>')
            self.writeln('</tr>' )
            
    def writeRowsOfSummaryColor(self, color, how_many, date_is_white=False):
        for i in range(how_many):
            self.writeln( '<tr>' )
            for next in self.columns():
                if date_is_white and next.fieldname in ['Amount']:
                    self.writeln('  <td style="background-color:' +'white'+ '; border-style:none">&nbsp;</td>')
                else:
                    self.writeln('  <td style="background-color:' +color+ '; border-style:none">&nbsp;</td>')
            self.writeln('</tr>' )
            
    def insertOneRecord(self, row, bkg_color, font_weight):
        lines = self.fillTheFields(row, bkg_color, font_weight)
        for line in lines: self.writeln(line)
        return None
            
    def insertOneTitleRecord(self, row, bkg_color, font_weight):
        lines = self.fillTheTitleFields(row, bkg_color, font_weight)
        for line in lines: self.writeln(line)
        return None
            
    def insertOneSummaryRecord(self, row, bkg_color, font_weight):
        lines = self.fillTheSummaryFields(row, bkg_color, font_weight)
        for line in lines:
            self.writeln(line)
        return None
    
    ####################################################################
    # writeStartOfTable
    ####################################################################
    def htmlBegin(self): return (
        '<html>\n'
    )

    def headBegin(self): return (
        '<head>\n'
    )

    def stylesBegin(self): return (
        '<style type="text/css">\n'
    )
    
    def tableStyles(self):
        return(
                      self.tableOneByTwoStyle().applyStyle(          '',     'OneByTwo')
            +                 self.tableStyle().applyStyle(          '', self.tablename)
            +          self.tableHeadingStyle().applyStyle(        'th', self.tablename)
            +              self.tableRowStyle().applyStyle(        'tr', self.tablename)
            +             self.tableCellStyle().applyStyle(        'td', self.tablename)
            +         self.tableCellLeftStyle().applyStyle(   'td.left', self.tablename)
            +        self.tableCellRightStyle().applyStyle(  'td.right', self.tablename)
            +        self.tableCellGreenStyle().applyStyle(  'td.green', self.tablename)
            +        self.tableCellFundsStyle().applyStyle(  'td.funds', self.tablename)
            +        self.tableCellFundsgStyle().applyStyle('td.fundsg', self.tablename)
            +        self.tableCellFundsrStyle().applyStyle('td.fundsr', self.tablename)
            +   self.tableCellWhiteRightStyle().applyStyle( 'td.whiter', self.tablename)
            +    self.tableCellWhiteLeftStyle().applyStyle( 'td.whitel', self.tablename)
            +          self.tableCellRedStyle().applyStyle(    'td.red', self.tablename)
            +       self.tableCellCenterStyle().applyStyle( 'td.center', self.tablename)
            +   self.tableCellNowrapLeftStyle().applyStyle('td.nowrapl', self.tablename)
            +  self.tableCellNowrapRightStyle().applyStyle('td.nowrapr', self.tablename)
            + self.tableCellNowrapCenterStyle().applyStyle('td.nowrapc', self.tablename)
            + self.tableCellStandardDateStyle().applyStyle(   'td.date', self.tablename)
            +         self.tableCellHideStyle().applyStyle(   'td.hide', self.tablename)
        )
        
    def stylesEnd(self): return (
        '</style>\n'
    )
    
    def headEnd(self): return (
        '</head>\n'
    )
    
    def htmlEnd(self): return (
        '</html>\n'
    )

    def bodyBegin(self): return (
        '<body style="font-size:14px; line-height:14px; margin:10px 1px 30px 100px;">\n'
    )
    
    def tableBegin(self):
        text = '<table id="' +self.tablename+ '">\n'
        return text
    
    def tableEnd(self):
        text = '</table>\n'
        return text
    
    def tableWidths(self):
        text = ''
        for next in self.columns():
            text += '   <col width=' + str(next.width) + '%>\n'
        return text 
        '''
        <td style="width:130px"> 
        '''      
    
    def tableWidthsPx(self):
        text = ''
        for next in self.columns():
            text += '   <col width=' + str(next.width) + '>\n'
        return text        

    def openTable(self, html_filename):
        self.writer = open(html_filename, 'wb')
        return None

    def beginHtml(self, first_row):
        self.writer.write( self.htmlBegin() )
        self.writer.write( self.headBegin() )
        
    def defineStyles(self, first_row):
        self.writer.write( self.stylesBegin() )
        self.writer.write( self.tableStyles() )
        self.writer.write( self.stylesEnd() )
        
    def beginBody(self, first_row):
        self.writer.write( self.headEnd() )
        #self.writer.write( self.htmlEnd() )
        self.writer.write( self.bodyBegin() )

    ####################################################################
    # writeEndOfTable
    ####################################################################
    def endBodyAndHtml(self):
        self.writer.write('</body>')
        self.writer.write('</html>')

    def closeTable(self):
        self.writer.close()
    
    ####################################################################
    # These are all of the styles for the table
    ####################################################################
    def tableStyle(self): return Style(Map({

        #'font-family'     : 'Verdana, Geneva, sans-serif'       ,
        'font-family':  '"Lucida Console", Monaco, monospace',
        'border-collapse' : 'collapse'                          ,
        #'width'           : '100%'                              ,
        'width'           : '0%'                                ,
        'table-layout'    : 'auto'                              ,
        'font-size'       : '12px'                              ,
        'line-height'     : '12px'                              }))
        #'font-size'       : '14px'                              ,
        #'line-height'     : '14px'                              }))

    def tableOneByTwoStyle(self): return Style(Map({

        #'font-family'     : 'Verdana, Geneva, sans-serif'       ,
        'font-family':  '"Lucida Console", Monaco, monospace',
        'border-collapse' : 'collapse'                          ,
        'width'           : '100%'                              ,
        'table-layout'    : 'auto'                              ,
        'font-size'       : '14px'                              ,
        'line-height'     : '14px'                              }))

    def tableHeadingStyle(self): return Style(Map({

                'font-size': '1.0em'           ,
               'text-align': 'left'            ,
                   'border': '1px solid black' ,
                   'border': '1px none #DCDCDC'  ,
                  'padding': '3px 10px 3px 10px' ,
         'background-color': '#DCDCDC'           ,
                    'color': 'black'           ,
               'font-style': 'italic'          }))

    def tableRowStyle(self): return Style(Map({

                'font-size': '1.0em'  ,
              'font-weight': 'normal' ,
                    'color': 'black'  ,
         'background-color': 'white'  }))

    def tableCellStyle(self): return Style(Map({

         'text-align': 'center'          ,
             'border': '1px none grey'   ,
            'padding': '3px 10px 3px 10px' }))

    def tableCellLeftStyle(self): return Style(dict({
        'text-align': 'left' }))

    def tableCellRightStyle(self): return Style(dict({
        'text-align': 'right' }))

    def tableCellGreenStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'green',
        'text-align': 'right' }))

    def tableCellFundsStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'green',
        'text-align': 'right' }))

    def tableCellFundsgStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'green',
        'text-align': 'right' }))

    def tableCellFundsrStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'red',
        'text-align': 'right' }))

    def tableCellWhiteRightStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'black',
        'white-space': 'nowrap',
        'text-align': 'right' }))

    def tableCellWhiteLeftStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'black',
        'white-space': 'nowrap',
        'text-align': 'left' }))

    def tableCellRedStyle(self): return Style(dict({
        'background-color': 'white',
        'color': 'red',
        'text-align': 'right' }))

    def tableCellCenterStyle(self): return Style(dict({
        'text-align': 'center' }))

    def tableCellNowrapLeftStyle(self): return Style(dict({
        'text-align': 'left',
        'white-space': 'nowrap' }))

    def tableCellNowrapRightStyle(self): return Style(dict({
        'text-align': 'right',
        'white-space': 'nowrap' }))

    def tableCellNowrapCenterStyle(self): return Style(dict({
        'text-align': 'center',
        'white-space': 'nowrap' }))

    def tableCellStandardDateStyle(self): return Style(dict({
        #'font-family': 'Verdana, Geneva, monospace',
        'font-family':  '"Lucida Console", Monaco, monospace',
        'text-align': 'right',
        'white-space': 'nowrap' }))

    def tableCellHideStyle(self): return Style(dict({
        'background-color': 'white',
              'visibility': 'hidden' }))
         
    ####################################################################
    # end styles
    ####################################################################

    ####################################################################
    # more fixed final helpers
    ####################################################################
    
    '''
      'Date'      'Amount'     'Account'
       
      Credit      5,043.14     Aug 2015            
      Debit     -10,918.16                
      Balance    -5,875.02     131 transactions
    '''
    def doSummaryFollowingSubsection(self,
            bottom_row_prev_section,
            is_final_row=False,
            section='',        # this will be printed first row right column
            subsection='',     # this will be printed second row right column
            show_monthly=False):
                
        color = self.background_color
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Credit'
        stuff['Amount'] = subtractStrings( 
                              bottom_row_prev_section['TotalSubsection'],
                              bottom_row_prev_section['DebitSubsection'])    
        stuff['Account'] = section       
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Debit'
        stuff['Amount'] = bottom_row_prev_section['DebitSubsection']       
        stuff['Account'] = subsection      
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Balance'
        stuff['Amount'] = bottom_row_prev_section['TotalSubsection']       
        stuff['Account'] = bottom_row_prev_section['CountSubsection']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')  
                    
        if show_monthly:
            stuff = self.blankColumns()
            stuff['Date'] = 'Month Ave' 
            stuff['Amount'] = avePerMonth(bottom_row_prev_section['TotalSubsection'])
            stuff['Account'] = '&nbsp;'
            self.insertOneSummaryRecord(stuff, color, 'normal')  
                    
        self.writeRowsOfColor(color, 1, False)
        return

        
    def doSummaryFollowingSection(self,
            bottom_row_prev_section, is_final_row=False,
            section='', subsection='', show_monthly=False):
                
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Credit'
        stuff['Amount'] = subtractStrings( 
                              bottom_row_prev_section['TotalSection'],
                              bottom_row_prev_section['DebitSection'])    
        stuff['Account'] = section       
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Debit'
        stuff['Amount'] = bottom_row_prev_section['DebitSection']       
        stuff['Account'] = subsection      
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Balance'
        stuff['Amount'] = bottom_row_prev_section['TotalSection']       
        stuff['Account'] = bottom_row_prev_section['CountSection']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal')  
                    
        if show_monthly:
            stuff = self.blankColumns()
            stuff['Date'] = 'Month Ave'
            stuff['Amount'] = avePerMonth(bottom_row_prev_section['TotalSection'])
            stuff['Account'] = '&nbsp;'
            self.insertOneSummaryRecord(stuff, color, 'normal')  

        self.writeRowsOfColor(color, 1, False)
        return

    def doSummaryAtEnd(self, bottom_row_prev_section):
        color = 'white'
        cols = self.orderedHtmlColumns()
        self.writeRowsOfColor(color, 1, False)
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Credit'
        stuff['Amount'] = subtractStrings( 
                              bottom_row_prev_section['TotalRunning'],
                              bottom_row_prev_section['DebitRunning'])    
        stuff['Account'] = 'Grand Total'
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Debit'
        stuff['Amount'] = bottom_row_prev_section['DebitRunning']       
        stuff['Account'] = '&nbsp;'
        self.insertOneSummaryRecord(stuff, color, 'normal')  
        
        stuff = self.blankColumns()
        stuff['Date'] = 'Balance'
        stuff['Amount'] = bottom_row_prev_section['TotalRunning']       
        stuff['Account'] = bottom_row_prev_section['CountRunning']+' transactions'
        self.insertOneSummaryRecord(stuff, color, 'normal') 
        return 

########################################################################
# UsualDefaults - default implementation of the AbstractMethods
########################################################################
class UsualDefaults(Base):
        
    def summaryOnly(self):
        return False
            
    def splitSectionsIntoSeparateFiles(self):
        return False

    #===================================================================        
    # by default, two rows with every field blank white
    # <td style="background-color:white; border-style:none">&nbsp;</td>
    #===================================================================        
    def titlePrecedingSection(self, first_row):
        if self.summaryOnly():
            self.writeRowsOfColor('white', 1)
        else:
            self.writeRowsOfColor('white', 2)
        return None

    #==========================================================================
    # At the beginning of a section:
    #    begin the table
    #    specify the column widths
    #    as table rows, print some title for the section
    #==========================================================================       
    def beginSection(self, writer, first_row):
        self.first_row_of_section = True
        writer.write( self.tableBegin() )
        writer.write( self.tableWidths() )
        self.titlePrecedingSection(first_row)
        return None
        
    def titlePrecedingSubsection(self, first_row):
        return None

    #==========================================================================
    # At the beginning of a subsection:
    #    if also beginning of a section, write a bookmark
    #    as rows of the table, write a title for this subsection
    #    write the table headings
    #    advance the background color
    #    write a blank row with new color
    #==========================================================================       
    def beginSubsection(self, writer, row, bookmark):
        if self.first_row_of_section:       
            writer.write( self.bookmark(bookmark) )
        self.titlePrecedingSubsection(row)
        if not self.summaryOnly():
            writer.write( self.tableHeadings() )
            # advance the color            
            self.background_color = self.getRowColor(row)
            self.writeRowsOfColor(self.background_color, 1, False)
        self.first_row_of_section = False
        return None
        
    #==========================================================================
    # At the end of a subsection:
    #    as rows of the table, print a summary of this subsection
    #==========================================================================       
    def endSubsection(self, writer, monitor, is_final_row):
        # check if this is last row of the file
        bottom_row_prev_section = monitor.prev_fields
        last_row_of_csv_file = monitor.new_fields

        if is_final_row:
            row = last_row_of_csv_file
        else:
            row = bottom_row_prev_section

        if True:
            self.summaryFollowingSubsection(row, is_final_row)
        else:
            self.summaryRecordsOnly(self.howManyBlankRows(), row,
                'TotalSection', 'CreditSection', 'DebitSection' )
            if monitor.fieldHasChanged('Year') or is_final_row:
                self.summaryRecordsOnly(1, row,
                    'YearTotal', 'YearCredit', 'YearDebit' )
        return None

    def summaryFollowingSubsection(self, bottom_row_prev_section, is_final_row=False):
        return None
                  
    #==========================================================================
    # At the end of a section:
    #    as table rows, print a section summary
    #    end the table
    #==========================================================================       
    def endSection(self, writer, last_row, end_of_file=False):
        self.summaryFollowingSection(last_row)
        if True and end_of_file:
            #print "DBG endSection"
            self.summaryAtEnd(last_row)            
        writer.write( self.tableEnd() )
        return None

    def summaryFollowingSection(self, bottom_row_prev_section):
        return None

    def summaryAtEnd(self, bottom_row_prev_section):
        return None
        