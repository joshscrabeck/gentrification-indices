"""
Calculating the Bates (2013) gentrification indices and the Freeman (2005) gentrification index
"""
#%%
import pandas as pd
import os
from functools import reduce
import geopandas as gpd

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
acs_2020_tenure = acs_2020_tenure.rename(columns = {'B25003_001E': 'popten', 'B25003_001M':'popten_e', 'B25003_002E': 'owner', 'B25003_002M':'owner_e', 'B25003_003E': 'renter', 'B25003_003M':'renter_e'})

acs_2020_tenure.dropna(axis='columns', inplace = True)

acs_2020_tenure = acs_2020_tenure[['GEO_ID', 'NAME', 'popten', 'owner', 'renter']]

acs_2010_tenure = acs_2010_tenure.rename(columns = {'B25003_001E': 'popten', 'B25003_001M':'popten_e', 'B25003_002E': 'owner', 'B25003_002M':'owner_e', 'B25003_003E': 'renter', 'B25003_003M':'renter_e'})

acs_2010_tenure.dropna(axis='columns', inplace = True)

acs_2010_tenure = acs_2010_tenure[['GEO_ID', 'NAME', 'popten', 'owner', 'renter']]

#Join by GEO_ID
acs_tenure_merge = acs_2010_tenure.merge(acs_2020_tenure, how = 'inner', on = ['GEO_ID', 'NAME'], suffixes = ('1', '2'))


#%%
##RACE AND ETHNICITY##
#Import ACS_2020_raceeth.csv and ACS_2010_raceeth.csv
acs_2020_raceeth = pd.read_csv('ACS_2020_raceeth.csv', skiprows= [1])
acs_2010_raceeth = pd.read_csv('ACS_2010_raceeth.csv', skiprows= [1]) 

#Rename relevant columns and drop unecessary columns
acs_2010_raceeth = acs_2010_raceeth.rename(columns = {'B03002_001E':'poprac', 'B03002_001M':'poprac_e', 'B03002_003E':'white', 'B03002_003M':'white_e'})

acs_2010_raceeth = acs_2010_raceeth[['GEO_ID', 'NAME', 'poprac', 'white']]

acs_2020_raceeth = acs_2020_raceeth.rename(columns = {'B03002_001E':'poprac', 'B03002_001M':'poprac_e', 'B03002_003E':'white', 'B03002_003M':'white_e'})

acs_2020_raceeth = acs_2020_raceeth[['GEO_ID', 'NAME', 'poprac', 'white']]

#join by GEO_ID
acs_raceeth_merge = acs_2010_raceeth.merge(acs_2020_raceeth, how = 'inner', on = [ 'GEO_ID', 'NAME'], suffixes = ('1', '2'))


#%%
##EDUCATIONAL ATTAINMENT##
#Import ACS_2020_educationbysex.csv and ACS_2010_educationbysex.csv
acs_2020_educationbysex = pd.read_csv('ACS_2020_educationbysex.csv', skiprows= [1])
acs_2010_educationbysex = pd.read_csv('ACS_2010_educationbysex.csv', skiprows= [1]) 

#Rename relevant columns and drop unecessary columns
acs_2020_educationbysex = acs_2020_educationbysex.rename(columns = {'B15002_001E':'popedu', 'B15002_001M':'popedu_e', 'B15002_002E':'popedum', 'B15002_002M':'popedum_e', 'B15002_014E':'ASdegm', 'B15002_014M':'ASdegm_e', 'B15002_015E':'BAdegm', 'B15002_015M':'BAdegm_e', 'B15002_016E':'MAdegm', 'B15002_016M':'MAdegm_e', 'B15002_017E':'prodegm', 'B15002_017M':'prodegm_e', 'B15002_018E':'drdegm', 'B15002_018M': 'drdegm_e','B15002_019E':'popeduf', 'B15002_019M':'popeduf_e', 'B15002_031E':'ASdegf', 'B15002_031M':'ASdegf_e', 'B15002_032E':'BAdegf', 'B15002_032M':'BAdegf_e', 'B15002_033E':'MAdegf', 'B15002_033M':'MAdegf_e', 'B15002_034E':'prodegf', 'B15002_034M':'prodegf_e', 'B15002_035E':'drdegf', 'B15002_035M': 'drdegf_e'})

