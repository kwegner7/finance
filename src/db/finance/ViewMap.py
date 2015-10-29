'''
    Generate and Import DB Maps
'''
#===============================================================================
# determine the module path
#===============================================================================
import abc, re
from db.Db import Abstract, View

__all__ = list()

#===============================================================================
#  Must implement these methods in addition to abstract methods required by
#  View, Transformer, and View
#===============================================================================
class MapGenerateAbstract(Abstract):
    
    @abc.abstractmethod
    def rowContainsKey(self, row): pass

#===============================================================================
# MapGenerate (abstract)
#===============================================================================
class MapGenerate(View, MapGenerateAbstract):
                    
    # implementations of required abstract methods             
    def initializeTransform(self):        
        return

    def subsectionChange(self):
        return list([])

    def sectionChange(self):
        return list([])

    def collapseOnFields(self): return list([])

#===============================================================================
# GenerateMapBillPay (may be instantiated)
#    This is a View Db of a Master Db which contains downloads from the
#    ML Website for Beyond Banking records. 
#
#    In the AccountAlias field search for 0088dddd anywhere.
#    Produces a new csv file with columns:
#           BillPayId        AccountAlias
#            00880303    YEKOPE MINISTRIE00880303
#
#===============================================================================
__all__ += ['GenerateMapBillPay']
class GenerateMapBillPay(MapGenerate):
    
    # the map csv file has these columns     
    def fieldNames(self): return list([
        "BillPayId",
        "AccountAlias",
        "Date",
        "Amount",
        ])

    # when the csv file was downloaded from the ML website
    # here is how to find the key     
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

    def collapseOnFields(self):
        return list([ 'BillPayId' ])
        
    # extract the rows from the ML database that contain the key
    def isSelectedRow(self, row):
        return (
            len(row['BillPayId']) > 0
            and not re.match('^' + 'PAYEE UNRECORDE' + '.*$', row['AccountAlias'])
        )

    # generate the columns: key, field
    def transform(self, row_in, next_row):
        row_out = dict()

        row_out["AccountAlias"] = row_in["AccountAlias"]
        row_out["Date"] = row_in["Date"]
        row_out["Amount"] = row_in["Amount"]
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
#    This is a View Db of a Master Db which contains downloads from the
#    ML Website for Beyond Banking records. 
#===============================================================================
__all__ += ['GenerateMapCheckNumber']
class GenerateMapCheckNumber(MapGenerate):

    # the map csv file has these columns     
    def fieldNames(self): return list([
        "CheckNumber",
        "AccountAlias",
        "Date",
        "Amount",
        ])
        
    # when the csv file was downloaded from the ML website
    # here is how to find the key     
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
        
    # extract the rows from the ML database that contain the key
    def isSelectedRow(self, row):
        return len(row['CheckNumber']) > 0

    # generate the columns: key, field
    def transform(self, row_in, next_row):
        row_out = dict()
        
        row_out["AccountAlias"] = row_in["AccountAlias"]
        row_out["Date"] = row_in["Date"]
        row_out["Amount"] = row_in["Amount"]
        row_contains_key, key = self.rowContainsKey(row_in)            
        if row_contains_key:
            row_out['CheckNumber'] = key
        else:
            row_out['CheckNumber'] = str('')

        return True, row_out

    def htmlPresentation(self, dirpath):
        HtmlModern(self, dirpath)
        return
