# Replication Package for "[Spillovers and the Direction of Innovation](https://www.ericdonald.com/research/spillovers-and-the-direction-of-innovation)"

## Dataset List:

Below is the list of all data sets required for replication. The first set lists those downloaded inside of the code using APIs, and the second set lists those contained within the Raw Data folder. Therefore, the links below are for reference only; a user does not need to visit these sites to extract the data.
To make use of the API commands, the user will need to make a '.env' file with the following lines:

```
#API Keys
FRED_API = 'XX'
EIA_API = 'XX'
PatentsView_API = 'XX'
```

where XX is the user's API key for the relevant data source. All data sources have publicly available APIs that only require registration.

### API Acessible:
- FRED
  - [CPI](https://fred.stlouisfed.org/series/CPIAUCSL)
  - [Motor Vehicle Output](https://fred.stlouisfed.org/series/A953RC1Q027SBEA#0)
  - [GDP](https://fred.stlouisfed.org/series/GDP)
  - [Total R&D Spending](https://fred.stlouisfed.org/series/Y694RC1Q027SBEA)
- EIA
  - [Electricity Revenue](https://www.eia.gov/opendata/browser/electricity/retail-sales?frequency=annual&data=revenue;&facets=stateid;sectorid;&stateid=US;&sectorid=ALL;&sortColumn=period;&sortDirection=desc;)
  - [Electricity Quantities](https://www.eia.gov/opendata/browser/electricity/electric-power-operational-data?frequency=annual&data=generation;&facets=fueltypeid;location;sectorid;&fueltypeid=ALL;FOS;&location=US;&sectorid=99;&sortColumn=period;&sortDirection=desc;)
- Our World in Data
  - [Global Industrial Emissions](https://ourworldindata.org/grapher/annual-co2-emissions-per-country?country=~OWID_WRL)
  - [Global Land-Use Emissions](https://ourworldindata.org/grapher/co2-land-use?tab=line&country=~OWID_WRL)
- PatentsView
  - [CPC Codes](https://patentsview.org/download/data-download-tables)
  - [Applications](https://patentsview.org/download/data-download-tables)
  - [Citations](https://patentsview.org/download/data-download-tables)

### Contained in Raw Data:
- [Transportation Energy Data Book: Table 6.02](https://tedb.ornl.gov/data/)
- Regional Emissions from [2010 RICE](https://www.icpsr.umich.edu/web/ICPSR/studies/28461/summary)
- [NOAA Atmospheric Carbon Concentrations](https://gml.noaa.gov/ccgg/trends/data.html)
- [EPA Emissions Inventory](https://cfpub.epa.gov/ghgdata/inventoryexplorer/#allsectors/allsectors/allgas/econsect/all)
- [IEA Public R&D Spending](https://www.iea.org/data-and-statistics/data-product/energy-technology-rd-and-d-budget-database-2)
- [Congressional Research Service Report IF11017](https://www.congress.gov/crs-product/IF11017)
- [Congressional Research Service Report IF10479](https://www.congress.gov/crs-product/IF10479)
