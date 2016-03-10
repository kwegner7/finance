'''
    class Html
'''

import sys, os, re, collections, types, textwrap
from helper.Container import *

#===============================================================================
# html text
#===============================================================================
def tagHref(link, show): return(
    '    <a HREF="' + link + '">' + show + '</a>' )

def tagDiv(contents): return(
    '    <div style="width:200px;float:left>' + contents + '</div>\n' )

def tagSurround(tag, style, contents): return(
    '<' + tag + ' ' + style + '">' + contents +'</' + tag + '>')
    
    
#===============================================================================
# TextWrap
#===============================================================================
class TextWrap(textwrap.TextWrapper):
    
    def __init__(self,
        width_pixels       = 190,
        font_size          = 9,
        line_height        = 11,
        font_weight        = 'bold',
        horizontal_padding = 6 ,      
        vertical_padding   = 5,
        chars_to_wrap      = 31):

        self.width_pixels       = width_pixels
        self.font_size          = font_size
        self.line_height        = line_height
        self.font_weight        = font_weight
        self.horizontal_padding = horizontal_padding
        self.vertical_padding   = vertical_padding
        self.chars_to_wrap      = chars_to_wrap
        
        textwrap.TextWrapper.__init__(self,
            replace_whitespace = True, 
            drop_whitespace    = True,
            break_long_words   = True,
            break_on_hyphens   = False)
        
    def show(self):
        print str(self.width_pixels) + ' x ' + str(self.cellHeight()), 'pixels',
        print self.optimalWidth(), 'chars', self.single_line_out
 
    def wrapAndCheckForNewLines(self, text_in):
        find_pattern = '.*' +'<break>'+ '.*'
        if False:
            if True and re.match(find_pattern,text_in):
                print " BREAKS:", text_in

        divide_this = re.sub('<break><break>', '<break><br>', text_in)

        if ( re.match(find_pattern,divide_this)):
            first_part = re.sub('<break>.*', '', divide_this)
            last_part = re.sub('.*'+'<break>', '', divide_this)
            first_wrapped = self.wrap(first_part)
            last_wrapped = self.wrap(last_part)
            first_wrapped.extend(last_wrapped)
            contains_manual_breaks = True
        else:
            first_wrapped = self.wrap(divide_this)
            contains_manual_breaks = False

        return first_wrapped, contains_manual_breaks
 
    def lineWrapped(self, single_line_in, chars_to_wrap):

        if ( re.match('.*'+'AVOID'+'.*',single_line_in)
        or not re.match('.*'+'[a-z]'+'.*',single_line_in) ):
            chars_to_wrap = int(round(float(chars_to_wrap) * 0.8))
            
        self.width = self.optimalWidth()
        self.width = chars_to_wrap
        self.single_line_in = single_line_in
        
        ''' create vector of string from single long line '''
        self.vector_of_string, contains_manual_breaks = (
            self.wrapAndCheckForNewLines(self.single_line_in))
        
        ''' create single long line out from the vector '''
        self.single_line_out = str()
        for i in range(0, len(self.vector_of_string)):
            if i > 0: self.single_line_out += '<br>'
            self.single_line_out += self.vector_of_string[i]

        if contains_manual_breaks: print "WRAPPED",self.single_line_out
        return self.single_line_out
    
    def numberLines(self):
        return len(self.vector_of_string)

    def optimalWidth(self):
        if (
                self.width_pixels == 1900000
            and self.font_size    == 9
            and self.font_weight  == 'bold'
            and self.horizontal_padding == 6
        ): return 31 # 31
        return self.chars_to_wrap
        return 31

    def cellHeight(self):
        cell_height = (
            self.vertical_padding +
            ((self.numberLines()-1) * self.line_height) + self.font_size +
            self.vertical_padding
        )
        return cell_height

#===============================================================================
# Style
#===============================================================================
class Style(Container):

    # constructor              
    def __init__(self, pairs):
        Container.__init__(self, pairs)
        return None
        
    def style(self):
        lines = VectorOfString()
        for next in self.assoc_array.keys():
            lines.append('   '+next+':'+self.get(next)+';')
        return lines

    def applyStyle(self, tag, tablename):
        text = VectorOfString()
        text.append('#'+tablename+' '+tag)
        text.append('{')
        text.concat(self.style())
        text.append('}')
        return text.write()

    def textStyle(self):
        print "GOTT HERREEE"
        print self.style()
        text = VectorOfString()
        text.append('"')
        text.concat(self.style())
        text.append('"')
        return text.write()

