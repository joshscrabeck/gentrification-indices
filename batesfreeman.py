"""
Calculating the Bates (2013) gentrification indices and the Freeman (2005) gentrification index
"""
#%%
import pandas as pd
import os
from math import sqrt
import numpy as np
import cpi
import geopandas as gpd

os.chdir('/Users/winncostantini/gus8066/gentrification-indices')

bates_df = gpd.read_file('bates-freeman-data/bates_df_shp.shp')

#%%

###DEFINE MOE FUNCTIONS###

def moe_perc(den, num_e, den_e, prop):
    '''This function calculates the margin of error for a single derived proportion'''
    sqrt_a = (num_e**2)
    sqrt_b = ((prop**2) * (den_e)**2)
    sqrt_pos = sqrt_a - sqrt_b
    sqrt_neg = sqrt_a + sqrt_b

    moe = np.where(sqrt_a > sqrt_b, (1/den) * (np.sqrt(sqrt_pos)), (1/den) * (np.sqrt(sqrt_neg)) )
    
    return moe.item()


def moe_alltracts(df, col):
    ''' This function calculates the margin of error for the summed value of a column (in this case, the aggregated value across all census tracts)'''
    
    x = df[col]**2
    
    moe = sqrt(x.sum())
    
    return moe

def moe_propagation(moe1, moe2):
    
    moe = sqrt((moe1**2) + (moe2**2))
    
    return moe

#%%
###CREATE DERIVED COLUMNS AND VALUES NEEDED FOR INDICES###

