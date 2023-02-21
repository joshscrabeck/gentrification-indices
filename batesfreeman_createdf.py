"""
Calculating the Bates (2013) gentrification indices and the Freeman (2005) gentrification index
"""
#%%
import pandas as pd
import os
from functools import reduce

os.chdir('/Users/winncostantini/gus8066/gentrification-indices/bates-freeman-data')


###DATA CLEANING###

##Functions##
#MOE calculation

#%%
##TENURE##
#Import ACS_2020_tenure.csv and ACS_2010_tenure.csv
acs_2020_tenure = pd.read_csv('ACS_2020_tenure.csv', skiprows= [1]) #skip row with column descriptions
acs_2010_tenure = pd.read_csv('ACS_2010_tenure.csv', skiprows= [1]) 


#Rename relevant columns and drop unecessary columns
acs_2020_tenure = acs_2020_tenure.rename(columns = {'B25003_001E': 'pop_tenure', 'B25003_001M':'pop_tenure_e', 'B25003_002E': 'owners', 'B25003_002M':'owners_e', 'B25003_003E': 'renters', 'B25003_003M':'renters_e'})

acs_2020_tenure.dropna(axis='columns', inplace = True)

acs_2010_tenure = acs_2010_tenure.rename(columns = {'B25003_001E': 'pop_tenure', 'B25003_001M':'pop_tenure_e', 'B25003_002E': 'owners', 'B25003_002M':'owners_e', 'B25003_003E': 'renters', 'B25003_003M':'renters_e'})

acs_2010_tenure.dropna(axis='columns', inplace = True)

#Join by GEO_ID
acs_tenure_merge = acs_2010_tenure.merge(acs_2020_tenure, how = 'inner', on = ['GEO_ID', 'NAME'], suffixes = ('_1', '_2'))


#%%
##RACE AND ETHNICITY##
#Import ACS_2020_raceeth.csv and ACS_2010_raceeth.csv
acs_2020_raceeth = pd.read_csv('ACS_2020_raceeth.csv', skiprows= [1])
acs_2010_raceeth = pd.read_csv('ACS_2010_raceeth.csv', skiprows= [1]) 

#Rename relevant columns and drop unecessary columns
acs_2010_raceeth = acs_2010_raceeth.rename(columns = {'B03002_001E':'pop_race', 'B03002_001M':'pop_race_e', 'B03002_003E':'white_nhl', 'B03002_003M':'white_nhl_e'})

acs_2010_raceeth = acs_2010_raceeth[['GEO_ID', 'NAME', 'pop_race', 'pop_race_e', 'white_nhl', 'white_nhl_e']]

acs_2020_raceeth = acs_2020_raceeth.rename(columns = {'B03002_001E':'pop_race', 'B03002_001M':'pop_race_e', 'B03002_003E':'white_nhl', 'B03002_003M':'white_nhl_e'})

acs_2020_raceeth = acs_2020_raceeth[['GEO_ID', 'NAME', 'pop_race', 'pop_race_e', 'white_nhl', 'white_nhl_e']]

#join by GEO_ID
acs_raceeth_merge = acs_2010_raceeth.merge(acs_2020_raceeth, how = 'inner', on = [ 'GEO_ID', 'NAME'], suffixes = ('_1', '_2'))


#%%
##EDUCATIONAL ATTAINMENT##
#Import ACS_2020_educationbysex.csv and ACS_2010_educationbysex.csv
acs_2020_educationbysex = pd.read_csv('ACS_2020_educationbysex.csv', skiprows= [1])
acs_2010_educationbysex = pd.read_csv('ACS_2010_educationbysex.csv', skiprows= [1]) 

#Rename relevant columns and drop unecessary columns
acs_2020_educationbysex = acs_2020_educationbysex.rename(columns = {'B15002_001E':'pop_edu', 'B15002_001M':'pop_edu_e', 'B15002_002E':'pop_edu_m', 'B15002_002M':'pop_edu_m_e', 'B15002_014E':'ASdegree_m', 'B15002_014M':'ASdegree_m_e', 'B15002_015E':'BAdegree_m', 'B15002_015M':'BAdegree_m_e', 'B15002_016E':'MAdegree_m', 'B15002_016M':'MAdegree_m_e', 'B15002_017E':'profdegree_m', 'B15002_017M':'profdegree_m_e', 'B15002_018E':'docdegree_m', 'B15002_018M': 'docdegree_m_e','B15002_019E':'pop_edu_f', 'B15002_019M':'pop_edu_f_e', 'B15002_031E':'ASdegree_f', 'B15002_031M':'ASdegree_f_e', 'B15002_032E':'BAdegree_f', 'B15002_032M':'BAdegree_f_e', 'B15002_033E':'MAdegree_f', 'B15002_033M':'MAdegree_f_e', 'B15002_034E':'profdegree_f', 'B15002_034M':'profdegree_f_e', 'B15002_035E':'docdegree_f', 'B15002_035M': 'docdegree_f_e'})

