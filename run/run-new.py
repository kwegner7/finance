'''
    This script reads one year + one month
    of Beyond Banking and htmls several reports
'''

#===============================================================================
# This determines the run path (os.getcwd) containing the in and out folders
# And the module paths for all python imports
#===============================================================================
import sys, os
src_base = '../src'
run_path = '.'
sys.path[0] = src_base
os.chdir(run_path)

#===============================================================================
# imports are relative to the src folder
#===============================================================================
from db.Db import Db
from db.finance import Finance, Original, Essence

#===============================================================================
# main
#===============================================================================
if __name__ == '__main__':

    print "------------------------------------------------------------------"
    print "Runtime path to the in and out folders is", os.getcwd()
    print "Module path is:"
    for folder in sys.path:
        print "   ", folder
    print "------------------------------------------------------------------"
            
    #===========================================================================
    # Append all csv files in a folder to produce LATEST_ML_SORTED.csv
    #===========================================================================
    latest_bb_downloads = "/home/orig/kurt/Documents/institutions/original/ml-beyondbanking/downloaded2015-10-11"        
    first_time = True        
    for directory, subdirectories, files in os.walk(latest_bb_downloads):
        for file in files:
            csv = os.path.join(directory, file)
            print "    Combining another file:", csv

            # convert original BB to original Finance
            if first_time:
                first_time = False        
                orig = Original.OrigBeyondBanking(csv, Db.CsvFormatStandard)   
                bb   = Essence.EssenceFinance(orig)          
            else:
                orig = Original.OrigBeyondBanking(csv, Db.CsvFormatStandard)   
                next = Essence.EssenceFinance(orig)          
                bb.append(next)
    bb.export(os.getcwd()+'/in/BeyondBanking/LATEST_ML.csv') 

    # Convert original Finance to sorted original Finance
    orig = Original.OrigFinance(os.getcwd()+'/in/BeyondBanking/LATEST_ML.csv')   
    latest = Essence.EssenceFinanceSorted(orig)          
    latest.export(os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv') 
        
    #=======================================================================
    # practice better design - prev 2 yrs ML, mint older, capital one, chase
    #======================================================================= 

    # horizontal add columns
    csv = os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv'
    orig = Finance.OrigEssence(csv)   
    essence = Finance.Essence(orig) 
    
    csv = '/home/orig/kurt/Documents/institutions/original/mint-capital-one/download2015-10-13.csv'
    orig = Finance.OrigMint(csv, Db.CsvFormatStandard)   
    essence.append(Finance.Essence(orig)) 
             
    csv = '/home/orig/kurt/Documents/institutions/original/mint-chase/download2015-10-13.csv'
    orig = Finance.OrigMint(csv, Db.CsvFormatStandard)   
    essence.append(Finance.Essence(orig)) 

    model = Finance.Model(essence)

    # obtain views of the model            
    view = Finance.ViewMonth(model)
    html = view.pages(os.getcwd()+'/../publish')
    os.rename(
        os.getcwd()+'/../publish/out.html',
        os.getcwd()+'/../publish/MonthDetails.html')

    # obtain views of the model            
    view = Finance.ViewMonthSummary(model)
    html = view.pages(os.getcwd()+'/../publish')
    os.rename(
        os.getcwd()+'/../publish/out.html',
        os.getcwd()+'/../publish/MonthSummary.html')

    # obtain views of the model            
    view = Finance.ViewSubCategory(model)
    html = view.pages(os.getcwd()+'/../publish')
    os.rename(
        os.getcwd()+'/../publish/out.html',
        os.getcwd()+'/../publish/SubCategoryDetails.html')

    # obtain views of the model            
    view = Finance.ViewSubCategorySummary(model)
    html = view.pages(os.getcwd()+'/../publish')
    os.rename(
        os.getcwd()+'/../publish/out.html',
        os.getcwd()+'/../publish/SubCategorySummary.html')
 
exit()
