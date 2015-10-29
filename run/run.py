'''
    This script performs
'''

#===============================================================================
# This determines the os.getcwd containing the .../in .../out .../check
# And the module paths for all python imports
#===============================================================================
import sys, os
src_base = '../src'
run_path = '.'
sys.path[0] = src_base
os.chdir(run_path)

#===============================================================================
# imports relative to /proj/finance/python
#===============================================================================
from db.Db import Db, Original
from db.finance.Original import OrigBeyondBanking, OrigFinance, OrigMint
from db.finance.Essence import EssenceBeyondBankingSorted, EssenceFinance, EssenceFinanceSorted
from db.finance.Build import BuildModel
from db.finance.View import *
from db.finance.ViewMap import *

#===============================================================================
# main
#===============================================================================
if __name__ == '__main__':

    print "------------------------------------------------------------------"
    print "Runtime path to in, out, check folders is", os.getcwd()
    print "Module path is:"
    for folder in sys.path:
        print "   ", folder
    print "------------------------------------------------------------------"
    
    #===========================================================================
    # collection
    #===========================================================================
    collection = True
    if collection:

        #===========================================================================
        # This is a sorted version of all collected ML BB downloads
        #    2010-09-30 --> 2015-08-20
        # So I manually editted ALLBB_Sorted.csv to become ALLBB_Previous.csv
        #    remove "PAYEE UNRECORDE" and sort -ui (ignore multiple blanks)
        #    cat ALLBB_Previous.csv |tr --squeeze-repeats ' ' | sort -u > 2010-09-30to2013-10-10.csv
        #    tr --squeeze-repeats ' ' 
        #    2010-09-30 --> 2013-10-10
        #===========================================================================
        if True:
            print "Generating ALL_BB_Sorted"
            orig = OrigBeyondBanking(os.getcwd()+'/in/BeyondBanking/ALLBB.csv', Db.CsvFormatStandard)   
            all_bb = EssenceBeyondBankingSorted(orig)          
            all_bb.export(os.getcwd()+'/in/BeyondBanking/ALLBB_Sorted.csv')      
        
        #===========================================================================
        # These are the latest 2 year downloads of ML BB
        #    2013-10-11 --> 2015-10-06
        #===========================================================================
        if True:
            import os
            latest_bb_downloads = "/home/kurt/Documents/institutions/original/ml-beyondbanking/downloaded2015-10-11"        
            first_time = True        
            for directory, subdirectories, files in os.walk(latest_bb_downloads):
                for file in files:
                    csv = os.path.join(directory, file)
                    print "    Combining another file:", csv
                    if first_time:
                        first_time = False        
                        orig = OrigBeyondBanking(csv, Db.CsvFormatStandard)   
                        bb   = EssenceFinance(orig)          
                    else:
                        orig = OrigBeyondBanking(csv, Db.CsvFormatStandard)   
                        next = EssenceFinance(orig)          
                        bb.append(next)
            bb.export(os.getcwd()+'/in/BeyondBanking/LATEST_ML.csv') 
            orig = OrigFinance(os.getcwd()+'/in/BeyondBanking/LATEST_ML.csv')   
            latest = EssenceFinanceSorted(orig)          
            latest.export(os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv') 

        #===========================================================================
        # At this point we have:
        #    .../in/BeyondBanking/LATEST_ML_SORTED.csv sorted OrigFinance
        #    .../in/BeyondBanking/2010-09-30to2013-10-10.csv sorted OrigFinance
        #===========================================================================
        
        #===========================================================================
        # Now add the Mint download of all Capital One Credit Card
        # and add the Mint download of all Chase Credit Card
        #===========================================================================
        print "\nThe Master Database is expecting certain Essence columns"
        print "\nConvert each input database to consist of these Essence columns"

        if False:
            print "\n    obtaining older Beyond Banking from ML Website"
            combine = OrigFinance(os.getcwd()+'/in/BeyondBanking/2010-09-30to2013-10-10.csv') 
            #combine.append(essence)
    
            print "\n    obtaining latest two years Beyond Banking from ML Website"
            essence = OrigFinance(os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv') 
            combine.append(essence)
      
            print "\n    obtaining Mint Capital One Credit Card"
            csv = '/home/kurt/Documents/institutions/original/mint-capital-one/download2015-10-13.csv'
            orig    = OrigMint(csv, Db.CsvFormatStandard)   
            essence  = EssenceMint(orig, 'Mint Capital One')          
            combine.append(essence)
            
            print "\n    obtaining Mint Chase Credit Card"
            csv = '/home/kurt/Documents/institutions/original/mint-chase/download2015-10-13.csv'
            orig    = OrigMint(csv, Db.CsvFormatStandard)   
            essence = EssenceMint(orig, 'Mint Chase')                  
            combine.append(essence)
            
            print "\nCombine all of these into a single Essence expected by Master"
            print "\nThe Master transforms horizontally to derived useful columns from the Essence"
            model  = ModelFinance(combine) 
            
        else:
            csv1 = os.getcwd()+'/in/BeyondBanking/2010-09-30to2013-10-10.csv'
            csv2 = os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv'
            csv3 = '/home/kurt/Documents/institutions/original/mint-capital-one/download2015-10-13.csv'
            csv4 = '/home/kurt/Documents/institutions/original/mint-chase/download2015-10-13.csv'
            model = BuildModel( list([
                EssenceFinance(OrigFinance(csv1)),
                EssenceFinance(OrigFinance(csv2)),
                EssenceFinance(OrigMint(csv3, Db.CsvFormatStandard),'Mint Capital One'),
                EssenceFinance(OrigMint(csv4, Db.CsvFormatStandard),'Mint Chase')   
            ])).model

        #===========================================================================
        # Views
        #===========================================================================
        print "\nA View Sorts and Transforms Vertically From the Master - All transactions in order of date"
        subset  = ViewMonth(model)         
        html = subset.pages(os.getcwd()+'/out/html/Month')
        subset  = ViewMonthSummary(model)         
        html = subset.pages(os.getcwd()+'/publish')
        os.rename(
            os.getcwd()+'/publish/out.html',
            os.getcwd()+'/publish/MonthSummary.html')
        subset  = ViewSubCategory(model)         
        html = subset.pages(os.getcwd()+'/out/html/Subcategory')
        subset  = ViewSubCategorySummary(model)         
        html = subset.pages(os.getcwd()+'/out/html/SubcategorySummary')
        
        #=======================================================================
        # practice maps
        #======================================================================= 
        print "\nCreate two Maps"
        subset  = GenerateMapBillPay(model)
        subset.export(os.getcwd()+'/out/maps/billpay.csv')         
        subset  = GenerateMapCheckNumber(model)
        subset.export(os.getcwd()+'/out/maps/checknumber.csv')         

        #=======================================================================
        # practice better design - all BB from ML in the past
        #======================================================================= 
        if True:
            from db.Db import Db
            from db.finance import Finance
            csv = os.getcwd()+'/in/BeyondBanking/ALLBB.csv'

            # collect originals             
            orig = Finance.OrigBeyondBanking(csv, Db.CsvFormatStandard)

            # generate the model             
            essence = Finance.Essence(orig) 
            model = Finance.Model(essence)

            # obtain views of the model            
            view = Finance.ViewMonth(model)
            html = view.pages(os.getcwd()+'/out/html/BetterDesign1')

        #=======================================================================
        # practice better design - prev 2 yrs ML, mint older, capital one, chase
        #======================================================================= 
        if True:
            csv = os.getcwd()+'/in/BeyondBanking/LATEST_ML_SORTED.csv'
            orig = Finance.OrigEssence(csv)   
            essence = Finance.Essence(orig) 
            
            csv = os.getcwd()+'/in/BeyondBanking/2010-09-30to2013-10-10.csv'
            orig = Finance.OrigEssence(csv)   
            essence.append(Finance.Essence(orig)) 
            
            csv = '/home/kurt/Documents/institutions/original/mint-capital-one/download2015-10-13.csv'
            orig = Finance.OrigMint(csv, Db.CsvFormatStandard)   
            essence.append(Finance.Essence(orig)) 
                     
            csv = '/home/kurt/Documents/institutions/original/mint-chase/download2015-10-13.csv'
            orig = Finance.OrigMint(csv, Db.CsvFormatStandard)   
            essence.append(Finance.Essence(orig)) 

            model = Finance.Model(essence)

            # obtain views of the model            
            view = Finance.ViewMonth(model)
            html = view.pages(os.getcwd()+'/publish')
            os.rename(
                os.getcwd()+'/publish/out.html',
                os.getcwd()+'/publish/MonthDetails.html')
            
        
        exit()
