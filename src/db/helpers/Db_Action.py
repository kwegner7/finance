'''
    Db.Accounts
'''

from db.Db import Db

#===============================================================================
# Db_Accounts
#===============================================================================
class Db_Action(Db):

    def __init__(self, filename, fieldnames, dialect, skip_first_record):
        Db.__init__(self, filename, fieldnames, dialect, skip_first_record)
        self.forEachRow(self)
        #print "Performing Action", filename  
                    
    def forEachRow(self, csv_in):
        csv_in.openRead();
        for row in csv_in.reader:
            self.performAction(row)
        csv_in.closeRead();
        return None                                  