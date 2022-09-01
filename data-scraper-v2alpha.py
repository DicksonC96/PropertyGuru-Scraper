from multiprocessing.sharedctypes import Value
from bs4 import BeautifulSoup
import time
from datetime import date
import cloudscraper
import numpy as np
import pandas as pd
import os
import hashlib
import argparse

# Default Query parameter
MARKET = 'residential'
TYPE = 'condo'
STATE = 'kl'

### CODE STARTS HERE ###

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

def BSPrep(URL):
    exitcode = 1
    while exitcode == 1:
        try:
            trial = 0
            while trial < 10:
                scraper = cloudscraper.create_scraper()
                print('Loading '+URL)
                s = scraper.get(URL)
                soup = BeautifulSoup(s.content, 'html.parser')
                if "captcha" in soup.text:
                    trial += 1
                    print('Retrying '+' ('+str(trial)+'/10) ...')
                    time.sleep(0.1)
                    continue
                elif "No Results" in soup.text:
                    print('Invalid URL, skipping '+URL)
                    trial = 99
                else:
                    trial = 99
            if trial == 10:
                print('Trial exceeded, skipping '+URL)
            exitcode = 0
            return soup
        except:
                print('Connection reset, retrying in 1 mins...', flush=True)
                time.sleep(60)
        
def Pagination(soup):
    pagination = soup.find("ul", class_="pagination")
    if pagination.find_all("li", class_="pagination-next disabled"):
        pages = int(pagination.find_all("a")[0]['data-page'])
    else:
        pages = int(pagination.find_all("a")[-2]['data-page'])
    return pages

def LinkScraper(soup):
    links = []
    units = soup.find_all("div", itemtype="https://schema.org/Place")
    for unit in units:
        if unit.find("a", class_="btn btn-primary-outline units_for_sale disabled") and unit.find("a", class_="btn btn-primary-outline units_for_rent disabled"):
            continue
        prop = unit.find("a", class_="nav-link")
        links.append((prop['title'],HEADER+prop["href"]))
    return(links)

def InfoExtract(pname, soup, key):
    page_listing = []
    i = -1 if 'sale' in key else 0
    type = 'Sale' if 'sale' in key else 'Rent'
    for property in soup.find_all(itemtype="https://schema.org/Place"):
        try:
            bed = property.find('span', class_="bed").text.strip()
            bath = property.find('span', class_="bath").text.strip()
        except AttributeError:
            try:
                bed = property.find("li", class_="listing-rooms pull-left").text.strip()
                bath = property.find("li", class_="listing-rooms pull-left").text.strip()
            except AttributeError:
                bed = np.nan
                bath = np.nan
            
        try:
            price = float(property.find("span", class_="price").text.split(' ')[i].replace(',','').strip())
        except AttributeError:
            price = np.nan
        except ValueError:
            price = property.find("span", class_="price").text.split(' ')[i].replace(',','').strip()
        try:
            sqft = int(property.find("li", class_="listing-floorarea pull-left").text.split(' ')[0])
        except AttributeError:
            sqft = np.nan
        except ValueError:
            sqft = np.nan
        try:
            author = property.find('span', class_='name').text
        except AttributeError:
            author = np.nan
        page_listing.append([pname, type, price, bed, bath, sqft, author])
    return page_listing

