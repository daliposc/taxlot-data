import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

TLID_URL = "http://gisims.co.washington.or.us/GIS/index.cfm?id=30&sid=3&IDValue={}"

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    fields = {"prop_class":"Property Classification:",
               "taxcode":"Taxcode:",
               "mrkt_land_val":"Market Land Value:",
               "mrkt_bld_val":"Market Bldg Value:",
               "mrkt_special_val":"Special Market Value:",
               "mrkt_tot_val":"Market Total Value:",
               "assessed_val":"Taxable Assessed Value:",
               "legal_desc":"Legal"}
    data = {}
    for field in fields:
        print(field)
        td = soup.find(string=re.compile(fields[field]))
        print(td, ":", td.parent.next_sibling.next_sibling.text)
        data[field] = [td.parent.next_sibling.next_sibling.text]
    df = pd.DataFrame(data)
    return df

def get_webpage(tlid):
    response = requests.get(TLID_URL.format(tlid))
    with open("page.html", 'w') as f:
        f.write(response.text)
    return parse_html(open("page.html", 'r'))

def main():
    df = pd.read_csv("data/taxlots_hillsboro_sql_table_export.csv")
    get_webpage("1N228AA00400")

if __name__ == '__main__':
    main()