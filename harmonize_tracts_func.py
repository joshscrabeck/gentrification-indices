

import pandas as pd
import os
from tobler.area_weighted import area_interpolate
import geopandas as gpd

os.chdir('/Users/wc555/gus8066/gentrification-indices/bates-freeman-data')



#%%

##Create test dfs##

#Import ACS_2020_tenure.csv and ACS_2010_tenure.csv
acs_2020_tenure = pd.read_csv('ACS_2020_tenure.csv', skiprows= [1]) #skip row with column descriptions
acs_2010_tenure = pd.read_csv('ACS_2010_tenure.csv', skiprows= [1]) 
shp10 = gpd.read_file('/Users/wc555/gus8066/tl_2010_42101_tract10.shp').to_crs('epsg:6565')
shp20 = gpd.read_file('tl_2022_42_tract.shp').to_crs('epsg:6565')
shp20 = shp20[shp20['COUNTYFP'] == '101']

#Rename relevant columns and drop unecessary columns
acs_2020_tenure = acs_2020_tenure.rename(columns = {'B25003_001E': 'popten', 'B25003_001M':'popten_e', 'B25003_002E': 'owner', 'B25003_002M':'owner_e', 'B25003_003E': 'renter', 'B25003_003M':'renter_e'})
acs_2020_tenure.dropna(axis='columns', inplace = True)
acs_2020_tenure = acs_2020_tenure[['GEO_ID', 'NAME', 'popten', 'owner', 'renter']]
acs_2020_tenure['GEO_ID'] = acs_2020_tenure['GEO_ID'].apply(lambda x: x[-11:])
shp_merge_2020 = shp20.merge(acs_2020_tenure, left_on = 'GEOID', right_on = 'GEO_ID', suffixes = ('_x', '_y'))


acs_2010_tenure = acs_2010_tenure.rename(columns = {'B25003_001E': 'popten', 'B25003_001M':'popten_e', 'B25003_002E': 'owner', 'B25003_002M':'owner_e', 'B25003_003E': 'renter', 'B25003_003M':'renter_e'})
acs_2010_tenure.dropna(axis='columns', inplace = True)
acs_2010_tenure = acs_2010_tenure[['GEO_ID', 'NAME', 'popten', 'owner', 'renter']]
acs_2010_tenure['GEO_ID'] = acs_2010_tenure['GEO_ID'].apply(lambda x: x[-11:])
shp_merge_2010 = shp10.merge(acs_2010_tenure, left_on = 'GEOID10', right_on = 'GEO_ID', suffixes = ('_x', '_y'))


#%%
def harmonize_tracts(input_df, target_df, extensive_variables = None, intensive_variables = None):
    interpolated_columns = area_interpolate(input_df, target_df, extensive_variables = extensive_variables, intensive_variables = intensive_variables)
    output = interpolated_columns.sjoin(target_df, predicate = 'within', lsuffix = '_1', rsuffix='_2')
    output.drop(list(output.filter(regex = 'index')), axis = 1, inplace = True)
    return output

#%%

testdf = harmonize_tracts(shp_merge_2010, shp_merge_2020, extensive_variables= ['popten', 'owner', 'renter'])
