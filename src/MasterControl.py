'''
    MasterControl - mutate csv files and create html reports
'''

import sys, os
from abc import abstractmethod

__all__ = list()

#===============================================================================
# search path for source files begins here
#===============================================================================
src_base = '.'
sys.path[0] = src_base

#===============================================================================
# chdir to the run path (os.getcwd) containing run.py and the in, out folders
#===============================================================================
run_path = '../run'
os.chdir(run_path)

#===============================================================================
# MasterControl (abstract)
#===============================================================================
class MasterControl(object):

    @abstractmethod
    def originalToEssence(self, orig): pass

    @abstractmethod
    def essenceToModel(self, essence): pass

    @abstractmethod
    def collectOriginals(self): pass
    
    @abstractmethod
    def createViewsOfTheModel(self, model): pass

    # constructor
    def __init__(self):
        object.__init__(self)

    # common
    def essenceOfOriginals(self, originals):
        first_time = True        
        for orig in originals:
            if first_time:
                first_time = False        
                essence = self.originalToEssence(orig)
            else:
                next = self.originalToEssence(orig)          
                essence.append(next)
        return essence
    
    # common
    def csvToHtml(self, view, filename):
        html = view.htmlPresentation(os.getcwd()+'/out/publish/' + filename)
        return
    
    # process database     
    def process(self):
        originals = self.collectOriginals()   
        essence = self.essenceOfOriginals(originals)
        model = self.essenceToModel(essence)
        views = self.createViewsOfTheModel(model)
        for view in views:
            htmlfilename = view.__class__.__name__+'.html'
            self.csvToHtml(view, htmlfilename)
        return

