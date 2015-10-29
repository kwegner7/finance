'''
    Build This is not a subclass of Db rather a helper to build a Model Db
'''

__all__ = list()

#===============================================================================
# imports
#===============================================================================
import os
from db.Db import Db
from db.finance.Original import *
from db.finance.Essence import *
from db.finance.Model import *

#===============================================================================
# BuildModel (may be instantiated)
#===============================================================================
__all__ += ['BuildModel']
class BuildModel(ModelFinance):
                
    # constructor
    def __init__(self, list_of_origs):
        self.list_of_origs = list_of_origs
        self.model = ModelFinance(self.combineOriginals())
        return
        
    def combineOriginals(self):
        first_time = True
        for orig in self.list_of_origs:
            if first_time:
                first_time = False
                combine = orig
                print "Begin Combining:", orig
            else:
                print "Next Orig", orig
                if isinstance(orig, OrigFinance):
                    combine.append(orig)
                else:
                    #essence = EssenceMint(orig, self.text)          
                    combine.append(orig)
        return combine
                              