acs_2020_educationbysex = acs_2020_educationbysex[['GEO_ID', 'NAME', 'pop_edu','pop_edu_e','pop_edu_m','pop_edu_m_e','ASdegree_m', 'ASdegree_m_e', 'BAdegree_m', 'BAdegree_m_e','MAdegree_m', 'MAdegree_m_e', 'profdegree_m', 'profdegree_m_e', 'docdegree_m', 'docdegree_m_e','pop_edu_f', 'pop_edu_f_e', 'ASdegree_f', 'ASdegree_f_e', 'BAdegree_f', 'BAdegree_f_e','MAdegree_f', 'MAdegree_f_e', 'profdegree_f', 'profdegree_f_e','docdegree_f', 'docdegree_f_e']]

acs_2010_educationbysex = acs_2010_educationbysex.rename(columns = {'B15002_001E':'pop_edu', 'B15002_001M':'pop_edu_e', 'B15002_002E':'pop_edu_m', 'B15002_002M':'pop_edu_m_e', 'B15002_014E':'ASdegree_m', 'B15002_014M':'ASdegree_m_e', 'B15002_015E':'BAdegree_m', 'B15002_015M':'BAdegree_m_e', 'B15002_016E':'MAdegree_m', 'B15002_016M':'MAdegree_m_e', 'B15002_017E':'profdegree_m', 'B15002_017M':'profdegree_m_e', 'B15002_018E':'docdegree_m', 'B15002_018M': 'docdegree_m_e','B15002_019E':'pop_edu_f', 'B15002_019M':'pop_edu_f_e', 'B15002_031E':'ASdegree_f', 'B15002_031M':'ASdegree_f_e', 'B15002_032E':'BAdegree_f', 'B15002_032M':'BAdegree_f_e', 'B15002_033E':'MAdegree_f', 'B15002_033M':'MAdegree_f_e', 'B15002_034E':'profdegree_f', 'B15002_034M':'profdegree_f_e', 'B15002_035E':'docdegree_f', 'B15002_035M': 'docdegree_f_e'})

acs_2010_educationbysex = acs_2010_educationbysex[['GEO_ID', 'NAME', 'pop_edu','pop_edu_e','pop_edu_m','pop_edu_m_e','ASdegree_m', 'ASdegree_m_e', 'BAdegree_m', 'BAdegree_m_e','MAdegree_m', 'MAdegree_m_e', 'profdegree_m', 'profdegree_m_e', 'docdegree_m', 'docdegree_m_e','pop_edu_f', 'pop_edu_f_e', 'ASdegree_f', 'ASdegree_f_e', 'BAdegree_f', 'BAdegree_f_e','MAdegree_f', 'MAdegree_f_e', 'profdegree_f', 'profdegree_f_e','docdegree_f', 'docdegree_f_e']]

#Inner join 2010 and 2020
acs_educationbysex_merge = acs_2010_educationbysex.merge(acs_2020_educationbysex, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('_1', '_2'))


