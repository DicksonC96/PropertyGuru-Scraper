from bs4 import BeautifulSoup
import time
import cloudscraper
import numpy as np
import pandas as pd

'''
##PropertyGuru project query filter format:

MARKET (required):
residential
commercial

PROPERTY_TYPE:
all
bungalow(Bungalow / Villa)
condo(Apartment / Condo / Service Residence)
semid(Semi-Detached House)
terrace(Terrace / Link House)
land(Residential Land)

STATE:
johor, kedah, kelantan, melaka, ns, pahang, penang, perak, perlis, selangor, terengganu,
sabah, sarawak, kl, labuan, putrajaya, other

##Script limitations:
1. Only those properties with both sale and rental listed will be selected.
2. Gross Loan Repayment Rate are pre-calculated as: RM404 monthly /RM100k selling price (90% loan, 3.5% IR, 30yrs)
3. Rarely rental price will produce NaN failed to be scraped (will be fixed soon)

'''
# Initialize your Query selection here:
MARKET = 'residential'
TYPE = 'condo'
STATE = 'penang'
FILE_NAME = 'example-output.csv'

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
            print('Retrying ('+str(trial)+'/10)...')
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

def Link_Scraper(soup, with_price):
    wrapper = soup.find(id="wrapper-inner")
    projects = wrapper.find_all("div", itemtype="https://schema.org/Place")
    links = []
    for project in projects:
        if with_price==1:
            if not project.find("span", class_="list-price__start"):
                continue
        info = project.find("a", class_="nav-link")
        link = info["href"]
        links.append(link)
    return links
        
def Pagination(soup):
    wrapper = soup.find(id="wrapper-inner")
    pagination = wrapper.find("ul", class_="pagination")
    if pagination.find_all("li", class_="pagination-next disabled"):
        pages = int(pagination.find_all("a")[0]['data-page'])
        print(str(pages)+' page will be scrapped.')
    else:
        pages = int(pagination.find_all("a")[-2]['data-page'])
        print(str(pages)+' pages will be scrapped.')
    return pages

def Property_Scraper(soup, link):
    propname = soup.find("h1", class_="h2 text-transform-none").text.strip()
    minsale = soup.find("span", class_="element-label price", itemprop="lowPrice")
    maxsale = soup.find("span", class_="element-label price", itemprop="highPrice")
    if maxsale:
        maxsale = int(maxsale['content'])
    else:
        maxsale = np.nan
    if minsale:
        minsale = int(minsale['content'])
    else:
        minsale = maxsale

    rental = soup.find("div", class_="price-overview-row rentals")
    if rental:
        rentals = [int(r.text.strip().replace(',','')) for r in rental.find_all("span", class_="element-label price")]
        if len(rentals)==2:
            minrental, maxrental = rentals
        else:
            minrental, maxrental = rentals[0], rentals[0]
    else:
        minrental, maxrental = np.nan, np.nan

    
    
    propinfo = [propname, minsale, maxsale, minrental, maxrental, HEADER2+link]
    return propinfo

def Listing_Link_Scraper(soup):
    links = []
    units = soup.find_all("div", itemtype="https://schema.org/Place")
    for unit in units:
        if unit.find("a", class_="btn btn-primary-outline units_for_sale disabled") or unit.find("a", class_="btn btn-primary-outline units_for_rent disabled"):
            continue
        #print(unit.find("a", class_="btn btn-primary-outline units_for_sale"), unit.find("a", class_="btn btn-primary-outline units_for_rent"))
        prop = unit.find("a", class_="nav-link")
        sale = unit.find("a", class_="btn btn-primary-outline units_for_sale")["href"]
        rent = unit.find("a", class_="btn btn-primary-outline units_for_rent")["href"]
        links.append((prop['title'],prop["href"]))
    return(links)

def Listing_Price_Scrapper(prop):
    pname, plink= prop
    print('Scraping '+pname+' for sale...')
    sale_soup = BS_Prep(HEADER+plink.replace('/condo/', '/property-for-sale/at-')+'?limit=500')
    sale_list = []
    for s in sale_soup.find_all("span", class_="price"):
        try:
            sale_list.append(float(s.text.split(' ')[-1].replace(',','').strip()))
        except:
            sale_list.append(np.nan)
    print('Scraping '+pname+' for rent...')
    rent_soup = BS_Prep(HEADER+plink.replace('/condo/', '/property-for-rent/at-')+'?limit=500')
    rent_list = []
    for r in rent_soup.find_all("span", class_="price"):
        try:
            rent_list.append(float(r.text.split(' ')[0].replace(',','').strip()))
        except:
            rent_list.append(np.nan)
    return [pname, np.nanmean(sale_list), np.nanmedian(sale_list), len(sale_list), np.nanmean(rent_list), np.nanmedian(rent_list), len(rent_list), HEADER+plink]

# Initialize URL
HEADER = 'https://www.propertyguru.com.my'
KEY = '/condo/search-project'
QUERY = '?limit=500&market='+MARKET+property_type[TYPE]+state[STATE]+'&newProject=all'

# Load first page with Query and scrape no. of pages
soup = BS_Prep(HEADER+KEY+QUERY)
pages = Pagination(soup)

# Scrape links from first page for properties with both sale and rental listing
props = []
props += Listing_Link_Scraper(soup)
print('\rPage 1 done.', flush=True)

# Scrape subsequent pages
for page in range(2, pages+1):
    soup = BS_Prep(HEADER+KEY+'/'+str(page)+QUERY)
    props += Listing_Link_Scraper(soup)
    print('\rPage '+str(page)+' done.', flush=True)

# Scrape prices for sale and rental of each properties
data = []
print('A total of '+str(len(props))+' properties will be scraped.')
for i, prop in enumerate(props):
    p = Listing_Price_Scrapper(prop)
    print(p)
    print(str(i+1)+'/'+str(len(props))+' done!')
    data.append(p)
print(data)

# Result into DataFrame and Analysis
df = pd.DataFrame(data, columns=['PropertyName','MeanSale','MedianSale', 'NSale', 'MeanRental','MedianRental', 'NRental', 'URL'])
df.dropna(inplace=True)
df.insert(7, 'Mean%Coverage', df.MeanRental*100/df.MeanSale/100000*404)
df.insert(8, 'Median%Coverage', df.MedianRental*100/df.MedianSale/100000*404)

# Data save to file
df.to_csv(FILENAME, index=False)
print('Output file saved to /'+FILENAME)