acs_2020_educationbysex = acs_2020_educationbysex[['GEO_ID', 'NAME', 'popedu','popedum','ASdegm', 'BAdegm', 'MAdegm','prodegm', 'drdegm','popeduf', 'ASdegf',  'BAdegf', 'MAdegf','prodegf', 'drdegf']]

acs_2010_educationbysex = acs_2010_educationbysex.rename(columns = {'B15002_001E':'popedu', 'B15002_001M':'popedu_e', 'B15002_002E':'popedum', 'B15002_002M':'popedum_e', 'B15002_014E':'ASdegm', 'B15002_014M':'ASdegm_e', 'B15002_015E':'BAdegm', 'B15002_015M':'BAdegm_e', 'B15002_016E':'MAdegm', 'B15002_016M':'MAdegm_e', 'B15002_017E':'prodegm', 'B15002_017M':'prodegm_e', 'B15002_018E':'drdegm', 'B15002_018M': 'drdegm_e','B15002_019E':'popeduf', 'B15002_019M':'popeduf_e', 'B15002_031E':'ASdegf', 'B15002_031M':'ASdegf_e', 'B15002_032E':'BAdegf', 'B15002_032M':'BAdegf_e', 'B15002_033E':'MAdegf', 'B15002_033M':'MAdegf_e', 'B15002_034E':'prodegf', 'B15002_034M':'prodegf_e', 'B15002_035E':'drdegf', 'B15002_035M': 'drdegf_e'})

acs_2010_educationbysex = acs_2010_educationbysex[['GEO_ID', 'NAME', 'popedu', 'popedum','popedum_e','ASdegm', 'BAdegm', 'MAdegm', 'prodegm',  'drdegm', 'popeduf',  'ASdegf',  'BAdegf', 'MAdegf', 'prodegf', 'drdegf']]


#Inner join 2010 and 2020
acs_educationbysex_merge = acs_2010_educationbysex.merge(acs_2020_educationbysex, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('1', '2'))


