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
from time import sleep
import logging

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

## Returns an empty dataframe
def empty_dataframe(tlid, prop_account_id):
    data = {}
    data['tlid'] = [tlid]
    data['prop_account_id'] = [prop_account_id]
    for field in FIELDS:
        data[field] = ['']
    data['taxes_2018'] = ['']
    data['taxes_2019'] = ['']
    return pd.DataFrame(data)


## Searches and navigates tables cells of Wash Co assessment & taxation report
## Uses BeautifulSoup to search and pull data from tables in the HTML tree 
def get_asessment_report(tlid):
    try:
        sleep(0.1)
        logging.info('Requesting URL.')
        response = requests.get(TLID_ASESSMENT_REPORT_URL.format(tlid),timeout=10)
        response.raise_for_status()
        logging.info('Connected.')
    except HTTPError as e:
        logging.info(e)
        print("HTTP Error: {}".format(e))
        return empty_dataframe(tlid, '')
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
        logging.info('CONNECTION ERROR.')
        print("Connection failed. Sleeping and trying again.")
        connected = False
        i=1
        while connected is False:
            try:
                sleep(i)
                logging.info('Attempting to recconect.')
                response = requests.get(TLID_ASESSMENT_REPORT_URL.format(tlid), timeout=10)
                response.raise_for_status()
                logging.info('Connected.')
                connected = True
            except HTTPError as e:
                logging.info(e)
                print("HTTP Error: {}".format(e))
                return empty_dataframe(tlid, '')
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                logging.info('Connectionn still failed.')
                print("Still refused. Attempts:", i)
                i = i*2

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}
    df = pd.DataFrame()
    
    # One Taxlot can have multiple property accounts, so a unique row is created for each property account
    logging.info('Building data dict...')
    td_prop_accounts = soup.find(string=re.compile("Property Account ID"))
    try:
        logging.info("    Counting prop_account_id's")
        prop_accounts = re.findall(r'[RMPU]\d*', td_prop_accounts.parent.next_sibling.next_sibling.text)
        if prop_accounts == []:
            prop_accounts = ['']
    except AttributeError:
        logging.info('    No prop_account_id. Returning empty dataframe.')
        # example: http://gisims.co.washington.or.us/GIS/index.cfm?id=30&sid=3&IDValue=1N202DA00600
        return empty_dataframe(tlid, '')
    
    for i in range(len(prop_accounts)):
        data['tlid'] = [tlid]
        data['prop_account_id'] = [prop_accounts[i-1]]
        for field in FIELDS:
            logging.info(f'    Parsing: {field}')
            try:
                td_attribute = soup.find_all(string=re.compile(FIELDS[field]))[i-1]
            except IndexError:
                td_attribute = soup.find_all(string=re.compile(FIELDS[field]))[0]
            attribute = td_attribute.parent.next_sibling.next_sibling.text
            try:
                if field == 'prop_class':
                    data[field] = [str(attribute[:4])]
                elif field == 'code_area':
                    data[field] = [str(attribute.replace(' ', ''))]
                elif field == 'lot_size':
                    data[field] = [float(re.search(r'[0-9]+.[0-9]+', attribute).group(0))]
                elif 'val' in field:
                    data[field] = [int(''.join(re.findall(r'\d', attribute)))]
                else:
                    data[field] = [attribute]
            except AttributeError as e:
                logging.info(f'    AttributeError: "{attribute}"')
                data[field] = ['']
        # Image analysis
        logging.info('    Getting tax statement...')
        taxes = get_tax_statement(prop_accounts[i-1], tlid)
        logging.info('    Success.')
        data['taxes_2018'] = [taxes[0]]
        data['taxes_2019'] = [taxes[1]]
        logging.info('    Adding data dict row to dataframe.')
        df = df.append(pd.DataFrame(data), ignore_index =True)

    logging.info('Returning dataframe rows.')
    return df


## Downloads pdf, crops to an image, analyze with pytesseract, return dataframe
def get_tax_statement(prop_account_id, tlid):
    try:
        sleep(0.1)
        logging.info('      Requesting PDF.')
        response = requests.get(PROPERTY_TAX_STATEMENT_URL.format(prop_account_id), timeout=10)
        response.raise_for_status()
        logging.info('      Connected.')
    except HTTPError as e:
        logging.info('      HTTP Error. Returning zeroes.')
        print("HTTP Error: {}".format(e))
        return [0,0]
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
        logging.info(f'      CONNECTION ERROR.')
        print("Connection failed. Sleeping and trying again.")
        connected = False
        i=1
        while connected is False:
            try:
                sleep(i)
                logging.info('      Attempting to recconect.')
                response = requests.get(PROPERTY_TAX_STATEMENT_URL.format(prop_account_id), timeout=10)
                response.raise_for_status()
                logging.info('      Connected.')
                connected = True
            except HTTPError as e:
                logging.info('      HTTP Error. Returning zeroes.')
                print("HTTP Error: {}".format(e))
                return [0,0]
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                logging.info('      Connection still failed.')
                print("Still refused. Attempts:", i)
                i = i*2
    
    if prop_account_id == '':
        return ['','']
    
    logging.info('      Cropping PDF.')
    pagebuffer = BytesIO(response.content)    
    page = PdfFileReader(pagebuffer).getPage(0)
    page.cropBox.lowerLeft = (160, 550)
    page.cropBox.upperRight = (300, 578)
    
    crop = PdfFileWriter()
    crop.addPage(page)
    cropbuffer = BytesIO()
    crop.write(cropbuffer)

    logging.info('      Converting to image.')
    images = convert_from_bytes(cropbuffer.getvalue(), dpi=120, use_cropbox=True)

    logging.info('      Analyzing image.')
    tesseract_analysis = pytesseract.image_to_string(images[0], config='--dpi 120')
    taxes = re.findall(r'[$][\w,.]*', tesseract_analysis)

    # data = {}
    # data['prop_account_id'] = [prop_account_id]
    # data['taxes_2018'] = [float(re.search(r'[0-9]+[.][0-9]+', taxes[0].replace(',','')).group(0))]
    # data['taxes_2019'] = [float(re.search(r'[0-9]+[.][0-9]+', taxes[1].replace(',','')).group(0))]

    # df = pd.DataFrame(data)
    logging.info('      Formatting tax_values.')
    tax_values = [float(re.search(r'[0-9]+[.][0-9]+', taxes[0].replace(',','')).group(0)), float(re.search(r'[0-9]+[.][0-9]+', taxes[1].replace(',','')).group(0))]
    
    return tax_values

def main():
    #df = get_asessment_report("1S201AB09400")
    df = get_tax_statement('R2145549')
    print(df)
    print(df.dtypes)

if __name__ == '__main__':
    main()