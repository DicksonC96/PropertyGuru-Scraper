# PropertyGuru Property Listing Scraper And Rental-Installment BreakEven Analysis

## Interactive Dashboard 
Condo Property Price in KL (updated monthly): https://datastudio.google.com/s/iDD1161H8RQ
![image](https://user-images.githubusercontent.com/66625723/173601300-89c0b8c5-364b-48a3-90c4-cf60dff07471.png)  
  
### Column Description
- Mean: Mean Price for Sale/Rent
- CV: Coefficient of Variation of Sale/Rent Price
- Median: Mean Price for Sale/Rent  

### Color Legend
- Red: Sale list summary
- Blue: Rental list summary
- Green: Percentage breakeven (%)

### Rental-Installment BreakEven Formula and Assumptions
1. The degree of high-balling are assumed to be the same for both selling and renting prices scraped.
2. Only those properties with both sale and rental listed will be selected.
3. Default analysis will remove NaN entries and calculate break-even % as in (2) based on median prices.
5. Gross Rental-Installment Break-even Rate are pre-calculated as:
> RM404 monthly installment /RM100k selling price (90% loan, 3.5% IR, 30yrs)

## Property List Scraper
- A python scraper to scrape property price listed for sale or rent in Malaysia from PropertyGuru.com.
- Currently supports state and property type filters only (ping me if you need more precise/personalized filters)
- Strictly for educational purposes only.
- Any suggestions/collabs are very much welcomed!
- [Condo-KL price datasets](https://github.com/DicksonC96/PropertyGuru-Scraper/tree/main/data) (sampled every first day of the month)

### How to scrape myself?
1. Download [data-scraper-v2alpha.py](https://raw.githubusercontent.com/DicksonC96/PropertyGuru-Scraper/main/data-scraper-v2alpha.py) (right-click and download).
2. Modify __Section 1:Query Selection__ with keywords of your choice. (default: Residential Highrises in KL).
3. Run the script with [python](https://www.python.org/).
4. Enjoyy!
P/S: Refer section below for the keywords

### Query selection keywords (select one for each category):
|Category|Keywords|
|--|--|
|MARKET|residential, commercial (not tested)|
|PROPERTY_TYPE|all, bungalow (Bungalow / Villa), condo (Apartment / Condo / Service Residence), semid (Semi-Detached House), terrace (Terrace / Link House), land (Residential Land)|
|STATE|johor, kedah, kelantan, melaka, ns, pahang, penang, perak, perlis, selangor, terengganu, sabah, sarawak, kl, labuan, putrajaya, other|

### Output Data Description
|Column|Type|Remarks|
|--|--|--|
|PropertyName|str| |
|Type|str|Sale/Rent|
|Price|float| |
|Bedrooms|str|int or str (eg. Studio)|
|Bathrooms|str|int or str (eg. Studio)|
|Sqft|int|Lot size|
|Author|str|Person who uploaded the listing|
