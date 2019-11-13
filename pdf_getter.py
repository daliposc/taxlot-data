# try: [parcel].pdf  download
#   - Note: no leading zeroes, R0703625 -> R703625
#   - https://mtbachelor.co.washington.or.us/Tax2Web/2019-2020/[parcel].pdf
# except: taxlot id webpage, download R-number.pdf
#   - http://gisims.co.washington.or.us/GIS/index.cfm?id=30&sid=3&IDValue=[tlid]

import pandas as ps
import numpy
import urllib.request
import urllib.error
import sys

def make_parcel_url(parcel):
    if type(parcel) is str:
        n = 1
        while parcel[n] == '0':
            n += 1
        parcel = 'R{}'.format(parcel[n:])
    else:
        parcel='NaN'
    return "https://mtbachelor.co.washington.or.us/Tax2Web/2019-2020/{}.pdf".format(parcel)

df = ps.read_csv("/home/connor/Documents/data/geospatial/metro/taxlots_hillsboro_sql_table_export.csv")
parcel_url_column = []

for index, row in df.iterrows():
    parcel_url_column.append(make_parcel_url(row['parcel']))

df['parcel_url'] = parcel_url_column

i = 0
while i < 100:
    try:
        if type(df.loc[i].parcel) is str:
            print(df.loc[i].parcel_url)
            response = urllib.request.urlopen(df.loc[i].parcel_url)
            with open("{}.pdf".format(df.loc[i].parcel), mode='wb') as pdf:
                pdf.write(response.read())
            print("....PDF downloaded!!!")
        else:
            print(i, " .. No parcel number.")
    except urllib.error.HTTPError as e:
        print(e)
    i += 1
