'''
    Db.Accounts
'''

import re
from helper import Container
from db.helpers.Db_Action_CreateAccounts import Db_Action_CreateAccounts
import Account

'''
#===========================================================================
# This is an Account object
#===========================================================================
def __init__(self, title, category, subcategory):
    self.title = Container.String(title).whiteSpaceToBlank()
    self.category = Container.String(category).whiteSpaceToBlank()
    self.subcategory = Container.String(subcategory).whiteSpaceToBlank()
    self.aliases = set()
    return None
'''

#===============================================================================
# Db_Accounts
#===============================================================================
class Db_Accounts():

    def __init__(self, csv_all_accounts):
        # the action "createAccount" is performed on every row of the file Accounts_All.csv
        # createAccount(row['AccountText'], row['Alias'], row['Category'], row['SubCategory'])
        self.map_title_to_account = dict()
        self.map_alias_to_title = dict()
        action = Db_Action_CreateAccounts(self.createAccount, csv_all_accounts)

    def truncateKey(self, simplified):
        return simplified[0:4]
        
    '''
        FIX THIS: check that the alias does not exist before adding
        Reading from a csv file, records are:
           simplified alias, account title, category and subcategory
    '''
    def createAccount(self, title_in, alias_in, category_in, subcategory_in):

        # obtain 3 of the 4 fields of the row within the all accounts file
        title = Container.String(title_in).whiteSpaceToBlank()
        category = Container.String(category_in).whiteSpaceToBlank()
        subcategory = Container.String(subcategory_in).whiteSpaceToBlank()
        
        # an account title may appear multiple times because of multiple aliases
        # see if this is the first occurence of this account title in the csv file
        if not title in self.map_title_to_account.keys():
            # if this is the first time that this title appears, 
            #     add this new account to the map
            account = Account.Account(title, category, subcategory)
            self.map_title_to_account[title] = account
        else:
            # if the account title is already in the map, obtain the account data
            account = self.map_title_to_account[title] 
        # and add this new alias to the set of aliases for this account                  
        simplified = account.addAliasAsSimplified(alias_in)
        # also add this new alias to the map from simplified alias to title of account
        self.map_alias_to_title[simplified] = title
        return None 

    def getKey(self, full_alias):
        simplified = Account.simplifyAlias(full_alias)
        for key in self.map_alias_to_title.keys():                
            if (simplified.find(key) == 0):
                return key
        return 'KEYNOTFOUND'
   
    def getCategory(self, account_title):
        if account_title in self.map_title_to_account.keys():
            return self.map_title_to_account[account_title].category
        else:
            return "UNKNOWN_CATEGORY"
   
    def getSubcategory(self, account_title):
        if account_title in self.map_title_to_account.keys():
            return self.map_title_to_account[account_title].subcategory
        else:
            return "UNKNOWN_SUBCATEGORY"

    # In the file Accouts_All.csv it may be that a key appears in the
    # simplified string by coincidence. Make the simplified string into
    # a row of the table so that this method will select the exact match.
    def getAccountTitle(self, alias):
        simplified = Account.simplifyAlias(alias)
              
        # if the alias when simplified is exactly a key to the map
        # then return the title of the account        
        if simplified in self.map_alias_to_title.keys():
            #print "matches exactly", simplified
            return self.map_alias_to_title[simplified]

        # check to see if key appears at the beginning of simplified
        for key in self.map_alias_to_title.keys():                
            if simplified.find(key) == 0:
                #print "The key,", key, "matches at the beginning of", simplified
                return self.map_alias_to_title[key]
                
        # check to see if key appears somewhere in simplified
        for key in self.map_alias_to_title.keys():                
            if simplified.find(key) > 0:
                #print "The key,", key, "matches somewhere the simplified alias", simplified
                return self.map_alias_to_title[key]
        
        #print "The simplified alias does not match any key:", simplified
        return "UNKNOWN_ACCOUNT"

        # if the alias when simplified is a key to the map
        # then return title        
        if simplified in self.map_alias_to_title.keys():
            return self.map_alias_to_title[simplified]

        # if a key to the map is a leading substring of the alias when simplified 
        # then return title        
        else:
            found = None
            for key in self.map_alias_to_title.keys():
                len_key = len(key)
                if simplified[0:len_key] == key:
                    found = key
                    break
                
        if found == None:
            return "UNKNOWN_ACCOUNT"
        else:
            return self.map_alias_to_title[found]

                           