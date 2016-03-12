
import sys, csv, os, shutil, collections, re, datetime, string, tempfile

###############################################################################
# allow access to these internal items
############################################################################### 
__all__ = \
[
    "EquivalenceTree", "EquivalenceTreePrint",
    "MapAccountToEquivalence1", "MapAccountToLevels",
    "Container",
    "Const", "State", "Virtual", "SHOW",
    "KeyedObject",
    "String",
    "List",
    "Map",
    "VectorOfString",
    "EquivClasses",
    "pureVirtual",
    "convertDateWithSlashes",
    "convertDateToYear",
    "convertDateToYearMonth",
    "Colors",
    "RunningTotals",
    "getNegativeAmounts",
    "getFloat", "getFloatNoCommas", "avePerMonth",
    "formatDollars",
    "MonitorField",
    "convertToStandardDate",
    "removeDayFromDate",
    "clearFolder",
    "touchFolder",
    "temporaryFolder",
    "getPaypalAdjusted",
    "getAsPositive", "dirnameSlash","dirnameNoSlash",
    "convertStandardDateToMonth",
    "convertStandardDateToDay",
    "convertStandardDateToYearMonth",
    "convertStandardDateToYearMonth1",
    "padr",
    "padl",
    "subtractStrings",
]

Const = None
State = None
Virtual = None
SHOW = True

def padr(title, total_chars):
    size_title = len(title)
    if total_chars > size_title:
        padded = title + ('&nbsp;' * (total_chars-size_title))
    else:
        padded = title
    return padded

def padl(title, total_chars):
    size_title = len(title)
    if total_chars > size_title:
        padded =  ('&nbsp;' * (total_chars-size_title)) + title
    else:
        padded = title
    return padded
    
def subtractStrings(amount1, amount2):
    float1 = getFloatNoCommas(amount1)
    float2 = getFloatNoCommas(amount2)
    return formatDollars(float1-float2)
    
########################################################################
# clearFolder
########################################################################
class BaseFolder():
    # __file__ is the absolute location of this Container.py
    def __init__(self, abs_path_to_file):      
        self.location = (
            os.path.abspath(
                os.path.dirname(
                    os.path.dirname(abs_path_to_file))))          
TheBaseFolder = None
    
class InFolder():
    def __init__(self, abs_path_to_folder):      
        self.location = abs_path_to_folder
TheInFolder = None
    
class OutFolder():
    def __init__(self, abs_path_to_folder):      
        self.location = abs_path_to_folder
TheOutFolder = None
    
def touchFolder(folder): 
    if not os.access(folder, os.F_OK):
        os.makedirs(folder)

def clearFolder(folder): 
    if os.access(folder, os.F_OK):
        shutil.rmtree(folder)
    touchFolder(folder)
    
def temporaryFolder():
    tmp_folders = '/tmp/folders/'
    os.system ("mkdir --parents " + tmp_folders)
    return tempfile.mkdtemp(prefix='FOLDER-',dir=tmp_folders)
    
def dirnameSlash(fullpath): 
    return os.path.dirname(fullpath)+'/'        
        
def dirnameNoSlash(fullpath): 
    return os.path.dirname(fullpath)     

###############################################################################
# SubsetPath
###############################################################################
class SubsetPath():
             
    def __init__(self):      
        self.subset_path = list()
        self.subset_indices = list()
        self.subset_indent = list()
             
    def push(self, subset_number, subset):      
        self.subset_path.append(subset)
        self.subset_indices.append(subset_number)
        self.subset_indent.append(self.textOfIndices()+' ')
             
    def pop(self):      
        self.subset_path.pop()
        self.subset_indices.pop()
        self.subset_indent.pop()

    def getIndentToIndices(self):
        accum = str()
        size = len(self.subset_indent)
        for i in range(size):
            if i < size-1:
                text = self.subset_indent[i]
                accum += text
        if len(accum) > 0:
            return ' '.ljust(len(accum))
        else:
            return ''

        return ' '.ljust(len(accum))

    def getIndentToElements(self):
        accum = str()
        for text in self.subset_indent:
            accum += text
        return ' '.ljust(len(accum))

    def textOfIndices(self):
        accum = str()
        for i in range(len(self.subset_indices)):
            index = self.subset_indices[i]
            if i < len(self.subset_indices)-1:
                accum += str(index) + '.'
            else:
                accum += str(index)
        return accum

    def wellOrderedPath(self):
        well_ordering = list()
        for i in range(len(self.subset_path)):
            subset_name = self.subset_path[i].getTitle()
            well_ordering.append(subset_name)
        return well_ordering

    def equals(self, other):
        this_path = self.wellOrderedPath()
        other_path = other.wellOrderedPath()
        return (this_path == other_path)
 