#%%
##MEDIAN FAMILY INCOME##
#Import ACS_2020_MFI.csv and ACS_2010_MFI.csv
acs_2020_mfi = pd.read_csv('ACS_2020_MFI.csv', skiprows= [1])
acs_2010_mfi = pd.read_csv('ACS_2010_MFI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_mfi = acs_2010_mfi.rename(columns = {'B19113_001E':'mfi', 'B19113_001M':'mfi_e'})

acs_2010_mfi = acs_2010_mfi[['GEO_ID', 'NAME', 'mfi']]

acs_2020_mfi = acs_2020_mfi.rename(columns = {'B19113_001E':'mfi', 'B19113_001M':'mfi_e'})

acs_2020_mfi = acs_2020_mfi[['GEO_ID', 'NAME', 'mfi']]

#Inner join 2010 and 2020
acs_mfi_merge = acs_2010_mfi.merge(acs_2020_mfi, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('1', '2'))

acs_mfi_merge['mfi2'] = acs_mfi_merge['mfi2'].str.extract(pat='(\d+)', expand = False)
acs_mfi_merge.dropna(inplace = True)


acs_mfi_merge = acs_mfi_merge[(acs_mfi_merge['mfi2'] != '-') & (acs_mfi_merge['mfi1'] != '-')].astype({'mfi1':'int64', 'mfi2': 'int64'})


#%%
##MEDIAN HOUSEHOLD INCOME##
#Import ACS_2010_MHI.csv
acs_2010_mhi = pd.read_csv('ACS_2010_MHI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_mhi = acs_2010_mhi.rename(columns = {'B19013_001E':'mhi', 'B19013_001M':'mhi_e'})

acs_2010_mhi = acs_2010_mhi[['GEO_ID', 'NAME', 'mhi']]

acs_2010_mhi = acs_2010_mhi[acs_2010_mhi['mhi'] != '-'].astype({'mhi':'int64'})

#Import ACS_2020_MHI.csv
acs_2020_mhi = pd.read_csv('ACS_2020_MHI.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2020_mhi = acs_2020_mhi.rename(columns = {'B19013_001E':'mhi', 'B19013_001M':'mhi_e'})

acs_2020_mhi = acs_2020_mhi[['GEO_ID', 'NAME', 'mhi']]

acs_2020_mhi = acs_2020_mhi[acs_2020_mhi['mhi'] != '-'].astype({'mhi':'int64'})


#Inner join 2010 and 2020
acs_mhi_merge = acs_2010_mhi.merge(acs_2020_mhi, how = 'inner', on = ['GEO_ID','NAME'], suffixes = ('1', '2'))
##ADD TO FUNCTION
#Calculate citywide median and 40th percentile and MOE

#%%
##HOME VALUE##
#Import ACS_2020_housevalue.csv and ACS_2010_housevalue.csv and Census_2000_housevalue.csv
acs_2010_housevalue = pd.read_csv('ACS_2010_housevalue.csv', skiprows= [1]) 

acs_2020_housevalue = pd.read_csv('ACS_2020_housevalue.csv', skiprows= [1]) 

census_2000_housevalue = pd.read_csv('Census_2000_housevalue.csv', skiprows= [1]) 

#Rename relevant columns and drop unnecessary columns
acs_2010_housevalue = acs_2010_housevalue.rename(columns = {'B25077_001E':'mhv1', 'B25077_001M':'mhv_e1'})

acs_2010_housevalue = acs_2010_housevalue[['GEO_ID', 'NAME', 'mhv1']]

acs_2010_housevalue = acs_2010_housevalue[acs_2010_housevalue['mhv1'] != '-']

acs_2010_housevalue = acs_2010_housevalue.astype({'mhv1':'int64'})

acs_2020_housevalue = acs_2020_housevalue.rename(columns = {'B25077_001E':'mhv2', 'B25077_001M':'mhv_e2'})

acs_2020_housevalue = acs_2020_housevalue[['GEO_ID', 'NAME', 'mhv2']]

acs_2020_housevalue = acs_2020_housevalue[acs_2020_housevalue['mhv2'] != '-']

acs_2020_housevalue = acs_2020_housevalue.astype({'mhv2':'int64'})

census_2000_housevalue = census_2000_housevalue.rename(columns = {'H085001':'mhv0'})

census_2000_housevalue = census_2000_housevalue[['GEO_ID', 'NAME', 'mhv0']]

census_2000_housevalue['mhv0']=census_2000_housevalue['mhv0'].str.extract(pat='(\d+)', expand=False)

census_2000_housevalue = census_2000_housevalue.astype({'mhv0':'int64'})

housevalue_merge = census_2000_housevalue.merge(acs_2010_housevalue, how = 'inner', on = ['GEO_ID','NAME']).merge(acs_2020_housevalue, how = 'inner', on = ['GEO_ID', 'NAME'])


##ADD TO FUNCTION
#Calculate quintiles for each year
#calculate change in value deom 2000-2010, 2010-2020, 2000-2020 and quintiles

#%%
##BUILDING AGE##
#Import ACS_2020_yearbuilt.csv
acs_2020_yearbuilt = pd.read_csv('ACS_2020_yearbuilt.csv', skiprows= [1]) 

acs_2020_yearbuilt = acs_2020_yearbuilt.rename(columns ={'B25034_001E':'tothous', 'B25034_001M':'tothous_e', 'B25034_002E':'y14topr', 'B25034_002M':'y14topr_e', 'B25034_003E': 'y10to13', 'B25034_003M':'y10to13_e', })

#Select and rename relevant columns
acs_2020_yearbuilt = acs_2020_yearbuilt[['GEO_ID', 'NAME', 'tothous', 'y14topr',  'y10to13']]

##ADD TO FUNCTION
#caluclate % built in the last 20 years and MOE
#Calculate citywide median and MOE

#merge all into one df
dfs = [acs_tenure_merge, acs_educationbysex_merge, acs_raceeth_merge, acs_mfi_merge, housevalue_merge, acs_mhi_merge, acs_2020_yearbuilt]

bates_df= reduce(lambda  left,right: pd.merge(left,right,on=['GEO_ID','NAME'], how='inner'), dfs)



#merge with TIGER/Line shapefile
boundaries = gpd.read_file('tl_2022_42_tract.shp')
bates_df['GEO_ID'] = bates_df['GEO_ID'].apply(lambda x: x[-11:])

bates_df_shp = boundaries.merge(bates_df, left_on = 'GEOID', right_on = 'GEO_ID', suffixes = ('_x', '_y'))

bates_df_shp.to_file('bates_df_shp.shp')

bates_df.to_csv('bates_df.csv', index = False)