def calc_batesfreeman(df, yr1, yr2, renter1, owner1, popten1, renter2, owner2, popten2, white1, poprac1, white2, poprac2, ASdegm1, ASdegf1, BAdegm1, BAdegf1, MAdegm1, MAdegf1, prodegm1, prodegf1, drdegm1, drdegf1, popedu1, ASdegm2, ASdegf2, BAdegm2, BAdegf2, MAdegm2, MAdegf2, prodegm2, prodegf2, drdegm2, drdegf2, popedu2, mfi2, mhi1, mhi2, mhv0, mhv1, mhv2, tothous, y10to13, y14topr, inplace = False):
    
    copy_df = df.copy(deep = True)
    ###CREATE DERIVED COLUMNS AND VALUES NEEDED FOR INDICES###

    ##TENURE##

    #create new columns with proportion of renters in each tract for years 1 and 2
    df['renterp1'] = df[renter1]/df[popten1]
    df['ownerp1'] = 1 - df['renterp1']
    df['renterp2'] = df[renter2]/df[popten2]
    df['ownerp2'] = 1 - df['renterp2']

    #calculate the citywide proportion of renters for years 1 and 2
    citywide_renters_1 = df[renter1].sum()
    citywide_tenure_1 = df[popten1].sum()

    citywide_renters_2 = df[renter2].sum()
    citywide_tenure_2 = df[popten2].sum()

    citywide_renter_p_1 = citywide_renters_1/citywide_tenure_1
    citywide_owner_p_1 = 1 - citywide_renter_p_1
    citywide_renter_p_2 = citywide_renters_2/citywide_tenure_2
    citywide_owner_p_2 = 1 - citywide_renter_p_2

    #calculate the citywide moe for the number of renters and total number of households for years 1 and 2
    citywide_owner_e_1 = moe_alltracts(df, owner1)
    citywide_tenure_e_1 = moe_alltracts(df, popten1)

    citywide_renter_e_2 = moe_alltracts(df, renter2)
    citywide_owner_e_2 = moe_alltracts(df, owner2)
    citywide_tenure_e_2 = moe_alltracts(df, popten2)

    #assign variables to calculate moe for citywide proportion of owners for year 1
    den_1 = citywide_tenure_1
    num_e_1 = citywide_owner_e_1
    den_e_1 = citywide_tenure_e_1
    prop_1 = citywide_owner_p_1

    #use moe_perc function for year 1
    citywide_owner_moe_1 = moe_perc(den_1, num_e_1, den_e_1, prop_1)

    #assign variables to calculate moe for citywide proportion of owners and renters for year 2
    den_2 = citywide_tenure_2
    num_e_2 = citywide_owner_e_2
    den_e_2 = citywide_tenure_e_2
    prop_2 = citywide_owner_p_2

    #use moe_perc function for year 2 powners
    citywide_owner_moe_2 = moe_perc(den_2, num_e_2, den_e_2, prop_2)

    den_3 = citywide_tenure_2
    num_e_3 = citywide_renter_e_2
    den_e_3 = citywide_tenure_e_2
    prop_3 = citywide_renter_p_2

    #use moe_perc function for year 2 renters
    citywide_renter_moe_2 = moe_perc(den_3, num_e_3, den_e_3, prop_3)

    #For each tract, calculate change percentage point change of owners from year 1 to year 2
    df['ownerch'] = df['ownerp2'] - df['ownerp1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_owner_change = citywide_owner_p_2 - citywide_owner_p_1

    citywide_owner_change_e = moe_propagation(citywide_owner_moe_1, citywide_owner_moe_2)


    ##RACE AND ETHNICITY##

    #Calculate proportion of POC and white pop for each tract for years 1 and 2
    df['poc1'] = df[poprac1] - df[white1]
    df['pocp1'] = (df['poc1']/df[poprac1])
    df['whitep1'] = 1 - df['pocp1']

    df['poc2'] = df[poprac2] - df[white2]
    df['pocp2'] = (df['poc2']/df[poprac2])
    df['whitep2'] = 1 - df['pocp2']

    #Calculate citywide proportion of people of color for years 1 and 2

    citywide_pop_race_1 = df[poprac1].sum()
    citywide_poc_1 = df['poc1'].sum()
    citywide_poc_p_1 = citywide_poc_1/citywide_pop_race_1
    citywide_white_p_1 = 1 - citywide_poc_p_1 


    citywide_pop_race_2 = df[poprac2].sum()
    citywide_poc_2 = df['poc2'].sum()
    citywide_poc_p_2 = citywide_poc_2/citywide_pop_race_2
    citywide_white_p_2 = 1 - citywide_poc_p_2 

    #calculate the citywide moe for the number of poc and total pop for years 1 and 2
    #citywide_poc_e_1 = moe_alltracts(df, 'poc_1')
    citywide_white_e_1 = moe_alltracts(df, white1)
    citywide_pop_race_e_1 = moe_alltracts(df, poprac1)

    citywide_poc_e_2 = moe_alltracts(df, 'poc2')
    citywide_white_e_2 = moe_alltracts(df, white2)
    citywide_pop_race_e_2 = moe_alltracts(df, poprac2)

    #assign variables to calculate moe for citywide proportion for year 1 for white pop
    den_4 = citywide_pop_race_1
    num_e_4 = citywide_white_e_1
    den_e_4 = citywide_pop_race_e_1
    prop_4 = citywide_white_p_1

    #use moe_perc function for year 1
    citywide_white_moe_1 = moe_perc(den_4, num_e_4, den_e_4, prop_4)

    #assign variables to calculate moe for citywide proportion for year 2 for poc and white pop

    den_5 = citywide_pop_race_2
    num_e_5 = citywide_poc_e_2
    den_e_5 = citywide_pop_race_e_2
    prop_5 = citywide_poc_p_2

    #use moe_perc function for year 2 - poc
    citywide_poc_moe_2 = moe_perc(den_5, num_e_5, den_e_5, prop_5)

    den_6 = citywide_pop_race_2
    num_e_6 = citywide_white_e_2
    den_e_6 = citywide_pop_race_e_2
    prop_6 = citywide_white_p_2

    #use moe_perc function for year 2 - white
    citywide_white_moe_2 = moe_perc(den_6, num_e_6, den_e_6, prop_6)

    #For each tract, calculate change percentage point change from year 1 to year 2
    df['whitech'] = df['whitep2'] - df['whitep1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_white_change = citywide_white_p_2 - citywide_white_p_1

    citywide_white_change_e = moe_propagation(citywide_white_moe_1, citywide_white_moe_2)

    ##EDUCATIONAL ATTAINMENT##

    #Calculate proportion 25+ population with and without a college degree for each tract for years 1 and 2
    df['nocol1'] = (df[popedu1]) - (df[ASdegm1] + df[BAdegm1] + df[MAdegm1] + df[prodegm1] + df[drdegm1]) - (df[ASdegf1] + df[BAdegf1] + df[MAdegf1] + df[prodegf1] + df[drdegf1])

    df['col1'] = df[popedu1] - df['nocol1']

    df['nocolp1'] = df['nocol1'] / df[popedu1]
    df['colp1'] = 1 - df['nocolp1']

    df['nocol2'] = (df[popedu2]) - (df[ASdegm2] + df[BAdegm2] + df[MAdegm2] + df[prodegm2] + df[drdegm2]) - (df[ASdegf2] + df[BAdegf2] + df[MAdegf2] + df[prodegf2] + df[drdegf2])

    df['col2'] = df[popedu2] - df['nocol2']

    df['nocolp2'] = df['nocol2'] / df[popedu2]
    df['colp2'] = 1 - df['nocolp2']

    #Calculate citywide proportion of people without a college degree for years 1 and 2

    citywide_pop_edu_1 = df[popedu1].sum()
    citywide_nocollege_1 = df['nocol1'].sum()
    #citywide_college_1 = citywide_pop_edu_1 - citywide_nocollege_1
    citywide_nocollege_p_1 = citywide_nocollege_1/citywide_pop_edu_1
    citywide_college_p_1 = 1 - citywide_nocollege_p_1

    citywide_pop_edu_2 = df[popedu2].sum()
    citywide_nocollege_2 = df['nocol2'].sum()
    #citywide_college_2 = citywide_pop_edu_2 - citywide_nocollege_2
    citywide_nocollege_p_2 = citywide_nocollege_2/citywide_pop_edu_2
    citywide_college_p_2 = 1 - citywide_nocollege_p_2


    #calculate the citywide moe for the number of people w/o college degrees and total pop for years 1 and 2
    #citywide_nocollege_e_1 = moe_alltracts(df, 'nocollege_1')
    citywide_college_e_1 = moe_alltracts(df, 'col1')
    citywide_pop_edu_e_1 = moe_alltracts(df, popedu1)

    citywide_nocollege_e_2 = moe_alltracts(df, 'nocol2')
    citywide_college_e_2 = moe_alltracts(df, 'col2')
    citywide_pop_edu_e_2 = moe_alltracts(df, popedu2)

    #assign variables to calculate moe for citywide proportion for year 1 - college
    den_7 = citywide_pop_edu_1
    num_e_7 = citywide_college_e_1
    den_e_7 = citywide_pop_edu_e_1
    prop_7 = citywide_college_p_1

    #use moe_perc function for year 1
    citywide_college_moe_1 = moe_perc(den_7, num_e_7, den_e_7, prop_7)

    #assign variables to calculate moe for citywide proportion for year 2 - college and no college
    den_8 = citywide_pop_edu_2
    num_e_8 = citywide_nocollege_e_2
    den_e_8 = citywide_pop_edu_e_2
    prop_8 = citywide_nocollege_p_2

    #use moe_perc function for year 2 - no college
    citywide_nocollege_moe_2 = moe_perc(den_8, num_e_8, den_e_8, prop_8)

    den_9 = citywide_pop_edu_2
    num_e_9 = citywide_college_e_2
    den_e_9 = citywide_pop_edu_e_2
    prop_9 = citywide_college_p_2

    #use moe_perc function for year 2 - college
    citywide_college_moe_2 = moe_perc(den_9, num_e_9, den_e_9, prop_9)

    #For each tract, calculate change percentage point change from year 1 to year 2
    df['colch'] = df['colp2'] - df['colp1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_college_change = citywide_college_p_2 - citywide_college_p_1

    citywide_college_change_e = moe_propagation(citywide_college_moe_1, citywide_college_moe_2)


    ##MEDIAN HOUSEHOLD INCOME##

    #Still need to look into MOE for this calculation

    #adjust year 1 values for inflation
    df['mhi1adj'] = cpi.inflate(df[mhi1], yr1, to = yr2)

    #Calculate citywide average mfi years 1 and 2
    citywide_meanmhi_1 = df['mhi1adj'].mean()
    citywide_meanmhi_2 = df[mhi2].mean()

    #For each tract, calculate change in mfi from year 1 to year 2
    df['mhipch'] = (df[mhi2] - df['mhi1adj'])/df[mhi2]

    #Calculate the citywide change in mfi from year 1 to year 2 and the moe
    citywide_mhi_pchange = (citywide_meanmhi_2 - citywide_meanmhi_1)/citywide_meanmhi_2


    ###INDEX 1: VULNERABILITY SCORE###

    #This index will use ACS values from year 2

    ##TENURE##

    #Calculate threshold for proportion of renters
    citywide_renter_threshold = citywide_renter_p_2 - citywide_renter_moe_2

    #Calculate whether the % renters each tract is at or above the citywide median (minus the MOE)
    df['renterv'] = np.where(df['renterp2'] >= citywide_renter_threshold, 1, 0)

    ##RACE AND ETHNICITY##

    #Calculate threshold for proportion of poc
    citywide_poc_threshold = citywide_poc_p_2 - citywide_poc_moe_2

    #Calculate whether the % POC of each tract is at above the citywide median (minus MOE)
    df['pocv'] = np.where(df['pocp2'] >= citywide_poc_threshold, 1, 0)


    ##EDUCATIONAL ATTAINMENT##

    #Calculate threshold for proportion of people 25+ without college degrees
    citywide_nocollege_threshold = citywide_nocollege_p_2 - citywide_nocollege_moe_2

    #Calculate whether the % 25+ without college deg for each tract is at above the citywide median (minus MOE)

    df['nocolv'] = np.where(df['nocolp2'] >= citywide_nocollege_threshold, 1, 0)


    ##MFI##

    citywide_meanmfi_2 = df[mfi2].mean()
    citywide_mfi_threshold = citywide_meanmfi_2 * 0.8 #threshold is 80% of median mfi

    #Caluclate whether the MFI for each tract is at or below 80% of the citywide MFI
    df['mfiv'] = np.where(df[mfi2] <= citywide_mfi_threshold, 1, 0)


    ##TOTAL VULNERABILITY  SCORE##
    #Calculate score 0-4, weight of 1 for each category and create new column (and/or pandas series)

    df['vindex'] = df['renterv'] + df['pocv'] + df['nocolv'] + df['mfiv']


    ###INDEX 2: GENTRIFICATION RELATED DEMOGRAPHIC CHANGE###


    ##TENURE##
    #For each tract, calculate if proportion of owners 2010-2020 increased or decreased less the   citywide percentage point change (minus MOE)
    citywide_ownerchange_threshold = citywide_owner_change - citywide_owner_change_e

    df['tench'] = np.where(df['ownerch'] > citywide_ownerchange_threshold, 1, 0) 


    ##RACE AND ETHNICITY##
    #For each tract, calculate if proportion of white pop 2010-2020 increased or decreased less the citywide percentage point change (minus MOE)

    citywide_whitechange_threshold = citywide_white_change - citywide_white_change_e

    df['racech'] = np.where(df['whitech'] > citywide_whitechange_threshold, 1, 0) 


    ##EDUCATIONAL ATTAINMENT##
    #For each tract, calculate if change in proportion of 25+ without a college degree 2010-2020 is above or below the citywide percentage point change (add or subtact MOE)

    citywide_collegechange_threshold = citywide_college_change - citywide_college_change_e

    df['educh'] = np.where(df['colch'] > citywide_collegechange_threshold, 1, 0) 


    ##MHI##
    #For each tract, calculate if percent change in MHI 2010-2020 is above or below the citywide percent change (add or subtact MOE)

    df['incomech'] = np.where(df['mhipch'] > citywide_mhi_pchange, 1, 0) 


    ##SCORE: YES OR NO GENTRIFICATION RELATED DEMOGRAPHIC CHANGE##

    #YES if threshold is met for 3 out of four categories OR if meets threshold for %white and % 25+ with college degree
              

    df['demchindex'] = np.where((df['tench'] + df['racech'] +  df['educh'] + df['incomech']) >=3, True, np.where((df['racech'] + df['educh']) == 2, True, False ))
    
    ###INDEX 3: HOUSING MARKET CONDITIONS###

    ##2000, 2010, AND 2020 VALUES##
    #Calculate quintiles for year 0 and year 2

    #year 0
    df['homeq0'] = pd.qcut(df[mhv0], 5, labels = [0,1,2,3,4]).astype('int')

    df['homeq0'] = np.where(df['homeq0'] <= 2, 'lowmod', 'high')

    #year 2
    df['homeq2'] = pd.qcut(df[mhv2], 5, labels = [0,1,2,3,4]).astype('int')

    df['homeq2'] = df['homeq2'] = np.where(df['homeq2'] <= 2, 'lowmod', 'high')

    ##CHANGE 2000-2010##
    #Calculate change in median value for each tract and quintiles
    df['homech01q'] = df[mhv1] - df[mhv0]
    df['homech01q'] = pd.qcut(df['homech01q'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homech01q'] = np.where(df['homech01q'] <= 2, 'lowmod', 'high')


    ##CHANGE 2010-2020##
    #Calculate change in median value for each tract and quintiles
    df['homech12q'] = df[mhv2] - df[mhv1]
    df['homech12q'] = pd.qcut(df['homech12q'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homech12q'] = np.where(df['homech12q'] <= 2, 'lowmod', 'high')

    ##CHANGE 2000-2020##
    #Calculate change in median value for each tract and quintiles
    df['homech02q'] = df[mhv2] - df[mhv0]
    df['homech02q'] = pd.qcut(df['homech02q'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homech02q'] = np.where(df['homech02q'] <= 2, 'lowmod', 'high')

    ##TYPLOGY##

    #Create bool column to check if each tract has high 2020 value and/or touches a tract       with a high 2020 value

    df['adj_list'] = None  
    df['adjhigh2'] = None

    for index, row in df.iterrows():   

        # get 'not disjoint' countries
        neighbors = df[~df.geometry.disjoint(row.geometry)].homeq2.tolist()

        # add names of neighbors as NEIGHBORS value
        df.at[index, 'adj_list'] = neighbors

        if (neighbors.count('high') == 1) & (row.homeq2 == 'high'):
            df.at[index, 'adjhigh2'] = False
    
        elif ('high' in neighbors):
            df.at[index, 'adjhigh2'] = True
        
        else:
            df.at[index, 'adjhigh2'] = False
        
        #Create row for housing value typology

    #Adjacent: low or moderate 2020 value, low or moderate 2000-2010 appreciation, touch boundary of one tract with high 2020 value

    #Accelerating: low or moderate 2020 value, high 2010-2020 apprecation

    #Appreciated: low or moderate 2000 value, high 2020 value, high 2000-2020 appreciation

        
    df['mhv_type'] = None
    for index, row in df.iterrows():
    
        if (row.homeq2 == 'lowmod') & (row.homech01q == 'lowmod') & (row.adjhigh2== True):
        
            df.at[index, 'mhv_type'] = 'adjacent'
        
        elif (row.homeq2 == 'lowmod') & (row.homech12q == 'high'):
        
            df.at[index, 'mhv_type'] = 'accelerating'
        
        elif (row.homeq0 == 'lowmod') & (row.homeq2 == 'high') & (row.homech02q == 'high'):
        
            df.at[index, 'mhv_type'] = 'appreciated'
        
        else:
        
            df.at[index, 'mhv_type'] = 'no_typology'


    ###INDEX 4: FREEMAN INDEX###

    ##YEAR STRUCTURE BUILT##
    #Calculate whether the % housing build in last 20 years in each tract in 2020 is below the citywide median and 40th percentile

    df['newhousp'] = (df[y10to13] + df[y14topr])/df[tothous]
    citywide_newhous_med = df['newhousp'].median()

    df['newhous_fr'] = np.where(df['newhousp'] < citywide_newhous_med, 1, 0)


    ##EDUCATIONAL ATTAINMENT##
    #For each tract, calculate change in % 25+ without a college degree 2010-2020 and if this change is above the citywide percentage point change (without subtracting the MOE)

    df['nocolch'] = df['nocolp2'] - df['nocolp1']

    citywide_nocolch = (df['nocol2'].sum()/df['popedu2'].sum()) - (df['nocol1'].sum()/df[popedu1].sum())

    df['nocol_fr'] = np.where(df['nocolch'] > citywide_nocolch, 1, 0)


    ##MEDIAN HOUSEHOLD INCOME

    df['mhi_fr'] = np.where(df[mhi1] < df[mhi1].mean(), 1, 0 )

    ##HOUSING VALUE##
    #Calcuate if median housing values 2010-2020 increased (yes or no)

    df['mhv_fr'] = np.where((df[mhv2] - df[mhv1]) > 0, 1, 0)


    ##FREEMAN SCORE##
    #To be considered gentrifying, tract must meet fufill all categories 

    df['freeman'] = np.where((df['newhous_fr'] + df['nocol_fr'] + df['mhi_fr'] +    df['mhv_fr']) == 4, True, False)
    
    newcolumns =df[['renterv', 'pocv', 'nocolv', 'mfiv', 'vindex', 'tench', 'racech', 'educh', 'incomech', 'demchindex','homeq0','homeq2','homech01q','homech12q','homech02q','mhv_type', 'nocol_fr','mhi_fr','mhv_fr','freeman']].reset_index()
    
    keepcolumns =df[[ 'GEO_ID','NAME_y','STATEFP','COUNTYFP','TRACTCE','ALAND','AWATER','INTPTLAT','INTPTLON', 'geometry']].reset_index()
    
    if inplace == False:
        output = pd.merge(keepcolumns, newcolumns, left_index= True, right_index = True)
    
    else:
        output = pd.merge(copy_df, newcolumns, left_index= True, right_index = True)
    
    return output

#%%

###TEST###

newdf = calc_batesfreeman(bates_df, 2010, 2020, 'renter1', 'owner1', 'popten1', 'renter2', 'owner2', 'popten2', 'white1', 'poprac1', 'white2', 'poprac2', 'ASdegm1', 'ASdegf1', 'BAdegm1', 'BAdegf1', 'MAdegm1', 'MAdegf1', 'prodegm1', 'prodegf1', 'drdegm1', 'drdegf1', 'popedu1', 'ASdegm2', 'ASdegf2', 'BAdegm2', 'BAdegf2', 'MAdegm2', 'MAdegf2', 'prodegm2', 'prodegf2', 'drdegm2', 'drdegf2', 'popedu2', 'mfi2', 'mhi1', 'mhi2', 'mhv0', 'mhv1', 'mhv2', 'tothous', 'y10to13', 'y14topr', inplace = False)

samedf = calc_batesfreeman(bates_df, 2010, 2020, 'renter1', 'owner1', 'popten1', 'renter2', 'owner2', 'popten2', 'white1', 'poprac1', 'white2', 'poprac2', 'ASdegm1', 'ASdegf1', 'BAdegm1', 'BAdegf1', 'MAdegm1', 'MAdegf1', 'prodegm1', 'prodegf1', 'drdegm1', 'drdegf1', 'popedu1', 'ASdegm2', 'ASdegf2', 'BAdegm2', 'BAdegf2', 'MAdegm2', 'MAdegf2', 'prodegm2', 'prodegf2', 'drdegm2', 'drdegf2', 'popedu2', 'mfi2', 'mhi1', 'mhi2', 'mhv0', 'mhv1', 'mhv2', 'tothous', 'y10to13', 'y14topr', inplace = True)


#%%
###EXPORT DF###