###############################################################################
# EquivalenceTree
#   Elements are organized into multiple equivalence classes. There is exactly
#   one Subset at the top of the tree. Each Subset contains only Subsets
#   except the minimal Subset of each path consists of Elements only. The total
#   number of equivalence subdivisions of the Elements is equal to the height
#   of the tree.
###############################################################################
class EquivalenceTree():
             
    ########################### 
    # private state          
    ########################### 
    def __init__(self, top_level_set):
        self.initialize(top_level_set)

    def initialize(self, top_level_set):      
        self.top = top_level_set
        self.path = SubsetPath()
        self.height = 0
             
    ########################### 
    # private refactor methods
    ########################### 
    def doSomething(self, subset, elements):
        pass
             
    ########################### 
    # private local methods
    ########################### 
    def traverse(self, subset_number, subset):
        self.path.push(subset_number, subset)
        level = len(self.path.subset_indices)
        self.height = max(self.height, level)
        elements = list()

        for i in range(len(subset)):
            next_item_in_subset = subset[i]
            if isinstance(next_item_in_subset, Element):
                elements.append(next_item_in_subset)

        found, value = self.doSomething(subset, elements, level, self.path.subset_path)
        if found: self.value_to_return = value

        for i in range(len(subset)):
            next_item_in_subset = subset[i]
            if isinstance(next_item_in_subset, Subset):
                self.traverse(i+1, next_item_in_subset)

        self.path.pop()
        return self.value_to_return

    ########################### 
    # public local methods
    ########################### 
    def printTree(self):
        self.value_to_return = str('Not Found')
        i = 0
        for item in self.top:
            if isinstance(item, Subset):
                i += 1
                self.traverse(i, item)
                print_it = (
                    'The height of the tree "' + item.getTitle()
                     + '" is ' + str(self.height)
                )
                print print_it

    ########################### 
    # public local methods
    ########################### 
    def getCategory(self, element_name):
        self.value_to_find = element_name
        self.value_to_return = str('Not Found')
        self.traverse(1, self.top)
        return self.value_to_return

    ########################### 
    # public local methods
    ########################### 
    def getLevels(self, element_name):
        self.value_to_find = element_name
        self.value_to_return = ['','','','']
        self.traverse(1, self.top)
        return self.value_to_return

###############################################################################
# EquivalenceTreePrint
###############################################################################
class EquivalenceTreePrint(EquivalenceTree):
             
    ########################### 
    # private state          
    ########################### 
    def __init__(self, top_level_set):
        EquivalenceTree.__init__(self, top_level_set)
             
    ########################### 
    # private virtual methods
    ########################### 
    def doSomething(self, subset, elements, level, path):
        print (
            self.path.getIndentToIndices() +
            self.path.textOfIndices() + " " + 
            subset.getTitle()
        )
        for element in elements:
            print  (
                self.path.getIndentToElements() + 
                element.getTitle()
            )
        return False, str('None')


