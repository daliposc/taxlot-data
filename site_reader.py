## Scrapes the Wash Co site for taxlot data, stores to Pandas dataframe
import pandas as pd
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
import re
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO, StringIO
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract

TLID_ASESSMENT_REPORT_URL = "http://gisims.co.washington.or.us/GIS/index.cfm?id=30&sid=3&IDValue={}"
PROPERTY_TAX_STATEMENT_URL = "https://mtbachelor.co.washington.or.us/Tax2Web/2019-2020/{}.pdf"
FIELDS = {"prop_class":"Property Classification:",
            "code_area":"Taxcode:",
            "mrkt_land_val":"Market Land Value:",
            "mrkt_bld_val":"Market Bldg Value:",
            "mrkt_special_val":"Special Market Value:",
            "mrkt_tot_val":"Market Total Value:",
            "assessed_val":"Taxable Assessed Value:",
            "legal_desc":"Legal:",
            "address":"Site Address:",
            "lot_size":"Lot Size:"}

def empty_dataframe(attr, type):
    data = {}
    if type == 'tlid':
        data['tlid'] = [attr]
        data['property_account_id'] = ['']
        for field in FIELDS:
            data[field] = ['']
    if type == 'prop_account_id':
        data['prop_account_id'] = [attr]
        data['taxes_2018'] = ['']
        data['taxes_2019'] = ['']
    return pd.DataFrame(data)

## Searches and navigates tables cells of Wash Co assessment & taxation report
## Uses BeautifulSoup to search and pull data from tables in the HTML tree 
def get_asessment_report(tlid):
    try:
        response = requests.get(TLID_ASESSMENT_REPORT_URL.format(tlid))
        response.raise_for_status()
    except HTTPError as http_err:
        print("HTTP Error: {}".format(http_err))
        return empty_dataframe(tlid, 'tlid')

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}
    df = pd.DataFrame()
    
    # One Taxlot can have multiple property accounts, so a unique row is created for each property account
    td_prop_accounts = soup.find(string=re.compile("Property Account ID"))
    prop_accounts = re.findall(r'[RMPU]\d*', td_prop_accounts.parent.next_sibling.next_sibling.text)
    if prop_accounts == []:
        prop_accounts = ['']
    
    for i in range(len(prop_accounts)):
        data['tlid'] = tlid
        data['prop_account_id'] = prop_accounts[i-1]
        for field in FIELDS:
            td_attribute = soup.find_all(string=re.compile(FIELDS[field]))[i-1]
            attribute = td_attribute.parent.next_sibling.next_sibling.text
            if field == 'prop_class':
                data[field] = [attribute[:5]]
            elif field == 'lot_size':
                data[field] = float(re.search(r'[0-9]+.[0-9]+', attribute).group(0))
            elif 'val' in field:
                data[field] = int(''.join(re.findall(r'\d', attribute)))
            else:
                data[field] = [attribute]
        df = df.append(pd.DataFrame(data), ignore_index =True)

    return df

## Downloads pdf, crops to an image, analyze with pytesseract, return dataframe
def get_tax_statement(prop_account_id):
    try:
        response = requests.get(PROPERTY_TAX_STATEMENT_URL.format(prop_account_id))
        response.raise_for_status()
    except HTTPError as http_err:
        print("HTTP Error: {}".format(http_err))
        return empty_dataframe(prop_account_id, 'prop_account_id')
    
    
    pagebuffer = BytesIO(response.content)    
    page = PdfFileReader(pagebuffer).getPage(0)
    page.cropBox.lowerLeft = (160, 550)
    page.cropBox.upperRight = (300, 578)
    
    crop = PdfFileWriter()
    crop.addPage(page)
    cropbuffer = BytesIO()
    crop.write(cropbuffer)

    images = convert_from_bytes(cropbuffer.getvalue(), dpi=120, use_cropbox=True)

    tesseract_analysis = pytesseract.image_to_string(images[0], config='--dpi 120')
    taxes = re.findall(r'[$][\w,.]*', tesseract_analysis)

    data = {}
    data['prop_account_id'] = [prop_account_id]
    data['taxes_2018'] = [float(re.search(r'[0-9]+[.][0-9]+', taxes[0].replace(',','')).group(0))]
    data['taxes_2019'] = [float(re.search(r'[0-9]+[.][0-9]+', taxes[1].replace(',','')).group(0))]

    df = pd.DataFrame(data)

    return df


def main():
    #df = get_asessment_report("1S201AB09400")
    df = get_tax_statement('R2145549')
    print(df)
    print(df.dtypes)

if __name__ == '__main__':
    main()