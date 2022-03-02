# PropertyGuru Property Listing Scraper
## Description:
- A python scraper to scrape and compare property price for sale or rent in Malaysia from PropertyGuru.com.
- Currently supports state and property type filters only (ping me if you need more precise/personalized filters)
- Strictly for educational purposes only.
- Any suggestions/collabs are very much welcomed!
- [Condo-KL datasets](https://github.com/DicksonC96/PropertyGuru-Scraper/tree/main/data) (updated monthly)

## Instruction:
1. Download [data-scraper.py](https://raw.githubusercontent.com/DicksonC96/PropertyGuru-Scraper/main/data-scraper.py) (right-click and download).
2. Modify __Section 1:Query Selection__ with keywords of your choice. (default: Residential Terraces in KL).
3. Run the script with [python](https://www.python.org/).
4. Enjoyy!
P/S: Refer documentation below for the keywords

## Documentation:
### Query selection keywords (select one for each category):
|Category|Keywords|
|--|--|
|MARKET|residential, commercial (not tested)|
|PROPERTY_TYPE|all, bungalow (Bungalow / Villa), condo (Apartment / Condo / Service Residence), semid (Semi-Detached House), terrace (Terrace / Link House), land (Residential Land)|
|STATE|johor, kedah, kelantan, melaka, ns, pahang, penang, perak, perlis, selangor, terengganu, sabah, sarawak, kl, labuan, putrajaya, other|

### Quick Notes:
1. The degree of high-balling are assumed to be the same for both selling and renting prices scraped.
2. Only those properties with both sale and rental listed will be selected.
3. Number of properties being listed, along with the invalid result will be recorded for result validation.
4. Default analysis will remove NaN entries and calculate break-even percentages.
5. Monthly installment assumption:
> RM404 monthly installment /RM100k selling price (90% loan, 3.5% IR, 30yrs)
6. Rental-installment break-even percentage formula:
> Break-even = ( rental / (sale/100k*404) ) * 100 %

### Data Analysis
|Column|Description|
|--|--|
|PropertyName|Name of the property|
|MeanSale|Mean of the listed selling prices|
|MedianSale|Median of the listed selling prices|
|MeanRental|Mean of the listed rental prices|
|MedianRental|Median of the listed rental prices|
|%toBreakEven|Rental-installment break-even percentage based on median|
|NSale|Number of properties for sale listed|
|NRental|Number of properties for rent listed|
|NError|Number of listings with invalid price stated|
|URL|Direct link to the property site on PropertyGuru.com|