###############################################################################
# MapAccountToEquivalence1
###############################################################################
class MapAccountToEquivalence1(EquivalenceTree):
             
    ########################### 
    # private state          
    ########################### 
    def __init__(self, top_level_set):
        EquivalenceTree.__init__(self, top_level_set)
             
    ########################### 
    # private virtual methods
    ########################### 
    def doSomething(self, subset, elements, level, path):
        for element in elements:
            if element.getTitle() == self.value_to_find:
                broader = True
                if broader:
                    return True, path[2].getTitle()
                else:
                    return True, subset.getTitle()
        return False, str('Not Found')

###############################################################################
# MapAccountToLevels
###############################################################################
class MapAccountToLevels(EquivalenceTree):
             
    ########################### 
    # private state          
    ########################### 
    def __init__(self, top_level_set):
        EquivalenceTree.__init__(self, top_level_set)
             
    ########################### 
    # private virtual methods
    ########################### 
    def doSomething(self, subset, elements, level, path):
        for element in elements:
            if element.getTitle() == self.value_to_find:
                if len(path) == 4:
                    path_names = [ path[1].getTitle(), path[2].getTitle(), path[3].getTitle() ]
                else:
                    path_names = [ path[1].getTitle(), path[2].getTitle(), '' ]
                return True, path_names
        return False, str('Not Found')

###############################################################################
# pureVirtual
###############################################################################
def pureVirtual():
    print "ERROR: method not implemented"
    raise
def PublicFixed():
    print "ERROR: method not implemented"
    raise
def PublicVirtual():
    print "ERROR: method not implemented"
    raise
def PrivateVirtual():
    print "ERROR: method not implemented"
    raise

###############################################################################
# KeyedObject
###############################################################################
class KeyedObject():

    # state
    key = Const
    obj = Const

    # constructor              
    def __init__(self, key, obj):
        self.key = key
        self.obj = obj
        return None
       
    # method              
    def text(self):
        print "Key:",self.key,"Object:",self.obj
        return None

###############################################################################
# String
###############################################################################
class String():

    line = State
             
    def __init__(self, text=''):
        self.line = text
        return None
                  
    def append(self, other):
        self.line += other
        return None

    def show(self):
        print self.line
        return None

    def removeBlanks(self):
        return string.strip(re.sub('[ \t\n\r\f\v]+', '', self.line))

    def removeBlanksAndSlashes(self):
        return string.strip(re.sub('[/\\\ \t\n\r\f\v]+', '', self.line))

    def repeatCharacter(self, how_many):
        return self.line.rjust(how_many, self.line[0])

    def whiteSpaceToBlank(self):
        return string.strip(re.sub('[ \t\n\r\f\v]+', ' ', self.line))

    def whiteSpaceToBlankAndCapitalize(self):
        return string.strip(re.sub('[ \t\n\r\f\v]+', ' ', self.line)).upper()

    def removeBlanksAndNumbers(self):
        result = string.strip(re.sub('[ \t\n\r\f\v0123456789#*-.()/&\']+', '', self.line))
        #print "DBG size of simplified", len(result), result,  self.line
        if len(result) == 0:
            #print "Account Alias has numbers only", result, len(result), self.line            
            result = self.line           
        #if len(self.line) <= 0:
            #print "DBG field is empty", result, len(result), self.line 
            #result = 'BLANK' 
        return result

    def sub(self, find, replace):
        return re.sub(find, replace, self.line)
        
    def rstrip(self):
        return self.line.rstrip()

###############################################################################
# List
###############################################################################
class List(list):
             
    def __init__(self, items=[]):      
        list.__init__(self, items)
        return None

###############################################################################
# Map
###############################################################################
class Map(dict):
             
    def __init__(self, pairs={}):      
        dict.__init__(self, pairs)
        return None

###############################################################################
# Relation
###############################################################################
class Relation(dict):
             
    def __init__(self, key_list={}):      
        dict.__init__(self, key_list)
        return None

    def inverse(self):
        return None

