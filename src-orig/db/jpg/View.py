'''
    View Db
'''
#===============================================================================
# imports
#===============================================================================
import os
from abc import abstractmethod
from helper import Container

from db.Db import Db, View
from db.finance.Model import ModelFinance

from html.finance.HtmlTableFinance import *

__all__ = list()

#===============================================================================
# ViewGeneric (may be instantiated)
#===============================================================================        
class ViewGeneric(View):
                
    # constructor
    def __init__(self, obj):
        self.master_fields = obj.fieldNames()
        View.__init__(self, obj)

    # implementations of abstract methods     
    def fieldNames(self):
        return list([ 'Count' ]) + self.master_fields
        
    def isSelectedRow(self, row):
        return True

    def initializeTransform(self):
        self.count_running = 0
    
    def transform(self, master_col, next_col):
        self.count_running = self.count_running+1
        subset_col = dict(master_col)
        subset_col['Count'] = self.count_running
        return True, subset_col

    def sortBeforeTransform(self): return list()

    def sortAfterTransform(self): return list()

    def collapseOnFields(self): return list()

    def subsectionChange(self): return list()

    def sectionChange(self): return list()

    def htmlPresentation(self, dirpath):
        HtmlGeneric(self, dirpath)
        return
                                                                           