#%%
##MEDIAN FAMILY INCOME##
#Import ACS_2020_MFI.csv and ACS_2010_MFI.csv
acs_2020_mfi = pd.read_csv('ACS_2020_MFI.csv', skiprows= [1])
acs_2010_mfi = pd.read_csv('ACS_2010_MFI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_mfi = acs_2010_mfi.rename(columns = {'B19113_001E':'mfi', 'B19113_001M':'mfi_e'})

acs_2010_mfi = acs_2010_mfi[['GEO_ID', 'NAME', 'mfi', 'mfi_e']]

acs_2020_mfi = acs_2020_mfi.rename(columns = {'B19113_001E':'mfi', 'B19113_001M':'mfi_e'})

acs_2020_mfi = acs_2020_mfi[['GEO_ID', 'NAME', 'mfi', 'mfi_e']]

#Inner join 2010 and 2020
acs_mfi_merge = acs_2010_mfi.merge(acs_2020_mfi, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('_1', '_2'))

acs_mfi_merge = acs_mfi_merge[(acs_mfi_merge['mfi_2'] != '-') & (acs_mfi_merge['mfi_1'] != '-') & (acs_mfi_merge['mfi_e_2'] != '***')].astype({'mfi_1':'int64', 'mfi_e_1': 'int64', 'mfi_2': 'int64', 'mfi_e_2':'int64'})


#%%
##MEDIAN HOUSEHOLD INCOME##
#Import ACS_2010_MHI.csv
acs_2010_mhi = pd.read_csv('ACS_2010_MHI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_mhi = acs_2010_mhi.rename(columns = {'B19013_001E':'mhi', 'B19013_001M':'mhi_e'})

acs_2010_mhi = acs_2010_mhi[['GEO_ID', 'NAME', 'mhi', 'mhi_e']]

acs_2010_mhi = acs_2010_mhi[acs_2010_mhi['mhi'] != '-'].astype({'mhi':'int64', 'mhi_e':'int64'})

#Import ACS_2020_MHI.csv
acs_2020_mhi = pd.read_csv('ACS_2020_MHI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2020_mhi = acs_2020_mhi.rename(columns = {'B19013_001E':'mhi', 'B19013_001M':'mhi_e'})

acs_2020_mhi = acs_2020_mhi[['GEO_ID', 'NAME', 'mhi', 'mhi_e']]

acs_2020_mhi = acs_2020_mhi[acs_2020_mhi['mhi'] != '-'].astype({'mhi':'int64', 'mhi_e':'int64'})


#Inner join 2010 and 2020
acs_mhi_merge = acs_2010_mhi.merge(acs_2020_mhi, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('_1', '_2'))
##ADD TO FUNCTION
#Calculate citywide median and 40th percentile and MOE

#%%
##HOME VALUE##
#Import ACS_2020_housevalue.csv and ACS_2010_housevalue.csv and Census_2000_housevalue.csv
acs_2010_housevalue = pd.read_csv('ACS_2010_housevalue.csv', skiprows= [1]) 

acs_2020_housevalue = pd.read_csv('ACS_2020_housevalue.csv', skiprows= [1]) 

census_2000_housevalue = pd.read_csv('Census_2000_housevalue.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_housevalue = acs_2010_housevalue.rename(columns = {'B25077_001E':'medhousevalue_1', 'B25077_001M':'medhousevalue_e_1'})

acs_2010_housevalue = acs_2010_housevalue[['GEO_ID', 'NAME', 'medhousevalue_1', 'medhousevalue_e_1']]

acs_2010_housevalue = acs_2010_housevalue[acs_2010_housevalue['medhousevalue_1'] != '-']

acs_2010_housevalue = acs_2010_housevalue.astype({'medhousevalue_1':'int64', 'medhousevalue_e_1':'int64'})

acs_2020_housevalue = acs_2020_housevalue.rename(columns = {'B25077_001E':'medhousevalue_2', 'B25077_001M':'medhousevalue_e_2'})

acs_2020_housevalue = acs_2020_housevalue[['GEO_ID', 'NAME', 'medhousevalue_2', 'medhousevalue_e_2']]

acs_2020_housevalue = acs_2020_housevalue[acs_2020_housevalue['medhousevalue_2'] != '-']

acs_2020_housevalue = acs_2020_housevalue.astype({'medhousevalue_2':'int64', 'medhousevalue_e_2':'int64'})

census_2000_housevalue = census_2000_housevalue.rename(columns = {'H085001':'medhousevalue_0'})

census_2000_housevalue = census_2000_housevalue[['GEO_ID', 'NAME', 'medhousevalue_0']]

census_2000_housevalue['medhousevalue_0']=census_2000_housevalue['medhousevalue_0'].str.extract(pat='(\d+)', expand=False)

census_2000_housevalue = census_2000_housevalue.astype({'medhousevalue_0':'int64'})

housevalue_merge = census_2000_housevalue.merge(acs_2010_housevalue, how = 'inner', on = ['GEO_ID','NAME']).merge(acs_2020_housevalue, how = 'inner', on = ['GEO_ID', 'NAME'])


##ADD TO FUNCTION
#Calculate quintiles for each year
#calculate change in value deom 2000-2010, 2010-2020, 2000-2020 and quintiles

#%%
##BUILDING AGE##
#Import ACS_2020_yearbuilt.csv
acs_2020_yearbuilt = pd.read_csv('ACS_2020_yearbuilt.csv', skiprows= [1]) 

acs_2020_yearbuilt = acs_2020_yearbuilt.rename(columns ={'B25034_001E':'tot_houses', 'B25034_001M':'tot_houses_e', 'B25034_002E':'2014orlater', 'B25034_002M':'2014orlater_e', 'B25034_003E': '2010to2013', 'B25034_003M':'2010to2013_e', })

#Select and rename relevant columns
acs_2020_yearbuilt = acs_2020_yearbuilt[['GEO_ID', 'NAME', 'tot_houses', 'tot_houses_e', '2014orlater', '2014orlater_e', '2010to2013', '2010to2013_e']]

##ADD TO FUNCTION
#caluclate % built in the last 20 years and MOE
#Calculate citywide median and MOE

#merge all into one df
dfs = [acs_tenure_merge, acs_educationbysex_merge, acs_raceeth_merge, acs_mfi_merge, housevalue_merge, acs_mhi_merge, acs_2020_yearbuilt]

bates_df= reduce(lambda  left,right: pd.merge(left,right,on=['GEO_ID','NAME'], how='inner'), dfs)

bates_df.to_csv('bates_df.csv')