###############################################################################
# VectorOfStrings
###############################################################################
class VectorOfString():
             
    def __init__(self, first_item=None):
        self.vector = list()
        if first_item != None:
            self.append(first_item)
        return None
                  
    def append(self, line):
        self.vector.append(line)
        return None
                  
    def concat(self, other):
        self.vector.extend(other.vector)
        return None
                  
    def show(self):
        for line in self.vector: print line
        return None
                  
    def write(self):
        lines = String()
        for line in self.vector: lines.append(line+'\n')
        return lines.line

###############################################################################
# StoredVectorOfStrings
###############################################################################
class StoredVectorOfStrings():

    # state
    key = Const
    obj = Const

    # constructor              
    def __init__(self, key, obj):
        self.key = key
        self.obj = obj
        return None
       
    # method              
    def text(self):
        print "Key:",self.key,"Object:",self.obj
        return None

###############################################################################
# Container
###############################################################################
class Container():

    # state
    assoc_array = State

    # constructor              
    def __init__(self, pairs=None):
        if pairs == None: 
            self.assoc_array = dict()
        else:
            self.assoc_array = pairs
        return None

    # method              
    def add(self, key, obj=None):
       if isinstance(key, KeyedObject):
           self.assoc_array[key.key] = key.obj
       else:
           self.assoc_array[key] = obj
       return None
       
    # method              
    def get(self, key):
        if self.contains(key):
            return self.assoc_array[key]
        else:
            return self.assoc_array.values()[0]
       
    # method              
    def contains(self, key):
        return key in self.assoc_array
       
    # method              
    def text(self):
        if False: print self.assoc_array.items()
        for next in self.assoc_array:
            print 'NEXT',next
        return None

###############################################################################
# EquivClasses
###############################################################################
class EquivClassesFixedMethods( object ):
    def __init__(self) : object.__init__(self)

    def getAllMembersOf(self, classname) : pureVirtual()
    def getClassName(self, item)         : pureVirtual()

class EquivClassesVirtualMethods( EquivClassesFixedMethods ):
    def __init__(self) : EquivClassesFixedMethods.__init__(self) 
         
    def classNames(self) : pureVirtual()
    def matchesCriteriaOfEquivClass0(self, classname, item1, item2='', item3='') : pureVirtual()

class EquivClasses(EquivClassesVirtualMethods):            
    def __init__(self):
        EquivClassesVirtualMethods.__init__(self)

        self.equiv_class_names = self.classNames()
        pass

    def addElementToClass(self, classname, item):
        self.equiv_classes[classname].add(item)
        return None

    def getAllMembersOf(self, classname):
        return self.equiv_classes[classname]

    def getClassNameOfWAS(self, item):
        for classname in self.equiv_class_names:
            if item in self.getAllMembersOf(classname):
                return classname
        return 'UNCLASSIFIED'

    def text(self):
        for classname in self.equiv_class_names:
            print "CLASS:", classname
            for item in self.getAllMembersOf(classname):
                print "    ", self.getClassName(item), item
        return NonegetAsPositive

    def classify(self, original_set):
        self.original_set = original_set
        self.equiv_classes = dict()

        for classname in self.equiv_class_names:
            self.equiv_classes[classname] = set()

        for item in self.original_set:
            found = False
            for classname in self.equiv_class_names:
                if self.matchesCriteriaOfEquivClass(classname, item):
                    self.addElementToClass(classname, item)
                    found = True
                    break
            if not found: self.addElementToClass('UNCLASSIFIED', item)
        return None

    def getClassName(self, item1, item2='', item3=''):
        for classname in self.equiv_class_names:
            found, title = self.matchesCriteriaOfEquivClass(classname, item1, item2, item3)
            if found: return title
        return 'UNKNOWN MECHANISM'

    def getMechanismName(self, item1, item2='', item3=''):
        classname = self.getClassName(item1, item2, item3)
        out = re.sub(' \(credit\)','', classname)
        out = re.sub(' \(debit\)','', out)
        return out

    def matchesLeadingText(self, set_of_patterns, item):
        for pattern in set_of_patterns:
            find_pattern = '^' +pattern+ '+'
            if re.match(find_pattern, item): return True
        return False

    def matchesExactly(self, set_of_patterns, item):
        for pattern in set_of_patterns:
            find_pattern = '^' +pattern+ '$'
            if re.match(find_pattern, item): return True
        return False

    def matchesSomewhere(self, set_of_patterns, item):
        for pattern in set_of_patterns:
            find_pattern = '.*' +pattern+ '.*'
            if re.match(find_pattern, item): return True
        return False


