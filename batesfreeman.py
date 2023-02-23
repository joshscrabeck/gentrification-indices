"""
Calculating the Bates (2013) gentrification indices and the Freeman (2005) gentrification index
"""
#%%
import pandas as pd
import os
from math import sqrt
import numpy as np
import cpi

os.chdir('/Users/winncostantini/gus8066/gentrification-indices')

bates_df = pd.read_csv('bates_df.csv')

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

def calc_batesfreeman(df, year1, year2, renters_1, owners_1, pop_tenure_1, renters_2, owners_2, pop_tenure_2, white_nhl_1, pop_race_1, white_nhl_2, pop_race_2, ASdegree_m_1, ASdegree_f_1, BAdegree_m_1, BAdegree_f_1, MAdegree_m_1, MAdegree_f_1, profdegree_m_1, profdegree_f_1, docdegree_m_1, docdegree_f_1, pop_edu_1, ASdegree_m_2, ASdegree_f_2, BAdegree_m_2, BAdegree_f_2, MAdegree_m_2, MAdegree_f_2, profdegree_m_2, profdegree_f_2, docdegree_m_2, docdegree_f_2, pop_edu_2, mfi_2, mhi_1, mhi_2, inplace = False):
    
    ###CREATE DERIVED COLUMNS AND VALUES NEEDED FOR INDICES###

    ##TENURE##

    #create new columns with proportion of renters in each tract for years 1 and 2
    df['renters_p_1'] = df[renters_1]/bates_df[pop_tenure_1]
    df['owners_p_1'] = 1 - df['renters_p_1']
    df['renters_p_2'] = df[renters_2]/df[pop_tenure_2]
    df['owners_p_2'] = 1 - df['renters_p_2']

    #calculate the citywide proportion of renters for years 1 and 2
    citywide_renters_1 = df[renters_1].sum()
    citywide_tenure_1 = df[pop_tenure_1].sum()

    citywide_renters_2 = df[renters_2].sum()
    citywide_tenure_2 = df[pop_tenure_2].sum()

    citywide_renter_p_1 = citywide_renters_1/citywide_tenure_1
    citywide_owner_p_1 = 1 - citywide_renter_p_1
    citywide_renter_p_2 = citywide_renters_2/citywide_tenure_2
    citywide_owner_p_2 = 1 - citywide_renter_p_2

    #calculate the citywide moe for the number of renters and total number of households for years 1 and 2
    #citywide_renter_e_1 = moe_alltracts(df, renters_1)
    citywide_owner_e_1 = moe_alltracts(df, owners_1)
    citywide_tenure_e_1 = moe_alltracts(df, pop_tenure_1)

    citywide_renter_e_2 = moe_alltracts(df, renters_2)
    citywide_owner_e_2 = moe_alltracts(df, owners_2)
    citywide_tenure_e_2 = moe_alltracts(df, pop_tenure_2)

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
    df['owner_change'] = df['owners_p_2'] - bates_df['owners_p_1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_owner_change = citywide_owner_p_2 - citywide_owner_p_1

    citywide_owner_change_e = moe_propagation(citywide_owner_moe_1, citywide_owner_moe_2)


    ##RACE AND ETHNICITY##

    #Calculate proportion of POC and white pop for each tract for years 1 and 2
    df['poc_1'] = df[pop_race_1] - df[white_nhl_1]
    df['poc_p_1'] = (df['poc_1']/df[pop_race_1])
    df['white_p_1'] = 1 - df['poc_p_1']

    df['poc_2'] = df[pop_race_2] - df[white_nhl_2]
    df['poc_p_2'] = (df['poc_2']/df[pop_race_2])
    df['white_p_2'] = 1 - df['poc_p_2']

    #Calculate citywide proportion of people of color for years 1 and 2

    citywide_pop_race_1 = df[pop_race_1].sum()
    citywide_poc_1 = df['poc_1'].sum()
    citywide_poc_p_1 = citywide_poc_1/citywide_pop_race_1
    citywide_white_p_1 = 1 - citywide_poc_p_1 


    citywide_pop_race_2 = df[pop_race_2].sum()
    citywide_poc_2 = df['poc_2'].sum()
    citywide_poc_p_2 = citywide_poc_2/citywide_pop_race_2
    citywide_white_p_2 = 1 - citywide_poc_p_2 

    #calculate the citywide moe for the number of poc and total pop for years 1 and 2
    #citywide_poc_e_1 = moe_alltracts(df, 'poc_1')
    citywide_white_e_1 = moe_alltracts(df, white_nhl_1)
    citywide_pop_race_e_1 = moe_alltracts(df, pop_race_1)

    citywide_poc_e_2 = moe_alltracts(df, 'poc_2')
    citywide_white_e_2 = moe_alltracts(df, white_nhl_2)
    citywide_pop_race_e_2 = moe_alltracts(df, pop_race_2)

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
    df['white_change'] = df['white_p_2'] - df['white_p_1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_white_change = citywide_white_p_2 - citywide_white_p_1

    citywide_white_change_e = moe_propagation(citywide_white_moe_1, citywide_white_moe_2)

    ##EDUCATIONAL ATTAINMENT##

    #Calculate proportion 25+ population with and without a college degree for each tract for years 1 and 2
    df['nocollege_1'] = (df[pop_edu_1]) - (df[ASdegree_m_1] + df[BAdegree_m_1] + df[MAdegree_m_1] + df[profdegree_m_1] + df[docdegree_m_1]) - (df[ASdegree_f_1] + df[BAdegree_f_1] + df[MAdegree_f_1] + df[profdegree_f_1] + df[docdegree_f_1])

    df['college_1'] = df[pop_edu_1] - df['nocollege_1']

    df['nocollege_p_1'] = df['nocollege_1'] / bates_df[pop_edu_1]
    df['college_p_1'] = 1 - df['nocollege_p_1']

    df['nocollege_2'] = (df[pop_edu_2]) - (df[ASdegree_m_2] + df[BAdegree_m_2] + df[MAdegree_m_2] + df[profdegree_m_2] + df[docdegree_m_2]) - (df[ASdegree_f_2] + df[BAdegree_f_2] + df[MAdegree_f_2] + df[profdegree_f_2] + df[docdegree_f_2])

    df['college_2'] = bates_df[pop_edu_2] - bates_df['nocollege_2']

    df['nocollege_p_2'] = bates_df['nocollege_2'] / bates_df[pop_edu_2]
    df['college_p_2'] = 1 - bates_df['nocollege_p_2']

    #Calculate citywide proportion of people without a college degree for years 1 and 2

    citywide_pop_edu_1 = df[pop_edu_1].sum()
    citywide_nocollege_1 = df['nocollege_1'].sum()
    #citywide_college_1 = citywide_pop_edu_1 - citywide_nocollege_1
    citywide_nocollege_p_1 = citywide_nocollege_1/citywide_pop_edu_1
    citywide_college_p_1 = 1 - citywide_nocollege_p_1

    citywide_pop_edu_2 = df[pop_edu_2].sum()
    citywide_nocollege_2 = df['nocollege_2'].sum()
    #citywide_college_2 = citywide_pop_edu_2 - citywide_nocollege_2
    citywide_nocollege_p_2 = citywide_nocollege_2/citywide_pop_edu_2
    citywide_college_p_2 = 1 - citywide_nocollege_p_2


    #calculate the citywide moe for the number of people w/o college degrees and total pop for years 1 and 2
    #citywide_nocollege_e_1 = moe_alltracts(bates_df, 'nocollege_1')
    citywide_college_e_1 = moe_alltracts(bates_df, 'college_1')
    citywide_pop_edu_e_1 = moe_alltracts(bates_df, pop_edu_1)

    citywide_nocollege_e_2 = moe_alltracts(bates_df, 'nocollege_2')
    citywide_college_e_2 = moe_alltracts(bates_df, 'college_2')
    citywide_pop_edu_e_2 = moe_alltracts(bates_df, pop_edu_2)

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
    df['college_change'] = df['college_p_2'] - df['college_p_1']

    #Calculate the citywide percentage point change from year 1 to year 2 and the moe
    citywide_college_change = citywide_college_p_2 - citywide_college_p_1

    citywide_college_change_e = moe_propagation(citywide_college_moe_1, citywide_college_moe_2)


    ##MEDIAN HOUSEHOLD INCOME##

    #Still need to look into MOE for this calculation

    #adjust year 1 values for inflation
    df['mhi_1_adj'] = cpi.inflate(df[mhi_1], year1, to = year2)

    #Calculate citywide average mfi years 1 and 2
    citywide_meanmhi_1 = df['mhi_1_adj'].mean()
    citywide_meanmhi_2 = df[mhi_2].mean()

    #For each tract, calculate change in mfi from year 1 to year 2
    df['mhi_pchange'] = (df[mhi_2] - df['mhi_1_adj'])/df[mhi_2]

    #Calculate the citywide change in mfi from year 1 to year 2 and the moe
    citywide_mhi_pchange = (citywide_meanmhi_2 - citywide_meanmhi_1)/citywide_meanmhi_2


    ###INDEX 1: VULNERABILITY SCORE###

    #This index will use ACS values from year 2


    ##TENURE##

    #Calculate threshold for proportion of renters
    citywide_renter_threshold = citywide_renter_p_2 - citywide_renter_moe_2

    #Calculate whether the % renters each tract is at or above the citywide median (minus the MOE)
    df['renter_vscore'] = np.where(df['renters_p_2'] >= citywide_renter_threshold, 1, 0)

    ##RACE AND ETHNICITY##

    #Calculate threshold for proportion of poc
    citywide_poc_threshold = citywide_poc_p_2 - citywide_poc_moe_2

    #Calculate whether the % POC of each tract is at above the citywide median (minus MOE)
    df['poc_vscore'] = np.where(df['poc_p_2'] >= citywide_poc_threshold, 1, 0)


    ##EDUCATIONAL ATTAINMENT##

    #Calculate threshold for proportion of people 25+ without college degrees
    citywide_nocollege_threshold = citywide_nocollege_p_2 - citywide_nocollege_moe_2

    #Calculate whether the % 25+ without college deg for each tract is at above the citywide median (minus MOE)

    df['nocollege_vscore'] = np.where(df['nocollege_p_2'] >= citywide_nocollege_threshold, 1, 0)


    ##MFI##

    citywide_meanmfi_2 = df[mfi_2].mean()
    citywide_mfi_threshold = citywide_meanmfi_2 * 0.8 #threshold is 80% of median mfi

    #Caluclate whether the MFI for each tract is at or below 80% of the citywide MFI
    df['mfi_vscore'] = np.where(df[mfi_2] <= citywide_mfi_threshold, 1, 0)


    ##TOTAL VULNERABILITY  SCORE##
    #Calculate score 0-4, weight of 1 for each category and create new column (and/or pandas series)

    df['vulnerability_index'] = df['renter_vscore'] + df['poc_vscore'] + df['nocollege_vscore'] + df['mfi_vscore']


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

    df['income_change'] = np.where(df['mhi_pchange'] > citywide_mhi_pchange, 1, 0) 


    ##SCORE: YES OR NO GENTRIFICATION RELATED DEMOGRAPHIC CHANGE##

    #YES if threshold is met for 3 out of four categories OR if meets threshold for %white and % 25+ with college degree
              

    df['demchange_index'] = np.where((df['tenure_change'] + df['race_change'] +  df['edu_change'] + df['income_change']) >=3, True, np.where((df['race_change'] + df['edu_change']) == 2, True, False ))
    
    
    if inplace == False:
        output = df[['GEO_ID','NAME','renter_vscore', 'poc_vscore', 'nocollege_vscore', 'mfi_vscore', 'vulnerability_index', 'tenure_change', 'race_change', 'edu_change', 'income_change', 'demchange_index']]
    
    else:
        output = df
    
    return output

#%%

###TEST###

newdf = calc_batesfreeman(bates_df, 2010, 2020, 'renters_1', 'owners_1', 'pop_tenure_1', 'renters_2', 'owners_2', 'pop_tenure_2', 'white_nhl_1', 'pop_race_1', 'white_nhl_2', 'pop_race_2', 'ASdegree_m_1', 'ASdegree_f_1', 'BAdegree_m_1', 'BAdegree_f_1', 'MAdegree_m_1', 'MAdegree_f_1', 'profdegree_m_1', 'profdegree_f_1', 'docdegree_m_1', 'docdegree_f_1', 'pop_edu_1', 'ASdegree_m_2', 'ASdegree_f_2', 'BAdegree_m_2', 'BAdegree_f_2', 'MAdegree_m_2', 'MAdegree_f_2', 'profdegree_m_2', 'profdegree_f_2', 'docdegree_m_2', 'docdegree_f_2', 'pop_edu_2', 'mfi_2', 'mhi_1', 'mhi_2', inplace = False)

samedf = calc_batesfreeman(bates_df, 2010, 2020, 'renters_1', 'owners_1', 'pop_tenure_1', 'renters_2', 'owners_2', 'pop_tenure_2', 'white_nhl_1', 'pop_race_1', 'white_nhl_2', 'pop_race_2', 'ASdegree_m_1', 'ASdegree_f_1', 'BAdegree_m_1', 'BAdegree_f_1', 'MAdegree_m_1', 'MAdegree_f_1', 'profdegree_m_1', 'profdegree_f_1', 'docdegree_m_1', 'docdegree_f_1', 'pop_edu_1', 'ASdegree_m_2', 'ASdegree_f_2', 'BAdegree_m_2', 'BAdegree_f_2', 'MAdegree_m_2', 'MAdegree_f_2', 'profdegree_m_2', 'profdegree_f_2', 'docdegree_m_2', 'docdegree_f_2', 'pop_edu_2', 'mfi_2', 'mhi_1', 'mhi_2', inplace = True)


#%%
###INDEX 3: HOUSING MARKET CONDITIONS###

#%%
##2000, 2010, AND 2020 VALUES##
#Calculate quintiles for each year
#For each tract, calculate change in % POC 2010-2020 and if this change is above or below the citywide percentage point change (add or subtact MOE)

#%%
##CHANGE 2000-2010##
#Calculate change in median value for each tract and quintiles
#For each tract, calculate change in % POC 2010-2020 and if this change is above or below the citywide percentage point change (add or subtact MOE)

#%%
##CHANGE 2010-2020##
#Calculate change in median value for each tract and quintiles
#For each tract, calculate change in % POC 2010-2020 and if this change is above or below the citywide percentage point change (add or subtact MOE)

#%%
##CHANGE 2000-2020##
#Calculate change in median value for each tract and quintiles
#For each tract, calculate change in % POC 2010-2020 and if this change is above or below the citywide percentage point change (add or subtact MOE)

#%%
##TYPLOGY##
#Adjacent: low or moderate 2020 value, low or moderate 2000-2010 appreciation, touch boundary of one tract with high 2020 value

#Accelerating: low or moderate 2020 value, high 2000-2010 apprecation

#Appreciated: low or moderate 2000 value, high 2020 value, high 2000-2020 appreciation

#add column fo typology

#%%
###INDEX 4: FREEMAN INDEX###

#%%
##YEAR STRUCTURE BUILT##
#Calculate whether the % housing build in last 20 years in each tract in 2020 is below the citywide median and 40th percentile

#%%
##EDUCATIONAL ATTAINMENT##
#For each tract, calculate change in % 25+ without a college degree 2010-2020 and if this change is above the citywide percentage point change (without subtracting the MOE)

#%%
##HOUSING VALUE##
#Calcuate if median housing values 2010-2020 increased (yes or no)

#%%
##SCORE##
#To be considered gentrifying, tract must meet fufill all categories 

#add column for yes or no for this index

#%%
###EXPORT DF###