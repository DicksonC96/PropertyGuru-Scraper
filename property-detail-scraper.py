from bs4 import BeautifulSoup
import time
from datetime import date
import cloudscraper
import numpy as np
import pandas as pd
import os
import re
import requests_cache

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
            while trial < 50:
                scraper = cloudscraper.create_scraper()
                print('Loading '+URL)
                requests_cache.install_cache(expire_after=86400)
                s = scraper.get(URL)
                soup = BeautifulSoup(s.content, 'html.parser')
                if "captcha" in soup.text:
                    trial += 1
                    print('Retrying '+' ('+str(trial)+'/50) ...')
                    time.sleep(0.1)
                    if trial%10 == 0:
                        print('Connection reset, retrying in 30 secs...', flush=True)
                        time.sleep(30)
                    continue
                elif "No Results" in soup.text:
                    print('Invalid URL, skipping '+URL)
                    trial = 99
                else:
                    trial = 99
            
            exitcode = 0
            return soup
        except:
                print('Connection reset, retrying in 1 min...', flush=True)
                time.sleep(60)
        
def Pagination(soup):
    pagination = soup.find("ul", class_="pagination")
    try:
        if pagination.find_all("li", class_="pagination-next disabled"):
            pages = int(pagination.find_all("a")[0]['data-page'])
        else:
            pages = int(pagination.find_all("a")[-2]['data-page'])
    except AttributeError:
        if soup.find("h1", class_="title search-title").text.split(' ')[2] == '0':
            print('No property found. Scraping stopped.')
            exit(0)
        else:
            exit(1)
    return pages

def LinkScraper(soup):
    links = []
    units = soup.find_all("div", itemtype="https://schema.org/Place")
    for unit in units:
        prop = unit.find("a", class_="nav-link")
        links.append((prop['title'],HEADER+prop["href"]))
    return(links)

def PropLocScrapper(pname, plink):
    soup = BSPrep(plink)
    pid = re.search(r'\d+$', plink).group(0)
    details = soup.find('div', class_="map-canvas")
    if details != None:
        pname = details["data-marker-label"]
        lat = details["data-latitude"]
        long = details["data-longitude"]
        region = details["data-region"].upper()
        return [pid, pname, lat, long, region]
    else:
        return [pid, np.nan, np.nan, np.nan, np.nan]

def main():
    
    # Load first page with Query and scrape no. of pages
    print('\n===================================================\nPropertyGuru Property Listing Scraper v2.4-alpha\nAuthor: DicksonC\n===================================================\n')
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
    
    # Scrape details for sale and rental of each properties
    proplocs = []
    print('\nA total of '+str(len(props))+' properties will be scraped.\n')

    for i, prop in enumerate(props):
        proploc = PropLocScrapper(*prop)
        proplocs.append(proploc)
        print(str(i+1)+'/'+str(len(props))+' done!')

    # Result into DataFrame and Analysis
    df = pd.DataFrame(proplocs, columns=['PropertyID','PropertyName','Latitude','Longitude','Region'])

    # Raw data saved to file
    df.to_csv(PLOC_LISTING, index=False)
    print('Raw data saved to {}'.format(PLOC_LISTING))

if __name__ == "__main__":

    PLOC_LISTING = './ploc/{}-{}-{}-ploc.csv'.format(TYPE,STATE,date.today().strftime("%b%Y"))

    # Initialize URL
    HEADER = 'https://www.propertyguru.com.my'
    KEY = '/condo/search-project'
    QUERY = '?limit=500&market='+MARKET.lower()+property_type[TYPE.lower()]+state[STATE.lower()]+'&newProject=all'
    
    main()
