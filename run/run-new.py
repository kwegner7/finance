'''
    Obtain Joint BB downloads for the year 2015 (Mar 10 and prev 2 yrs)
        I want to download account data - All Downloadable Activity
        /home/orig/kurt/Documents/institutions/original/ml-jointbb/downloaded2016-03-10    
    
    Obtain Beyond Banking downloads for the year 2015 (Mar 10 and prev 2 yrs)
        /home/orig/kurt/Documents/institutions/original/ml-beyondbanking/downloaded2016-03-10        
    
    Obtain Capital One Mint downloads for the year 2015
        open Mint - select Capital One - Download all transactions
        /home/orig/kurt/Documents/institutions/original/mint-capital-one/downloaded2016-03-10 
   
    Obtain Chase Mint downloads for the year 2015    
        /home/orig/kurt/Documents/institutions/original/mint-chase/downloaded2016-03-10    
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
    from MasterControlFinance import *    
    
    mc = MasterControlFinance()
    mc.process()
    
if __name__ == '__mainn__':


    folder_beyond_banking = \
    "/home/orig/kurt/Documents/institutions/original/ml-beyondbanking/downloaded2016-03-10" 
       
    folder_beyond_banking_was = \
    "/home/orig/kurt/Documents/institutions/original/ml-beyondbanking/downloaded2015-10-11"   
     
    folder_joint_beyond_banking = \
    "/home/orig/kurt/Documents/institutions/original/ml-jointbb/downloaded2016-03-10"        

    mint_capital_one = \
    "/home/orig/kurt/Documents/institutions/original/mint-capital-one/downloaded2016-03-10/transactions.csv"        

    mint_chase = \
    "/home/orig/kurt/Documents/institutions/original/mint-chase/downloaded2016-03-10/transactions.csv"        
            
    #===========================================================================
    # Append all csv files in a folder to produce LATEST_ML_SORTED.csv
    #===========================================================================
    print "------------------------------------------------------------------"
    print "Runtime path to the in and out folders is", os.getcwd()
    print "Module path is:"
    for folder in sys.path:
        print "   ", folder
    print "------------------------------------------------------------------"

    first_time = True        
    for directory, subdirectories, files in os.walk(folder_beyond_banking):
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

    for directory, subdirectories, files in os.walk(folder_joint_beyond_banking):
        for file in files:
            csv = os.path.join(directory, file)
            print "    Combining another joint file:", csv

            # convert original BB to original Finance
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
    
    orig = Finance.OrigMint(mint_capital_one, Db.CsvFormatStandard)   
    essence.append(Finance.Essence(orig)) 
             
    orig = Finance.OrigMint(mint_chase, Db.CsvFormatStandard)   
    essence.append(Finance.Essence(orig)) 

    model = Finance.Model(essence)

    # obtain views of the model 
    
    # month           
    view = Finance.ViewMonth(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/MonthDetails.html')

    # month        
    view = Finance.ViewMonthSummary(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/MonthSummary.html')
    
    # category          
    view = Finance.ViewCategory(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/CategoryDetails.html')
    
    # category          
    view = Finance.ViewCategorySummary(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/CategorySummary.html')

    # subcategory            
    view = Finance.ViewSubCategory(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/SubCategoryDetails.html')
    
    # subcategory          
    view = Finance.ViewSubCategorySummary(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/SubCategorySummary.html')
 
    # accounts            
    view = Finance.ViewAccounts(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/AccountsDetails.html')

    # accounts            
    view = Finance.ViewAccountsSummary(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/AccountsSummary.html')

    # accounts            
    view = Finance.ViewStudy(model)
    html = view.pages(os.getcwd()+'/out/publish')
    os.rename(
        os.getcwd()+'/out/publish/out.html',
        os.getcwd()+'/out/publish/Study.html')
 
exit()
