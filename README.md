# PropertyGuru Property Listing Scraper
## Description:
- A python scraper to scrape and compare property price for sale or rent in Malaysia from PropertyGuru.com.
- Currently supports state and property type filters only (ping me if you need more precise/personalized filters)
- Strictly for educational purposes only.
- Any suggestions/collabs are very much welcomed!

## Instruction:
Simple! Just modify the Query Selection value of your choices. (Default: Residential Terraces in KL)  
P/S: Refer to documentation below for the keywords

## Documentation:
### Query filter keywords (select one for each category):
|Category|Keywords|
|--|--|
|MARKET|residential, commercial (not tested)|
|PROPERTY_TYPE|all, bungalow (Bungalow / Villa), condo (Apartment / Condo / Service Residence), semid (Semi-Detached House), terrace (Terrace / Link House), land (Residential Land)|
|STATE|johor, kedah, kelantan, melaka, ns, pahang, penang, perak, perlis, selangor, terengganu,
sabah, sarawak, kl, labuan, putrajaya, other|

### Quick Notes:
1. The degree of high-balling are assumed to be the same for both selling and renting prices scraped.
2. Only those properties with both sale and rental listed will be selected.
3. Rarely rental price will produce NaN failed to be scraped (will be fixed soon)
4. Default analysis will remove NaN entries and calculate break-even % as in (2) based on median prices
5. Gross Rental-Installment Break-even Rate are pre-calculated as:
> RM404 monthly installment /RM100k selling price (90% loan, 3.5% IR, 30yrs)