#===============================================================================
# Table
#===============================================================================
class Table():
    def __init__(self, table_name='TABLE'):
        self.table_name = table_name
        if not hasattr(self, 'cfg'):
            self.cfg = collections.namedtuple( 'ConfigureColumns',
            'fieldname, heading, width, CellStyle, fontsize, chars_to_wrap' )

    #===========================================================================
    # these methods determine the main table and items between sections
    #===========================================================================
    def tableStyle(self): pass
    def tableHeadingStyle(self): pass
    def tableRowStyle(self): pass
    def tableCellStyle(self): pass
    def columns(self): pass
    def beginSection(self): pass
    def endSection(self): pass
    def beginSubsection(self): pass
    def endSubsection(self): pass

    #===========================================================================
    # common methods
    #===========================================================================
    def pleaseSortUnique(self):
        return False

    def hideRunningTotalColumn(self, cell):
        return cell.fieldname == 'RunningTotal' and cell.CellStyle == 'hide' 

    def fillTheFields(self, row, bkg_color):
        lines = list()
        color = bkg_color
        lines.append('<tr style=background-color:' + color + '>')
        for cell in self.columns():
            
            # BLANK is white blank
            if cell.fieldname == "BLANK":
                lines.append(
                    '  <td style=background-color:white;>&nbsp;</td>')
                continue
            
            contents_of_field = row[cell.fieldname]
            if self.hideRunningTotalColumn(cell):
                lines.append('  <td style=background-color:white>&nbsp;</td>')
                
            # special for finance
            elif ( cell.CellStyle in ['green', 'funds'] ):
                amount_no_commas = getFloatNoCommas(contents_of_field)
                if   ( amount_no_commas > 0.0 ):           color = 'green'
                elif ( amount_no_commas < 0.0 ):           color = 'red'
                elif ( cell.fieldname == 'DebitSection' ): color = 'red'
                else:                                      color = 'green'

                #print 'fillTheFields', cell.fieldname, color, contents_of_field
                lines.append('  <td class=' + color + '>' + contents_of_field + '</td>')
                
            # normally, use the CellStyle for displaying the contents
            else:
                lines.append('  <td class=' + cell.CellStyle + '>' + contents_of_field + '</td>')
        lines.append('</tr>' )
        return lines

    def insertOneRecord(self, row, bkg_color):
        lines = self.fillTheFields(row, bkg_color)
        if not self.pleaseSortUnique() or self.prev_lines != lines:
            self.prev_lines = lines
            return lines
        else:
            empty = list()
            return empty

    def bookmark(self, text='RaynaAndLevi'):
        bookmark = '<a name='+text+'></a>\n' 
        return bookmark

    def tableBegin(self):
        text = '<table id="' +self.table_name+ '">\n'
        return text
    
    def tableEnd(self):
        return '</table>\n'
    
    def tableWidths(self):
        text = ''
        for next in self.columns():
            if isinstance(next.width, types.StringType):
                text += '   <col style="width:' + str(next.width) + '">\n'
            else:
                text += '   <col style="width:' + str(next.width) + '%">\n'
        return text        
        return self.select_columns.table.columns(self.heading_account)

    def standardTableBegin(self, bookmark):
        text = self.bookmark(bookmark)
        text += self.tableBegin()
        text += self.tableWidths()
        text += self.tableHeadings()
        return text

    def tableHeadings(self):
        text = '<tr>\n'
        
        # special processing of heading when contents style is:
        # funds, date, nowrapr, green, nowrapc, hide
        print "DBG GOT HERE1"
        for next in self.columns():
            invisible = False
            background_white = False
            no_padding = False
            if next.CellStyle in ['funds']:
                align = 'right; '
            elif next.fieldname == "BLANK":
                align = 'center; '
                no_padding = True
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

            # heading alignment is usually left
            # fontsize from columns
            text += (
                '   <th style="' +
                'font-size:' + next.fontsize+'; ' + #'em; ' +
                'text-align:' + align + 
                'white-space:nowrap;'
                )

            if no_padding: text += (
                'padding-left:0px; ' +
                'padding-right:0px; ' 
                #'-ms-transform: rotate(315deg); ' +
                #'-webkit-transform: rotate(315deg); ' +
                #'transform: rotate(315deg); ' 
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

    def tableStyles(self):
        return(
                      #self.tableOneByTwoStyle().applyStyle(          '',     'OneByTwo')
                              self.tableStyle().applyStyle(          '', self.table_name)
            +          self.tableHeadingStyle().applyStyle(        'th', self.table_name)
            +              self.tableRowStyle().applyStyle(        'tr', self.table_name)
            +             self.tableCellStyle().applyStyle(        'td', self.table_name)
            +         self.tableCellLeftStyle().applyStyle(   'td.left', self.table_name)
            +        self.tableCellRightStyle().applyStyle(  'td.right', self.table_name)
            +        self.tableCellGreenStyle().applyStyle(  'td.green', self.table_name)
            +        self.tableCellFundsStyle().applyStyle(  'td.funds', self.table_name)
            +   self.tableCellWhiteRightStyle().applyStyle( 'td.whiter', self.table_name)
            +    self.tableCellWhiteLeftStyle().applyStyle( 'td.whitel', self.table_name)
            +          self.tableCellRedStyle().applyStyle(    'td.red', self.table_name)
            +       self.tableCellCenterStyle().applyStyle( 'td.center', self.table_name)
            +   self.tableCellNowrapLeftStyle().applyStyle('td.nowrapl', self.table_name)
            +  self.tableCellNowrapRightStyle().applyStyle('td.nowrapr', self.table_name)
            + self.tableCellNowrapCenterStyle().applyStyle('td.nowrapc', self.table_name)
            + self.tableCellStandardDateStyle().applyStyle(   'td.date', self.table_name)
            +         self.tableCellHideStyle().applyStyle(   'td.hide', self.table_name)
        )

    def tableOneByTwoStyle(self): return Style(Map({

        #'font-family'     : 'Verdana, Geneva, sans-serif'       ,
        'font-family'     :  '"Lucida Console", Monaco, monospace',
        'border-collapse' : 'collapse'                          ,
        'width'           : '100%'                              ,
        'table-layout'    : 'auto'                              ,
        'font-size'       : '14px'                              ,
        'line-height'     : '14px'                              }))

    #===========================================================================
    # alternate table cell styles
    #===========================================================================
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
        'padding-top': '0px' ,
        'padding-right': '0px' ,
        'padding-bottom': '0px' ,
        'padding-left': '0px' ,
        'text-align': 'center',
        'white-space': 'nowrap' }))

    def tableCellStandardDateStyle(self): return Style(dict({
        #'font-family': 'Verdana, Geneva, monospace',
        'font-family': "'Lucida Console', Monaco, monospace",
        'text-align': 'right',
        'white-space': 'nowrap' }))

    def tableCellHideStyle(self): return Style(dict({
        'background-color': 'white',
              'visibility': 'hidden' }))

    def oneCell(self,
        table_style,
        row_style,
        cell_style,
        contents, percent='100%'):
        
        text = VectorOfString()
        text.append( ''                            )
        text.append( '<table style="'              )
        text.concat(     table_style               )
        text.append( '">'                          )
        text.append( '   <col style=width:'+percent+'>'  )
        text.append( '   <tr style="'              )
        text.concat(        row_style              )
        text.append( '   ">'                       )
        
        text.append( '   <td style="'              )
        text.concat(        cell_style             )
        text.append( '   ">'                       )
        text.append(        contents               )
        text.append( '   </td>'                    )
        
        text.append( '   </tr>'                    )
        text.append( '</table>'                    )
        text.append( ''                            )
        return text.write()

    def twoCells(self,
        table_style,
        row_style,
        cellA_style,
        cellB_style,
        contentsA,
        contentsB, percentA='50%', percentB='50%'):
        
        text = VectorOfString()
        text.append( ''                                 )
        text.append( '<table style="'                   )
        text.concat(     table_style                    )
        text.append( '">'                               )
        text.append( '   <col style=width:'+percentA+'>'      )
        text.append( '   <col style=width:'+percentB+'>'      )
        text.append( '   <tr style="'                   )
        text.concat(        row_style                   )
        text.append( '   ">'                            )
        
        text.append( '   <td style="'                   )
        text.concat(        cellA_style                 )
        text.append( '   ">'                            )
        text.append(        contentsA                   )
        text.append( '   </td>'                         )
        text.append( '   <td style="'                   )
        text.concat(        cellB_style                 )
        text.append( '   ">'                            )
        text.append(        contentsB                   )
        text.append( '   </td>'                         )
        
        text.append( '   </tr>'                         )
        text.append( '</table>'                         )
        text.append( ''                                 )
        return text.write()

    def threeCells(self,
        table_style,
        row_style,
        cellA_style,
        cellB_style,
        cellC_style,
        contentsA,
        contentsB,
        contentsC,
        percentA='33%', percentB='32%', percentC='33%'):
        
        text = VectorOfString()
        text.append( ''                                 )
        text.append( '<table style="'                   )
        text.concat(     table_style                    )
        text.append( '">'                               )
        text.append( '   <col style=width:'+percentA+'>'      )
        text.append( '   <col style=width:'+percentB+'>'      )
        text.append( '   <col style=width:'+percentC+'>'      )
        text.append( '   <tr style="'                   )
        text.concat(        row_style                   )
        text.append( '   ">'                            )
        
        text.append( '   <td style="'                   )
        text.concat(        cellA_style                 )
        text.append( '   ">'                            )
        text.append(        contentsA                   )
        text.append( '   </td>'                         )
        text.append( '   <td style="'                   )
        text.concat(        cellB_style                 )
        text.append( '   ">'                            )
        text.append(        contentsB                   )
        text.append( '   </td>'                         )
        text.append( '   <td style="'                   )
        text.concat(        cellC_style                 )
        text.append( '   ">'                            )
        text.append(        contentsC                   )
        text.append( '   </td>'                         )
        
        text.append( '   </tr>'                         )
        text.append( '</table>'                         )
        text.append( ''                                 )
        return text.write()

    # Begin a one row table
    def manyCellsBegin(self, table_style, row_style, width, first_width=200, second_width=200, number_columns=10):
        
        text = VectorOfString()
        text.append( ''                                 )
        text.append( '<table style="'                   )
        text.concat(     table_style                    )
        text.append( '">'                               )
        text.append( '   <col style=width:'+str(first_width)+'>'      )
        text.append( '   <col style=width:'+str(second_width)+'>'      )
        for i in range(number_columns):
            text.append( '   <col style=width:'+str(width)+'>'      )
        text.append( '   <tr style="'                   )
        text.concat(        row_style                   )
        text.append( '   ">'                            )
        return text.write()
        
    def manyCellsNext(self, cell_style, cell_contents):
        
        text = VectorOfString()        
        text.append( '   <td style="'                   )
        text.concat(        cell_style                  )
        text.append( '   ">'                            )
        text.append(        cell_contents               )
        text.append( '   </td>'                         )
        return text.write()
        
    def manyCellsEnd(self):
       
        text = VectorOfString()        
        text.append( '   </tr>'                         )
        text.append( '</table>'                         )
        text.append( ''                                 )
        return text.write()


'''
    WEB-SAFE FONTS:

        font-family: Arial, Helvetica, sans-serif;
        font-family: 'Arial Black', Gadget, sans-serif;
        font-family: 'Bookman Old Style', serif;
        font-family: 'Comic Sans MS', cursive;
        font-family: Courier, monospace;
        font-family: 'Courier New', Courier, monospace;
        font-family: Garamond, serif;
        font-family: Georgia, serif;
        font-family: Impact, Charcoal, sans-serif;
        font-family: 'Lucida Console', Monaco, monospace;
        font-family: 'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
        font-family: 'MS Sans Serif', Geneva, sans-serif;
        font-family: 'MS Serif', 'New York', sans-serif;
        font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
        font-family: Symbol, sans-serif;
        font-family: Tahoma, Geneva, sans-serif;
        font-family: 'Times New Roman', Times, serif;
        font-family: 'Trebuchet MS', Helvetica, sans-serif;
        font-family: Verdana, Geneva, sans-serif;
        font-family: Webdings, sans-serif;
        font-family: Wingdings, 'Zapf Dingbats', sans-serif;
'''
             
