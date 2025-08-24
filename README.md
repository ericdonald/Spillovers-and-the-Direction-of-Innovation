# Replication Package for "Spillovers and the Direction of Innovation"

## Dataset List:

Below is the list of all data sets required for replication. The first set lists those downloaded inside of the code using APIs, and the second set lists those contained within the Raw Data folder. Therefore, the links below are for reference only; a user does not need to visit these sites to extract the data.
To make use of the API commands, the user will need to make a '.env' file with the following lines:

```
#API Keys
FRED_API = 'XX'
IPUMS_API = 'XX'
BEA_API = 'XX'
EIA_API = 'XX'
```

where XX is the user's API key for the relevant data source. All data sources have publicly available APIs that only require registration.

### API Acessible:
- FRED
  - [CPI](https://fred.stlouisfed.org/series/CPIAUCSL)
  - [Motor Vehicle Output (Nominal)](https://fred.stlouisfed.org/series/A953RC1Q027SBEA#0)
  - [Nominal GDP](https://fred.stlouisfed.org/series/GDP)
  - [Total R&D (Nominal)](https://fred.stlouisfed.org/series/Y694RC1Q027SBEA)
- EIA
- Our World in Data
- PatentsView

### Contained in Raw Data:
- [Transportation Energy Data Book: Table 6.02](https://tedb.ornl.gov/data/)
- [2010 RICE](https://www.icpsr.umich.edu/web/ICPSR/studies/28461/summary). Note that the '.xlsx' file in the Raw Data folder comes from running the downloadable sheet from the link and extracting emission paths.