###############################################################################
# MonitorField
###############################################################################
class MonitorField():

    def __init__(self):
        self.reset()
        pass

    def reset(self):
        self.first_time = True
        self.prev_fields = dict()
        self.new_fields = dict()
        return None

    def slideFieldValues(self, row):
        if self.first_time:
            self.first_time = False
            self.prev_fields = self.new_fields = row
            return None
        else:
            self.prev_fields = self.new_fields
            self.new_fields = row
            return None
 
    def fieldHasChanged(self, list_of_fields):
        for field in list_of_fields:
            if field in self.prev_fields.keys():
                if (self.prev_fields[field] != self.new_fields[field]):
                    return True
        return False


###############################################################################
# RunningTotals
###############################################################################
class RunningTotals():

    # static
    monitor = MonitorField()
               
    # public
    def __init__(self, beginning_balance = 0.0):
        self.count_records = 0
        self.sub_total = beginning_balance     
        self.sub_credit = 0
        self.sub_debit = 0
        pass

    # public
    def accumulate(self, amount, list_of_fields, decrease_credit_increase_debit=False):
        field_has_changed = self.monitor.fieldHasChanged(list_of_fields)
        self.accumulateTotal(amount,  field_has_changed)
        if decrease_credit_increase_debit:
            #print "DBG credit was", self.sub_credit, amount
            #print "DBG debit  was", self.sub_debit, amount
            money = getFloatNoCommas(amount)
            if field_has_changed:
                self.sub_debit = money
            else:
                self.sub_debit += money
            #print "DBG credit  is", self.sub_credit
            #print "DBG debit  is", self.sub_debit
        else:
            self.accumulateCredit(amount, field_has_changed)
            self.accumulateDebit(amount,  field_has_changed)
        return None

    def accumulate(self, amount, list_of_fields):
        field_has_changed = self.monitor.fieldHasChanged(list_of_fields)
        self.accumulateTotal(amount,  field_has_changed)
        self.accumulateCredit(amount, field_has_changed)
        self.accumulateDebit(amount,  field_has_changed)
        return None

    # public
    def getNumberTransactions(self):
        return str(self.count_records)

    # public
    def getTotal(self):
        return formatDollars(self.sub_total)

    # publicgetAsPositive
    def getCredit(self):
        return formatDollars(self.sub_credit)

    # public
    def getDebit(self):
        return formatDollars(self.sub_debit)

    # private
    def accumulateTotal(self, amount, field_has_changed):
        if field_has_changed:
            self.sub_total = getFloatNoCommas(amount)
            self.count_records = 1
        else:
            self.sub_total += getFloatNoCommas(amount) 
            self.count_records += 1      
        return None

    # private
    def accumulateCredit(self, amount, field_has_changed):
        money = getFloatNoCommas(amount)
        if field_has_changed:
            if money >= 0.0: self.sub_credit = money
            else:            self.sub_credit = 0.0
        else:
            if money >= 0.0: self.sub_credit += money
        return None

    # private
    def accumulateDebit(self, amount, field_has_changed):
        money = getFloatNoCommas(amount)
        if field_has_changed:
            if money < 0.0: self.sub_debit = money
            else:           self.sub_debit = 0.0
        else:
            if money < 0.0: self.sub_debit += money
        return None

###############################################################################
# Useful functions
###############################################################################

# date style is "11/25/2012"
def convertDateWithSlashes(date):
    mon_day_year = date.split('/')
    split_date = map(int, mon_day_year)
    out = datetime.date(
        split_date[2], split_date[0], split_date[1])
    return str(out)

