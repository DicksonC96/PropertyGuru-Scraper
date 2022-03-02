from bs4 import BeautifulSoup
import time
from datetime import date
import cloudscraper
import numpy as np
import pandas as pd

### Section 1:Query Selection ###
# Initialize your Query selection here:
MARKET = 'residential'
TYPE = 'condo'
STATE = 'kl'

# Initialize filenames (leave empty if not generating):
PROPERTY_LIST = ''
RAW_DATA = ''
ANALYZED_DATA = './data/{}-{}-{}.csv'.format(TYPE,STATE,date.today().strftime("%b%Y"))

### CODE STARTS FROM HERE ###

property_type = {'all':'',
        'bungalow':'&property_type_code%5B%5D=BUNG&property_type_code%5B%5D=LBUNG&property_type_code%5B%5D=ZBUNG&property_type_code%5B%5D=TWINV&property_type_code%5B%5D=TWINC&property_type=B',
        'condo':'&property_type_code%5B%5D=CONDO&property_type_code%5B%5D=APT&property_type_code%5B%5D=FLAT&property_type_code%5B%5D=PENT&property_type_code%5B%5D=SRES&property_type_code%5B%5D=STDIO&property_type_code%5B%5D=DUPLX&property_type_code%5B%5D=TOWNC&property_type=N',
        'semid':'&property_type_code%5B%5D=SEMI&property_type_code%5B%5D=CLUS&property_type=S',
        'terrace':'&property_type_code%5B%5D=TERRA&property_type_code%5B%5D=TOWN&property_type_code%5B%5D=TER1&property_type_code%5B%5D=TER15&property_type_code%5B%5D=TER2&property_type_code%5B%5D=TER25&property_type_code%5B%5D=TER3&property_type_code%5B%5D=TER35&property_type=T',
        'land':'&property_type_code%5B%5D=RLAND&property_type=L'}

state = {'all':'',
        'johor':'&region_code=MY01',
        'kedah':'&region_code=MY02',
        'kelantan':'&region_code=MY03',
        'melaka':'&region_code=MY04',
        'ns':'&region_code=MY05',
        'pahang':'&region_code=MY06',
        'penang':'&region_code=MY07',
        'perak':'&region_code=MY08',
        'perlis':'&region_code=MY09',
        'selangor':'&region_code=MY10',
        'terengganu':'&region_code=MY11',
        'sabah':'&region_code=MY12',
        'sarawak':'&region_code=MY13',
        'kl':'&region_code=MY14',
        'labuan':'&region_code=MY15',
        'putrajaya':'&region_code=MY16',
        'other':'&region_code=MY99'}

def BS_Prep(URL):
    trial = 0
    while trial < 10:
        scraper = cloudscraper.create_scraper()
        s = scraper.get(URL)
        soup = BeautifulSoup(s.content, 'html.parser')
        if "captcha" in soup.text:
            trial += 1
            print('Retrying ('+str(trial)+'/10) ...')
            time.sleep(0.1)
            continue
        elif "No Results" in soup.text:
            print('Invalid URL, skipping '+URL)
            trial = 99
        else:
            trial = 99
    if trial == 10:
        print('Trial exceeded, skipping '+URL)
    return soup
        
def Pagination(soup):
    wrapper = soup.find(id="wrapper-inner")
    pagination = wrapper.find("ul", class_="pagination")
    if pagination.find_all("li", class_="pagination-next disabled"):
        pages = int(pagination.find_all("a")[0]['data-page'])
    else:
        pages = int(pagination.find_all("a")[-2]['data-page'])
    return pages

def Listing_Link_Scraper(soup):
    links = []
    units = soup.find_all("div", itemtype="https://schema.org/Place")
    for unit in units:
        if unit.find("a", class_="btn btn-primary-outline units_for_sale disabled") or unit.find("a", class_="btn btn-primary-outline units_for_rent disabled"):
            continue
        prop = unit.find("a", class_="nav-link")
        links.append((prop['title'],HEADER+prop["href"]))
    return(links)

def Listing_Price_Scrapper(prop):
    pname, plink= prop
    error_counter = 0
    sale_soup = BS_Prep(plink.replace('/condo/', '/property-for-sale/at-')+'?limit=500')
    sale_list = []
    for s in sale_soup.find_all("span", class_="price"):
        try:
            sale_list.append(float(s.text.split(' ')[-1].replace(',','').strip()))
        except:
            sale_list.append(np.nan)
            error_counter += 1
    rent_soup = BS_Prep(plink.replace('/condo/', '/property-for-rent/at-')+'?limit=500')
    rent_list = []
    for r in rent_soup.find_all("span", class_="price"):
        try:
            rent_list.append(float(r.text.split(' ')[0].replace(',','').strip()))
        except:
            rent_list.append(np.nan)
            error_counter += 1
    return [pname, np.nanmean(sale_list), np.nanmedian(sale_list), np.nanmean(rent_list), np.nanmedian(rent_list), len(sale_list), len(rent_list), error_counter, plink]

# Initialize URL
HEADER = 'https://www.propertyguru.com.my'
KEY = '/condo/search-project'
QUERY = '?limit=500&market='+MARKET+property_type[TYPE]+state[STATE]+'&newProject=all'

# Load first page with Query and scrape no. of pages
print('\n===================================================\nPropertyGuru Property Listing Scraper v1.0\nAuthor: DicksonC\n===================================================\n')
time.sleep(2)
print('Job initiated with query on {} in {}.'.format(TYPE, STATE))
print('\nLoading '+HEADER+KEY+QUERY+' ...\n')
soup = BS_Prep(HEADER+KEY+QUERY)
pages = Pagination(soup)
print(str(pages)+' page will be scrapped.\n')

# Scrape links from first page for properties with both sale and rental listing
props = []
props += Listing_Link_Scraper(soup)
print('\rPage 1/{} done.'.format(str(pages)))

# Scrape subsequent pages
for page in range(2, pages+1):
    soup = BS_Prep(HEADER+KEY+'/'+str(page)+QUERY)
    props += Listing_Link_Scraper(soup)
    print('\rPage {}/{} done.'.format(str(page), str(pages)))

if PROPERTY_LIST:
    list_df = pd.DataFrame(props, columns=['PropertyName', 'URL'])
    list_df.to_csv(PROPERTY_LIST, index=False)
    print('\nProperty list saved to {}'.format(PROPERTY_LIST))

# Scrape prices for sale and rental of each properties
data = []
print('\nA total of '+str(len(props))+' properties will be scraped.\n')
for i, prop in enumerate(props):
    p = Listing_Price_Scrapper(prop)
    print(str(i+1)+'/'+str(len(props))+' done!')
    data.append(p)

# Result into DataFrame and Analysis
df = pd.DataFrame(data, columns=['PropertyName','MeanSale','MedianSale','MeanRental','MedianRental','NSale','NRental','NError','URL'])
if RAW_DATA:
    df.to_csv(RAW_DATA, index=False)
    print('Raw data saved to {}'.format(RAW_DATA))

df.dropna(inplace=True)
#df.insert(5, 'Mean%Coverage', df.MeanRental*100/df.MeanSale/100000*404)
df.insert(5, '%toBreakEven', df.MedianRental*100/df.MedianSale*100000/404)

# Data save to file
df.to_csv(ANALYZED_DATA, index=False)
print('Analyzed data saved to {}\n\nDone scraping {} properties!'.format(ANALYZED_DATA,str(len(props))))