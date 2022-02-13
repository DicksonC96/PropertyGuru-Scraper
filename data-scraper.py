import requests
from bs4 import BeautifulSoup
import time
import cloudscraper

'''
PropertyGuru project query filter format:

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

'''

MARKET = 'residential'
TYPE = 'bungalow'
STATE = 'kedah'
WITH_PRICE = 1
FILE_NAME = ''

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
    exit_code = 1
    while exit_code == 1:
        scraper = cloudscraper.create_scraper()
        s = scraper.get(URL)
        soup = BeautifulSoup(s.content, 'html.parser')
        if "captcha" not in soup.text:
            exit_code = 0
        else:
            print('Retrying...')
            time.sleep(0.1)
    return soup

def Link_Scrapper(soup, with_price):
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
    

HEADER = 'https://www.propertyguru.com.my/condo/search-project'
QUERY = '?limit=500&market='+MARKET+property_type[TYPE]+state[STATE]+'&newProject=all'

soup = BS_Prep(HEADER+QUERY)
pages = Pagination(soup)

links = []
links += Link_Scrapper(soup, WITH_PRICE)
print('\rPage 1 done.', flush=True)

for page in range(2,pages+1):
    page_URL = HEADER+'/'+str(page)+QUERY
    soup = BS_Prep(page_URL)
    links += Link_Scrapper(soup, WITH_PRICE)
    print('\rPage '+str(page)+' done.', flush=True)

print(links)
print(str(len(links))+' property links generated!')

