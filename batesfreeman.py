"""
Calculating the Bates (2013) gentrification indices and the Freeman (2005) gentrification index
"""
#%%
import pandas as pd
import os
from math import sqrt
import numpy as np
import geopandas as gpd

os.chdir('/Users/wc555/gus8066/gentrification-indices')

from batesfreeman_createdf import bates_df_geo   
bates_df_geo = gpd.GeoDataFrame(bates_df_geo, geometry = 'geometry', crs = 'EPSG: 4269')

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


def calc_batesfreeman(df, infl_rate, pop_tenure_yr1, owners_yr1, renters_yr1, pop_tenure_yr2, owners_yr2, renters_yr2, pop_edu_yr1, pop_edu_m_yr1, ASdeg_m_yr1, BAdeg_m_yr1, MAdeg_m_yr1, profdeg_m_yr1, drdeg_m_yr1, pop_edu_f_yr1, ASdeg_f_yr1, BAdeg_f_yr1, MAdeg_f_yr1, profdeg_f_yr1, drdeg_f_yr1, pop_edu_yr2, pop_edu_m_yr2, ASdeg_m_yr2, BAdeg_m_yr2, MAdeg_m_yr2, profdeg_m_yr2, drdeg_m_yr2, pop_edu_f_yr2, ASdeg_f_yr2, BAdeg_f_yr2, MAdeg_f_yr2, profdeg_f_yr2, drdeg_f_yr2, pop_race_yr1, white_yr1, pop_race_yr2, white_yr2, mfi_yr1, mfi_yr2, mhv_yr0, mhv_yr1, mhv_yr2, mhi_yr1, mhi_yr2, tothouse_yr2, newhouse_col1, newhouse_col2, inplace = False):
    
    ##Create two deep copies##
    #The first will be used at the end of the function to return the orginal input df with the new output columns appended.
    #The second will make a copy that the rest of the function uses to calculate all intermediate columns (needed to caclulate final output columns) without adding them to the initial input df.
    copy_df = df.copy(deep = True)
    df = df.copy(deep = True)    
    
    ###CREATE DERIVED COLUMNS AND VALUES NEEDED FOR INDICES###

    ##TENURE##

    #create new columns with proportion of renters in each tract for years 1 and 2
    df['renterp_yr1'] = df[renters_yr1]/df[pop_tenure_yr1]
    df['ownerp_yr1'] = 1 - df['renterp_yr1']
    df['renterp_yr2'] = df[renters_yr2]/df[pop_tenure_yr2]
    df['ownerp_yr2'] = 1 - df['renterp_yr2']

    #calculate the citywide proportion of renters for years 1 and 2
    citywide_renters_1 = df[renters_yr1].sum()
    citywide_tenure_1 = df[pop_tenure_yr1].sum()

    citywide_renters_2 = df[renters_yr2].sum()
    citywide_tenure_2 = df[pop_tenure_yr2].sum()

    citywide_renter_p_1 = citywide_renters_1/citywide_tenure_1
    citywide_owner_p_1 = 1 - citywide_renter_p_1
    citywide_renter_p_2 = citywide_renters_2/citywide_tenure_2
    citywide_owner_p_2 = 1 - citywide_renter_p_2

    #calculate the citywide moe for the number of renters and total number of households for years 1 and 2
    citywide_owner_e_1 = moe_alltracts(df, owners_yr1)
    citywide_tenure_e_1 = moe_alltracts(df, pop_tenure_yr1)

    citywide_renter_e_2 = moe_alltracts(df, renters_yr2)
    citywide_owner_e_2 = moe_alltracts(df, owners_yr2)
    citywide_tenure_e_2 = moe_alltracts(df, pop_tenure_yr2)

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
    df['owner_change'] = df['ownerp_yr2'] - df['ownerp_yr1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_owner_change = citywide_owner_p_2 - citywide_owner_p_1

    citywide_owner_change_e = moe_propagation(citywide_owner_moe_1, citywide_owner_moe_2)


    ##RACE AND ETHNICITY##

    #Calculate proportion of POC and white pop for each tract for years 1 and 2
    df['poc_yr1'] = df[pop_race_yr1] - df[white_yr1]
    df['pocp_yr1'] = (df['poc_yr1']/df[pop_race_yr1])
    df['whitep_yr1'] = 1 - df['pocp_yr1']

    df['poc_yr2'] = df[pop_race_yr2] - df[white_yr2]
    df['pocp_yr2'] = (df['poc_yr2']/df[pop_race_yr1])
    df['whitep_yr2'] = 1 - df['pocp_yr2']

    #Calculate citywide proportion of people of color for years 1 and 2

    citywide_pop_race_1 = df[pop_race_yr1].sum()
    citywide_poc_1 = df['poc_yr1'].sum()
    citywide_poc_p_1 = citywide_poc_1/citywide_pop_race_1
    citywide_white_p_1 = 1 - citywide_poc_p_1 


    citywide_pop_race_2 = df[pop_race_yr2].sum()
    citywide_poc_2 = df['poc_yr2'].sum()
    citywide_poc_p_2 = citywide_poc_2/citywide_pop_race_2
    citywide_white_p_2 = 1 - citywide_poc_p_2 

    #calculate the citywide moe for the number of poc and total pop for years 1 and 2
    #citywide_poc_e_1 = moe_alltracts(df, 'poc_1')
    citywide_white_e_1 = moe_alltracts(df, white_yr1)
    citywide_pop_race_e_1 = moe_alltracts(df, pop_race_yr1)

    citywide_poc_e_2 = moe_alltracts(df, 'poc_yr2')
    citywide_white_e_2 = moe_alltracts(df, white_yr2)
    citywide_pop_race_e_2 = moe_alltracts(df, pop_race_yr2)

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
    df['white_change'] = df['whitep_yr2'] - df['whitep_yr1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_white_change = citywide_white_p_2 - citywide_white_p_1

    citywide_white_change_e = moe_propagation(citywide_white_moe_1, citywide_white_moe_2)

    ##EDUCATIONAL ATTAINMENT##

    #Calculate proportion 25+ population with and without a college degree for each tract for years 1 and 2
    df['nocollege_yr1'] = (df[pop_edu_yr1]) - (df[ASdeg_m_yr1] + df[BAdeg_m_yr1] + df[MAdeg_m_yr1] + df[profdeg_m_yr1] + df[drdeg_m_yr1]) - (df[ASdeg_f_yr1] + df[BAdeg_f_yr1] + df[MAdeg_f_yr1] + df[profdeg_f_yr1] + df[drdeg_f_yr1])

    df['college_yr1'] = df[pop_edu_yr1] - df['nocollege_yr1']

    df['nocollegep_yr1'] = df['nocollege_yr1'] / df[pop_edu_yr1]
    df['collegep_yr1'] = 1 - df['nocollegep_yr1']

    df['nocollege_yr2'] = (df[pop_edu_yr2]) - (df[ASdeg_m_yr2] + df[BAdeg_m_yr2] + df[MAdeg_m_yr2] + df[profdeg_m_yr2] + df[drdeg_m_yr2]) - (df[ASdeg_f_yr2] + df[BAdeg_f_yr2] + df[MAdeg_f_yr2] + df[profdeg_f_yr2] + df[drdeg_f_yr2])

    df['college_yr2'] = df[pop_edu_yr2] - df['nocollege_yr2']

    df['nocollegep_yr2'] = df['nocollege_yr2'] / df[pop_edu_yr2]
    df['collegep_yr2'] = 1 - df['nocollegep_yr2']

    #Calculate citywide proportion of people without a college degree for years 1 and 2

    citywide_pop_edu_1 = df[pop_edu_yr1].sum()
    citywide_nocollege_1 = df['nocollege_yr1'].sum()
    #citywide_college_1 = citywide_pop_edu_1 - citywide_nocollege_1
    citywide_nocollege_p_1 = citywide_nocollege_1/citywide_pop_edu_1
    citywide_college_p_1 = 1 - citywide_nocollege_p_1

    citywide_pop_edu_2 = df[pop_edu_yr2].sum()
    citywide_nocollege_2 = df['nocollege_yr2'].sum()
    #citywide_college_2 = citywide_pop_edu_2 - citywide_nocollege_2
    citywide_nocollege_p_2 = citywide_nocollege_2/citywide_pop_edu_2
    citywide_college_p_2 = 1 - citywide_nocollege_p_2


    #calculate the citywide moe for the number of people w/o college degrees and total pop for years 1 and 2
    #citywide_nocollege_e_1 = moe_alltracts(df, 'nocollege_1')
    citywide_college_e_1 = moe_alltracts(df, 'college_yr1')
    citywide_pop_edu_e_1 = moe_alltracts(df, pop_edu_yr1)

    citywide_nocollege_e_2 = moe_alltracts(df, 'nocollege_yr2')
    citywide_college_e_2 = moe_alltracts(df, 'college_yr2')
    citywide_pop_edu_e_2 = moe_alltracts(df, pop_edu_yr2)

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
    df['college_change'] = df['collegep_yr2'] - df['collegep_yr1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_college_change = citywide_college_p_2 - citywide_college_p_1

    citywide_college_change_e = moe_propagation(citywide_college_moe_1, citywide_college_moe_2)


    ##MEDIAN HOUSEHOLD INCOME##

    #Still need to look into MOE for this calculation

    #adjust year 1 values for inflation
    df['mhi_yr1_adj'] = df[mhi_yr1] * float(infl_rate)

    #Calculate citywide average mfi years 1 and 2
    citywide_meanmhi_1 = df['mhi_yr1_adj'].mean()
    citywide_meanmhi_2 = df[mhi_yr2].mean()

    #For each tract, calculate change in mfi from year 1 to year 2
    df['mhip_change'] = (df[mhi_yr2] - df['mhi_yr1_adj'])/df[mhi_yr2]

    #Calculate the citywide change in mfi from year 1 to year 2 and the moe
    citywide_mhi_pchange = (citywide_meanmhi_2 - citywide_meanmhi_1)/citywide_meanmhi_2


    ###INDEX 1: VULNERABILITY SCORE###

    #This index will use ACS values from year 2

    ##TENURE##

    #Calculate threshold for proportion of renters
    citywide_renter_threshold = citywide_renter_p_2 - citywide_renter_moe_2

    #Calculate whether the % renters each tract is at or above the citywide median (minus the MOE)
    df['renter_v'] = np.where(df['renterp_yr2'] >= citywide_renter_threshold, 1, 0)

    ##RACE AND ETHNICITY##

    #Calculate threshold for proportion of poc
    citywide_poc_threshold = citywide_poc_p_2 - citywide_poc_moe_2

    #Calculate whether the % POC of each tract is at above the citywide median (minus MOE)
    df['poc_v'] = np.where(df['pocp_yr2'] >= citywide_poc_threshold, 1, 0)


    ##EDUCATIONAL ATTAINMENT##

    #Calculate threshold for proportion of people 25+ without college degrees
    citywide_nocollege_threshold = citywide_nocollege_p_2 - citywide_nocollege_moe_2

    #Calculate whether the % 25+ without college deg for each tract is at above the citywide median (minus MOE)

    df['nocollege_v'] = np.where(df['nocollegep_yr2'] >= citywide_nocollege_threshold, 1, 0)


    ##MFI##

    citywide_meanmfi_2 = df[mfi_yr2].mean()
    citywide_mfi_threshold = citywide_meanmfi_2 * 0.8 #threshold is 80% of median mfi

    #Caluclate whether the MFI for each tract is at or below 80% of the citywide MFI
    df['mfi_v'] = np.where(df[mfi_yr2] <= citywide_mfi_threshold, 1, 0)


    ##TOTAL VULNERABILITY  SCORE##
    #Calculate score 0-4, weight of 1 for each category and create new column (and/or pandas series)

    df['v_index'] = df['renter_v'] + df['poc_v'] + df['nocollege_v'] + df['mfi_v']


    ###INDEX 2: GENTRIFICATION RELATED DEMOGRAPHIC CHANGE###


    ##TENURE##
    #For each tract, calculate if proportion of owners 2010-2020 increased or decreased less the   citywide percentage point change (minus MOE)
    citywide_ownerchange_threshold = citywide_owner_change - citywide_owner_change_e

    df['tenure_change'] = np.where(df['owner_change'] > citywide_ownerchange_threshold, 1, 0) 


    ##RACE AND ETHNICITY##
    #For each tract, calculate if proportion of white pop 2010-2020 increased or decreased less the citywide percentage point change (minus MOE)

    citywide_whitechange_threshold = citywide_white_change - citywide_white_change_e

    df['race_change'] = np.where(df['white_change'] > citywide_whitechange_threshold, 1, 0) 


    ##EDUCATIONAL ATTAINMENT##
    #For each tract, calculate if change in proportion of 25+ without a college degree 2010-2020 is above or below the citywide percentage point change (add or subtact MOE)

    citywide_collegechange_threshold = citywide_college_change - citywide_college_change_e

    df['edu_change'] = np.where(df['college_change'] > citywide_collegechange_threshold, 1, 0) 


    ##MHI##
    #For each tract, calculate if percent change in MHI 2010-2020 is above or below the citywide percent change (add or subtact MOE)

    df['income_change'] = np.where(df['mhip_change'] > citywide_mhi_pchange, 1, 0) 


    ##SCORE: YES OR NO GENTRIFICATION RELATED DEMOGRAPHIC CHANGE##

    #YES if threshold is met for 3 out of four categories OR if meets threshold for %white and % 25+ with college degree
              

    df['dem_change_index'] = np.where((df['tenure_change'] + df['race_change'] +  df['edu_change'] + df['income_change']) >=3, True, np.where((df['race_change'] + df['edu_change']) == 2, True, False ))
    
    ###INDEX 3: HOUSING MARKET CONDITIONS###

    ##2000, 2010, AND 2020 VALUES##
    #Calculate quintiles for year 0 and year 2

    #year 0
    df['homevalueq_yr0'] = pd.qcut(df[mhv_yr0], 5, labels = [0,1,2,3,4]).astype('int')

    df['homevalueq_yr0'] = np.where(df['homevalueq_yr0'] <= 2, 'lowmod', 'high')

    #year 2
    df['homevalueq_yr2'] = pd.qcut(df[mhv_yr2], 5, labels = [0,1,2,3,4]).astype('int')

    df['homevalueq_yr2'] = df['homevalueq_yr2'] = np.where(df['homevalueq_yr2'] <= 2, 'lowmod', 'high')

    ##CHANGE 2000-2010##
    #Calculate change in median value for each tract and quintiles
    df['homevalueq_change_01'] = df[mhv_yr1] - df[mhv_yr0]
    df['homevalueq_change_01'] = pd.qcut(df['homevalueq_change_01'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homevalueq_change_01'] = np.where(df['homevalueq_change_01'] <= 2, 'lowmod', 'high')


    ##CHANGE 2010-2020##
    #Calculate change in median value for each tract and quintiles
    df['homevalueq_change_12'] = df[mhv_yr2] - df[mhv_yr1]
    df['homevalueq_change_12'] = pd.qcut(df['homevalueq_change_12'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homevalueq_change_12'] = np.where(df['homevalueq_change_12'] <= 2, 'lowmod', 'high')

    ##CHANGE 2000-2020##
    #Calculate change in median value for each tract and quintiles
    df['homevalueq_change_02'] = df[mhv_yr2] - df[mhv_yr0]
    df['homevalueq_change_02'] = pd.qcut(df['homevalueq_change_02'], 5, labels = [0,1,2,3,4]).astype('int')
    df['homevalueq_change_02'] = np.where(df['homevalueq_change_02'] <= 2, 'lowmod', 'high')

    ##TYPLOGY##

    #Create bool column to check if each tract has high 2020 value and/or touches a tract       with a high 2020 value

    df['adjacent_list'] = None  
    df['adjacent_high_yr2'] = None

    for index, row in df.iterrows():   

        # get 'not disjoint' tracts
        neighbors = df[~df.geometry.disjoint(row.geometry)].homevalueq_yr2.tolist()

        # add names of neighbors as NEIGHBORS value
        df.at[index, 'adjacent_list'] = neighbors

        if (neighbors.count('high') == 1) & (row.homevalueq_yr2 == 'high'):
            df.at[index, 'adjacent_high_yr2'] = False
    
        elif ('high' in neighbors):
            df.at[index, 'adjacent_high_yr2'] = True
        
        else:
            df.at[index, 'adjacent_high_yr2'] = False
        
        #Create row for housing value typology

    #Adjacent: low or moderate 2020 value, low or moderate 2000-2010 appreciation, touch boundary of one tract with high 2020 value

    #Accelerating: low or moderate 2020 value, high 2010-2020 apprecation

    #Appreciated: low or moderate 2000 value, high 2020 value, high 2000-2020 appreciation

        
    df['mhv_type'] = None
    for index, row in df.iterrows():
    
        if (row.homevalueq_yr2 == 'lowmod') & (row.homevalueq_change_01 == 'lowmod') & (row.adjacent_high_yr2 == True):
        
            df.at[index, 'mhv_type'] = 'adjacent'
        
        elif (row.homevalueq_yr2 == 'lowmod') & (row.homevalueq_change_12 == 'high'):
        
            df.at[index, 'mhv_type'] = 'accelerating'
        
        elif (row.homevalueq_yr0 == 'lowmod') & (row.homevalueq_yr2 == 'high') & (row.homevalueq_change_02 == 'high'):
        
            df.at[index, 'mhv_type'] = 'appreciated'
        
        else:
        
            df.at[index, 'mhv_type'] = 'no_typology'


    ###INDEX 4: FREEMAN INDEX###

    ##YEAR STRUCTURE BUILT##
    #Calculate whether the % housing build in last 20 years in each tract in 2020 is below the citywide median and 40th percentile

    df['newhousp'] = (df[newhouse_col1] + df[newhouse_col2])/df[tothouse_yr2]
    citywide_newhous_med = df['newhousp'].median()

    df['newhous_f_index'] = np.where(df['newhousp'] < citywide_newhous_med, 1, 0)


    ##EDUCATIONAL ATTAINMENT##
    #For each tract, calculate change in % 25+ without a college degree 2010-2020 and if this change is above the citywide percentage point change (without subtracting the MOE)

    df['nocollege_change'] = df['nocollegep_yr2'] - df['nocollegep_yr1']

    citywide_nocolch = (df['nocollege_yr2'].sum()/df[pop_edu_yr2].sum()) - (df['nocollege_yr1'].sum()/df[pop_edu_yr1].sum())

    df['nocollege_f_index'] = np.where(df['nocollege_change'] > citywide_nocolch, 1, 0)


    ##MEDIAN HOUSEHOLD INCOME

    df['mhi_f_index'] = np.where(df[mhi_yr1] < df[mhi_yr1].mean(), 1, 0 )

    ##HOUSING VALUE##
    #Calcuate if median housing values 2010-2020 increased (yes or no)

    df['mhv_f_index'] = np.where((df[mhv_yr2] - df[mhv_yr1]) > 0, 1, 0)


    ##FREEMAN SCORE##
    #To be considered gentrifying, tract must meet fufill all categories 


    df['freeman'] = np.where((df['newhous_f_index'] + df['nocollege_f_index'] + df['mhi_f_index'] +    df['mhv_f_index']) == 4, True, False)
    
    newcolumns = df[['renter_v', 'poc_v', 'nocollege_v', 'mfi_v', 'v_index', 'tenure_change', 'race_change', 'edu_change', 'income_change', 'dem_change_index','homevalueq_yr0', 'homevalueq_yr2','homevalueq_change_01','homevalueq_change_12','homevalueq_change_02','mhv_type', 'nocollege_f_index','mhi_f_index','mhv_f_index','freeman']].reset_index()
    
    keepcolumns =df[[ 'GEOID','NAMELSAD','ALAND','AWATER','INTPTLAT','INTPTLON', 'geometry']].reset_index()
    
    if inplace == False:
        output = pd.merge(keepcolumns, newcolumns, left_index= True, right_index = True)
    
    else:
        output = pd.merge(copy_df, newcolumns, left_index= True, right_index = True)
    
    print(df)
    
    return output

#%%

###TEST###


newdf = calc_batesfreeman(bates_df_geo, 1.19, 'pop_tenure_yr1', 'owners_yr1', 'renters_yr1', 'pop_tenure_yr2', 'owners_yr2', 'renters_yr2', 'pop_edu_yr1', 'pop_edu_m_yr1', 'ASdeg_m_yr1', 'BAdeg_m_yr1', 'MAdeg_m_yr1', 'profdeg_m_yr1', 'drdeg_m_yr1', 'pop_edu_f_yr1', 'ASdeg_f_yr1', 'BAdeg_f_yr1', 'MAdeg_f_yr1', 'profdeg_f_yr1', 'drdeg_f_yr1', 'pop_edu_yr2', 'pop_edu_m_yr2', 'ASdeg_m_yr2', 'BAdeg_m_yr2', 'MAdeg_m_yr2', 'profdeg_m_yr2', 'drdeg_m_yr2', 'pop_edu_f_yr2', 'ASdeg_f_yr2', 'BAdeg_f_yr2', 'MAdeg_f_yr2', 'profdeg_f_yr2', 'drdeg_f_yr2', 'pop_race_yr1', 'white_yr1', 'pop_race_yr2', 'white_yr2', 'mfi_yr1', 'mfi_yr2', 'mhv_yr0', 'mhv_yr1', 'mhv_yr2', 'mhi_yr1', 'mhi_yr2', 'tothouse_yr2', 'newhouse_col1', 'newhouse_col2', inplace = False)

samedf = calc_batesfreeman(bates_df_geo, 1.19, 'pop_tenure_yr1', 'owners_yr1', 'renters_yr1', 'pop_tenure_yr2', 'owners_yr2', 'renters_yr2', 'pop_edu_yr1', 'pop_edu_m_yr1', 'ASdeg_m_yr1', 'BAdeg_m_yr1', 'MAdeg_m_yr1', 'profdeg_m_yr1', 'drdeg_m_yr1', 'pop_edu_f_yr1', 'ASdeg_f_yr1', 'BAdeg_f_yr1', 'MAdeg_f_yr1', 'profdeg_f_yr1', 'drdeg_f_yr1', 'pop_edu_yr2', 'pop_edu_m_yr2', 'ASdeg_m_yr2', 'BAdeg_m_yr2', 'MAdeg_m_yr2', 'profdeg_m_yr2', 'drdeg_m_yr2', 'pop_edu_f_yr2', 'ASdeg_f_yr2', 'BAdeg_f_yr2', 'MAdeg_f_yr2', 'profdeg_f_yr2', 'drdeg_f_yr2', 'pop_race_yr1', 'white_yr1', 'pop_race_yr2', 'white_yr2', 'mfi_yr1', 'mfi_yr2', 'mhv_yr0', 'mhv_yr1', 'mhv_yr2', 'mhi_yr1', 'mhi_yr2', 'tothouse_yr2', 'newhouse_col1', 'newhouse_col2', inplace = True)


#%%
###EXPORT DF###