# date style is "11/25/2012"
def convertDateWithSlashes1(date):
    mon_day_year = date.split('/')
    split_date = map(int, mon_day_year)
    out = datetime.date(
        split_date[2], split_date[0], split_date[1])
    return str(out)

def convertDateToYear(date):
    mon_day_year = date.split('/')
    split_date = map(int, mon_day_year)
    year_mon_day = datetime.date(
        split_date[2], split_date[0], split_date[1])
    return year_mon_day.strftime("%Y")

def convertStandardDateToYear(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%Y")

def convertStandardDateToMonth(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%m")

def convertYearMonthToMonth(date):
    year_mon = date.split('-')
    split_date = map(int, year_mon)
    out = datetime.date(
        split_date[0], split_date[1], 1)
    return out.strftime("%m")

__all__ += ['convertYearMonthToYear']
def convertYearMonthToYear(date):
    year_mon = date.split('-')
    split_date = map(int, year_mon)
    out = datetime.date(
        split_date[0], split_date[1], 1)
    return out.strftime("%Y")

def convertStandardDateToDay(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%d")

def convertStandardDateToYearMonth(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%Y-%m")

def convertStandardDateToYearMonth1(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%b %Y")

def convertStandardDateToMonth(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    out = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return out.strftime("%b")

def convertDateToYearMonth(date):
    mon_day_year = date.split('/')
    split_date = map(int, mon_day_year)
    year_mon_day = datetime.date(
        split_date[2], split_date[0], split_date[1])
    return year_mon_day.strftime("%Y-%m")

def removeDayFromDate(date):
    day_mon_yr = date.split(' ')
    split_date = map(str, day_mon_yr)
    return list([split_date[1], split_date[2]])

def convertToStandardDate(date):
    year_mon_day = date.split('-')
    split_date = map(int, year_mon_day)
    standard = datetime.date(
        split_date[0], split_date[1], split_date[2])
    return standard.strftime("%d %b %Y")

class Colors():
    def __init__(self):
        self.first_time_color = True
        
    def getCyclicColors(self):
        if self.first_time_color:
            self.first_time_color = False
            self.colors = list()
            self.colors.append('#CCFFCC') # green
            self.colors.append('#FEF1B5') # yellow
            self.colors.append('#EED2EE') # purple
            self.colors.append('#DAF4F0') # bluish
            self.colors.append('#FFDAB9') # orange-brown
            self.colors.append('#E6E6FA') # purple-blue
    
            self.colors.append('#CCFFCC') # green
            self.colors.append('#FEF1B5') # yellow
            self.colors.append('#EED2EE') # purple
            self.colors.append('#DAF4F0') # bluish
            self.colors.append('#FFDAB9') # orange-brown
            self.colors.append('#E6E6FA') # purple-blue
            self.colors.append('lightpink')
            self.which_color = len(self.colors)-1
        self.which_color += 1
        self.which_color %= len(self.colors)
        return self.colors[self.which_color]
        
    def getBasedUponTime(self, row):
        time = row['time']
        #print "TIME IS", time
        if   time=='7:00 am'    : color_row = 'lightpink'
        elif time=='8:00 am'    : color_row = '#FEF1B5'
        elif time=='9:00 am'    : color_row = '#FFDAB9'
        elif time=='10:00 am'   : color_row = 'lightbrown'
        elif time=='11:00 am'   : color_row = 'lightyellow'
        elif time=='12:00 noon' : color_row = '#EED2EE'
        elif time=='2:00 pm'    : color_row = 'lightblue'
        elif time=='4:00 pm'    : color_row = '#DAF4F0'
        elif time=='5:00 pm'    : color_row = '#E6E6FA'
        elif time=='6:00 pm'    : color_row = '#FFF4FF'
        elif time=='7:00 pm'    : color_row = 'SeaShell'
        elif time=='8:00 pm'    : color_row = '#CCFFCC'
        elif time=='9:00 pm'    : color_row = 'Wheat'
        elif time=='10:00 pm'   : color_row = '#BFEFFF'
        elif time=='as needed'  : color_row = 'lightgrey'
        else:
            print "Color not found for this time:", time
            color_row = 'red'
        return color_row

    def getBasedUponDay(self, row):
        day = row['day']
        if   day=='Sunday'         : color_row = 'lightpink'
        elif day=='Monday'         : color_row = '#FEF1B5'
        elif day=='Tuesday'        : color_row = '#DAF4F0'
        elif day=='Wednesday'      : color_row = '#FFDAB9'
        elif day=='Thursday'       : color_row = '#EED2EE'
        elif day=='Friday'         : color_row = '#CCFFCC'
        elif day=='Saturday'       : color_row = '#E6E6FA'
        elif day=='as needed'      : color_row = 'lightgrey'
        else                       : color_row = 'red'
        return color_row

def getNegativeAmounts(amount_text):
    out = re.sub('\)$','', amount_text)
    out = re.sub('^\(','-', out)
    return out

def getAsPositive(amount_text):
    #out = re.sub('\)$','', amount_text) # convert (amount_text) to amount_text
    #out = re.sub('^\(','', out)
    out = re.sub('[\(\)-]','', amount_text)
    return out

def getFloat(amount_text):
    out = re.sub('\)$','', amount_text)
    out = re.sub('^\(','-', out)
    out = re.sub(',','', out)
    return float(out)

def getFloatNoCommas(amount_text):
    if amount_text == '&nbsp;' or amount_text == '':
        return float(0.0)
    out = re.sub('\)$','', amount_text) # convert (amount_text) to -amount_text
    out = re.sub('^\(','-', out)
    out = re.sub(',','', out)           # remove commas
    return float(out)

def formatDollars(amount):
    return "{:,.2f}".format(amount)

#===============================================================================
# In order of date, accumulate month subtotals and year totals.
# At the end of every year, execute this function to compute monthly average.
# The first month is a partial month so the monthly average for the first year
# will be incorrect. It is best then to ignore completely the partial first
# month in the database.
#===============================================================================
def avePerMonth(total_year_text, total_month_text='', year_month='', master_first_row=dict(), master_last_row=dict()):
    year = convertYearMonthToYear(year_month)
    first_year = final_month = ' '
    if 'Date' in master_first_row.keys():
        first_date = master_first_row['Date']
        first_month = convertStandardDateToYearMonth(first_date)
        first_year = convertStandardDateToYear(first_date)
    if 'Date' in master_last_row.keys():
        final_date = master_last_row['Date']
        final_month = convertStandardDateToYearMonth(final_date)
        #print "final date is",final_date, final_month
    if year == first_year:
        month = convertYearMonthToMonth(first_month)
        number_months = (12.0-float(month))
        total_year = getFloatNoCommas(total_year_text)
        print "first year is", first_year, number_months
    elif year_month == final_month:
        month = convertYearMonthToMonth(final_month)
        number_months = (float(month)-1.0)
        total_year = getFloatNoCommas(total_year_text)
        total_month = getFloatNoCommas(total_month_text)
        total_year -= total_month
    else:
        number_months = 12.0
        total_year = getFloatNoCommas(total_year_text)
    ave_per_month = total_year/number_months
    return formatDollars(ave_per_month)

def avePerMonth(total_year_text, total_month_text='', year_month='', master_first_row=dict(), master_last_row=dict()):
    number_months = 12.0
    total_year = getFloatNoCommas(total_year_text)
    ave_per_month = total_year/number_months
    return formatDollars(ave_per_month)


def getPaypalAdjusted(amount_text, is_usa_payment=True):
    if is_usa_payment:
        # 2.9% plus $0.30
        rate = 0.029
        offset = 0.3
    else:
        # 3.9% plus $0.30
        rate = 0.039
        offset = 0.3
    net = getFloatNoCommas(amount_text)
    orig = (net+offset)/(1-rate)
    return formatDollars(orig)


