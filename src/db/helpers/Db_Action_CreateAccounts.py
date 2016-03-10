'''
    Db.Action.CreateAccounts
'''

from db import CsvObject
from db.helpers.Db_Action import Db_Action

#===============================================================================
# Db_Action_CreateAccounts
#===============================================================================
class Db_Action_CreateAccounts(Db_Action):

    def __init__(self, action, csv_file):
        self.action = action

        Db_Action.__init__(self,
            csv_file,
            self.actionFields(),
            self.dialect(),
            self.skipFirstRecord())
            
        
    #===========================================================================
    # configuration items
    #===========================================================================
    def actionFields(self): return list([
        "Alias",
        "AccountText",
        "Category",
        "SubCategory",
    ])

    def dialect(self):
        return CsvObject.CsvBackquoteDialect()

    def skipFirstRecord(self):
        return False
                                                
    def performAction(self, row): 
        #print row['AccountText'], row['Alias'], row['Category'], row['SubCategory']
        self.action(row['AccountText'], row['Alias'], row['Category'], row['SubCategory'])
 