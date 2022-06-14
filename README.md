# PropertyGuru Property Listing Scraper

## Description:
- A python scraper to scrape and compare property price for sale or rent in Malaysia from PropertyGuru.com.
- Currently supports state and property type filters only (ping me if you need more precise/personalized filters)
- Strictly for educational purposes only.
- Any suggestions/collabs are very much welcomed!
- [Condo-KL price datasets](https://github.com/DicksonC96/PropertyGuru-Scraper/tree/main/data) (updated monthly)
- [Condo-KL data visualization](https://datastudio.google.com/s/iDD1161H8RQ) (updated monthly)

## Dashboard  
Data Studio dashboard: https://datastudio.google.com/reporting/b0445da4-f585-4790-a75b-f452eefc1e53
![image](https://user-images.githubusercontent.com/66625723/173601300-89c0b8c5-364b-48a3-90c4-cf60dff07471.png)  
  
### Column Description
- Mean: Mean Price for Sale/Rent
- CV: Coefficient of Variation of Sale/Rent Price
- Median: Mean Price for Sale/Rent  

### Color Legend
- $`\textcolor{red}{\text{red}}`$: For Sale
- [Blue]{blue}: For Rent
- [Green]{green}: Percentage BreakEven

## Instruction:
1. Download [data-scraper-v2alpha.py](https://raw.githubusercontent.com/DicksonC96/PropertyGuru-Scraper/main/data-scraper-v2alpha.py) (right-click and download).
2. Modify __Section 1:Query Selection__ with keywords of your choice. (default: Residential Highrises in KL).
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

### Raw Data Column Description
|Column|Type|Remarks|
|--|--|--|
|PropertyName|str| |
|Type|str|Sale/Rent|
|Price|float| |
|Bedrooms|str|int or str (eg. Studio)|
|Bathrooms|str|int or str (eg. Studio)|
|Sqft|int|Lot size|
|Author|str|Person who uploaded the listing|
