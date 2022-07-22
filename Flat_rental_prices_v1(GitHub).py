# # Flat rental prices in Poland
# ### 1.Libraries
import pandas as pd
from datetime import datetime
import sys
import numpy as np
# ### 2.Set options
pd.reset_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# ### 3. WebScraping through API (json)
df=pd.DataFrame(columns=['id',
                         'location.city.name',
                         'location.city.normalized_name',
                         'location.district.name',
                         'location.region.name', 
                         'location.region.normalized_name', 
                         'title',
                         'price',
                         'currency',
                         'floor_select',
                         'furniture',
                         'builttype',
                         'm',
                         'rooms',
                         'rent'
                        ])
#Looping in regions
iCounter = 1
for idRegion in range(0,18):
    if idRegion==10 or idRegion==16:
        continue
    
    print('Downloading %i out of 16' % iCounter)
    # Looping in pages
    jCounter = 0
    for iPage in range(0,1050,50):
        #print(iPage)

        url='https://www.olx.pl/api/v1/offers/?offset=' + str(iPage) + \
            '&limit=49&category_id=15&region_id='+ str(idRegion) + \
            '&filter_refiners=&sl=178c8097095x771d8544'

        json=pd.read_json(
            url,
            orient='records',
            typ='series'
        )['data']
        
        try:
            if json == []:
                continue
            
            df_temp=pd.json_normalize(
                json)[['id', 
                       'location.city.name',
                       'location.city.normalized_name',
                       'location.district.name',
                       'location.region.name', 
                       'location.region.normalized_name', 
                       'title']]
        except KeyError as err:

            df_temp=pd.json_normalize(
                json)[['id', 
                       'location.city.name',
                       'location.city.normalized_name',
                       'location.region.name', 
                       'location.region.normalized_name', 
                       'title']]
            df_temp['location.district.name'] = np.nan
            jCounter += 1
        except:
            print('Error: ', sys.exc_info()[0])
        
        json2=pd.json_normalize(
            json,
            'params'
        )

        df_temp['price'] = json2.loc[json2.key == 'price', 'value.value'].reset_index(drop=True) #Money for owner
        df_temp['currency'] = json2.loc[json2.key == 'price', 'value.currency'].reset_index(drop=True) #Money for owner
        df_temp['floor_select'] = json2.loc[json2.key == 'floor_select', 'value.label'].reset_index(drop=True) #Floor number
        df_temp['furniture'] = json2.loc[json2.key == 'furniture', 'value.key'].reset_index(drop=True) #Furniture
        df_temp['builttype'] = json2.loc[json2.key == 'builttype', 'value.key'].reset_index(drop=True) #Builttype
        df_temp['m'] = json2.loc[json2.key == 'm', 'value.key'].reset_index(drop=True) #Surface
        df_temp['rooms'] = json2.loc[json2.key == 'rooms','value.key'].reset_index(drop=True) #Number of rooms (text, four == four or more)
        df_temp['rent'] = json2.loc[json2.key == 'rent', 'value.key'].reset_index(drop=True) #Rental (additionally paid)

        df=pd.concat([df,df_temp], ignore_index = True)
        
    print("\tDownloaded offers:", df.count()['id'])
    print("\tMissing districts in current region:", jCounter)
    iCounter += 1

df = df.drop_duplicates()
print('Data downloaded. Saving dataset')
filename = datetime.now().strftime('%Y') + '_flat_rental.csv'
df.to_csv(filename)
print('Process finished')
input('Press any key to close this window...')

