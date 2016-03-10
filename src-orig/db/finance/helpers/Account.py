'''
    Account
'''

import re, copy
from helper import Container

#===========================================================================
# static method: simplify the alias by removing blanks and numbers
#===========================================================================
def simplifyAlias(alias):
    
    # These words do not help to distinguish account alias
    remove_ambiguity1 = re.sub('Pre Authdebit','', alias)
    remove_ambiguity2 = re.sub('Visa Deferred','', remove_ambiguity1)
    
    # create the simplified alias
    simplified = Container.String(remove_ambiguity2).removeBlanksAndNumbers().upper()
    return simplified

#===============================================================================
# Account
#===============================================================================
class Account():

    #===========================================================================
    # constructor
    #===========================================================================
    def __init__(self, title, category, subcategory):
        self.title = Container.String(title).whiteSpaceToBlank()
        self.category = Container.String(category).whiteSpaceToBlank()
        self.subcategory = Container.String(subcategory).whiteSpaceToBlank()
        self.aliases = set()
        return None
  
    #===========================================================================
    # add to the set of aliases
    #===========================================================================
    def addAliasAsSimplified(self, alias):
        simplified = simplifyAlias(alias)
        self.aliases.add(simplified)
        return simplified
                      
    #===========================================================================
    # print this object
    #===========================================================================
    def text(self):
        #print "      Title:", self.title,
        #print "   Category:", self.category,
        #print "Subcategory:", self.subcategory
        print "Account", self.title, "has", len(self.aliases), "aliases"
        #if len(self.aliases) > 0:
        #    for alias in self.aliases:
        #        print "    Alias:", alias
        return None
   
