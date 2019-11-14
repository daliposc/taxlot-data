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

# Remove leading zeroes in Metro R-Number to match Wash Co formatting
# e.g. R0090737 -> R90737
def fix_parcel_num(parcel):
    if type(parcel) is str:
        n = 1
        while parcel[n] == '0':
            n += 1
        parcel = 'R{}'.format(parcel[n:])
    else:
        parcel='NaN'
    return parcel

# Download n number of property tax pdfs from Wash Co
# Returns 3 lists: no_num (tlid), not_found (parcel), downloaded (parcel)  
def get_n_pdfs(n, df):
    no_num = []
    not_found = []
    downloaded = []
    downloads = 0
    i = 0
    while downloads < n:
        try:
            if type(df.loc[i].parcel) is str:
                print(df.loc[i].parcel_url)
                response = urllib.request.urlopen(df.loc[i].parcel_url)
                with open("pdf/{}.pdf".format(df.loc[i].parcel), mode='wb') as pdf:
                    pdf.write(response.read())
                downloaded.append(df.loc[i].parcel)
                downloads += 1
                print("....PDF downloaded!!!")
            else:
                no_num.append(df.loc[i].tlid)
                print(i, " -- No parcel number.")
        except urllib.error.HTTPError as e:
            not_found.append(df.loc[i].parcel)
            print(e)
        i += 1
    return no_num, not_found, downloaded

def csv_to_formatted_df(uri):
    df = ps.read_csv(uri)
    parcel_url_column = []
    for index, row in df.iterrows():
        parcel_url_column.append("https://mtbachelor.co.washington.or.us/Tax2Web/2019-2020/{}.pdf".format(fix_parcel_num(row['parcel'])))
    df['parcel_url'] = parcel_url_column
    return df

df = csv_to_formatted_df("data/taxlots_hillsboro_sql_table_export.csv")
no_num, not_found, downloaded = get_n_pdfs(10, df)
print("No parcel number: ", len(no_num),"\nHTTP 404: ", len(not_found), "\nDownloaded: ", len(downloaded))