def PropScrapper(pname, plink, key):
    prop_listing = []
    soup = BSPrep(plink.replace('/condo/', key))
    title = soup.find('h1', class_='title search-title text-transform-none')
    total = title['title'].split(' ')[0]
    prop_listing += InfoExtract(pname, soup, key)
    if total != 'No' and int(total) > 20:
        for page in range(2, int(total)//20+2):
            soup = BSPrep(plink.replace('/condo/', key)+'/'+str(page))
            prop_listing += InfoExtract(pname, soup, key)
    return prop_listing

def md5hash(datafile, hashfile):
    h = hashlib.md5()
    with open(datafile,'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    with open(hashfile, 'w') as f:
        f.write(h.hexdigest())
    print('MD5 hash generated to '+hashfile)

def PropTrimmer(props, datafile):
    df_old = pd.read_csv(datafile)
    prop, link = zip(*props)
    len_old_props = len(prop)
    last_prop_name = df_old.PropertyName.iat[-1]
    prop_index = prop.index(last_prop_name)
    props = props[prop_index:]
    print('This is a re-run.\nSkipping {} properties scraped previously.'.format(len_old_props-len(props)))
    return props, last_prop_name

def argparser():
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('-m', '--market', default=MARKET, dest='Market', help='eg. Residential, Commercial etc. (default: Condo)')
        parser.add_argument('-t', '--type', default=TYPE, dest='Type', help='eg. Condo, Terrace, etc. (default: condo)')
        parser.add_argument('-s', '--state', default=STATE, dest='State', help='eg. KL, Selangor, Johor etc. (default: KL)')
        args = parser.parse_args()
        return args
    except:
        parser.print_help()
        exit()

def main():
    
    # Load first page with Query and scrape no. of pages
    print('\n===================================================\nPropertyGuru Property Listing Scraper v2.3-alpha\nAuthor: DicksonC\n===================================================\n')
    time.sleep(2)
    print('Job initiated with query on {} in {}.'.format(TYPE, STATE))
    print('\nLoading '+HEADER+KEY+QUERY+' ...\n')
    soup = BSPrep(HEADER+KEY+QUERY)
    pages = Pagination(soup)
    print(str(pages)+' page will be scrapped.\n')

    # Scrape links from first page for properties with both sale and rental listing
    props = []
    props += LinkScraper(soup)
    print('\rPage 1/{} done.'.format(str(pages)))

    # Scrape subsequent pages
    for page in range(2, pages+1):
        soup = BSPrep(HEADER+KEY+'/'+str(page)+QUERY)
        props += LinkScraper(soup)
        print('\rPage {}/{} done.'.format(str(page), str(pages)))

    # Check exising data and remove scraped links
    if os.path.exists(RAW_LISTING):
        try:
            props, last_prop_name = PropTrimmer(props, RAW_LISTING)
            error_flag = False
        except ValueError or IndexError:
            print("EOF does not match. Scraping starts from the beginning.")
            error_flag = True
    
    # Scrape details for sale and rental of each properties
    data = []
    print('\nA total of '+str(len(props))+' properties will be scraped.\n')
    try:
        for i, prop in enumerate(props):
            sale = PropScrapper(*prop, '/property-for-sale/at-')
            rent = PropScrapper(*prop, '/property-for-rent/at-')
            print(str(i+1)+'/'+str(len(props))+' done!')
            data += sale
            data += rent
        
        # Result into DataFrame and Analysis
        df = pd.DataFrame(data, columns=['PropertyName','Type','Price','Bedrooms','Bathrooms','Sqft','Author'])

        # Check exising data and combine
        if os.path.exists(RAW_LISTING):
            if not error_flag:
                df_old = pd.read_csv(RAW_LISTING)
                df_old = df_old[df_old.PropertyName!=last_prop_name]
                df = pd.concat([df_old, df])

        # Raw data saved to file
        df.to_csv(RAW_LISTING, index=False)
        print('Raw data saved to {}'.format(RAW_LISTING))

    except:
        print('Error encountered! Exporting current data ...')

        # Result into DataFrame and Analysis
        df = pd.DataFrame(data, columns=['PropertyName','Type','Price','Bedrooms','Bathrooms','Sqft','Author'])

        # Raw data saved to file
        df.to_csv(RAW_LISTING, index=False)
        print('INCOMPLETE raw data saved to {}'.format(RAW_LISTING))
        exit(1)

    else:
        md5hash(RAW_LISTING, MD5HASH)

if __name__ == "__main__":

    # Initialize arguments
    args = argparser()
    MARKET, TYPE, STATE= args.Market, args.Type, args.State
    
    # Initialize filenames (leave empty if not generating):
    RAW_LISTING = './data/{}-{}-{}-listing.csv'.format(TYPE,STATE,date.today().strftime("%b%Y"))
    MD5HASH = './md5hash/{}-{}-{}-listing.md5'.format(TYPE,STATE,date.today().strftime("%b%Y"))

    # Initialize URL
    HEADER = 'https://www.propertyguru.com.my'
    KEY = '/condo/search-project'
    QUERY = '?limit=500&market='+MARKET.lower()+property_type[TYPE.lower()]+state[STATE.lower()]+'&newProject=all'
    
    main()
