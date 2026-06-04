# Replication Package <br> [Spillovers and the Direction of Innovation](https://www.ericdonald.com/research/spillovers-and-the-direction-of-innovation)

## Data Sources:

Below is the list of all data sources required for replication. The first group are those programmatically retrieved via APIs or direct download, the second group are those contained in the Raw Data folder, and the third group are those that require the user to have a license. The links below are for reference only; a user does not need to visit these sites to extract the data.
To make use of the API commands, the user will need to make a `.keys` file with the following lines:

```
FRED_API = XX
EIA_API = XX
```

where `XX` is the user's API key for the relevant data source.

### API/Web Acessible:

- FRED
  - [CPI](https://fred.stlouisfed.org/series/CPIAUCSL)
  - [Motor Vehicle Output](https://fred.stlouisfed.org/series/A953RC1Q027SBEA#0)
  - [GDP](https://fred.stlouisfed.org/series/GDP)
  - [Total R&D Spending](https://fred.stlouisfed.org/series/Y694RC1Q027SBEA)
- EIA
  - [Electricity Revenue](https://www.eia.gov/opendata/browser/electricity/retail-sales?frequency=annual&data=revenue;&facets=stateid;sectorid;&stateid=US;&sectorid=ALL;&sortColumn=period;&sortDirection=desc;)
  - [Electricity Quantities](https://www.eia.gov/opendata/browser/electricity/electric-power-operational-data?frequency=annual&data=generation;&facets=fueltypeid;location;sectorid;&fueltypeid=ALL;FOS;&location=US;&sectorid=99;&sortColumn=period;&sortDirection=desc;)
- EPA
  - [Greenhouse Gas Inventory](https://cfpub.epa.gov/ghgdata/inventoryexplorer/#allsectors/allsectors/allgas/econsect/all)
- Our World in Data
  - [Global Industrial Emissions](https://ourworldindata.org/grapher/annual-co2-emissions-per-country?country=~OWID_WRL)
  - [Global Land-Use Emissions](https://ourworldindata.org/grapher/co2-land-use?tab=line&country=~OWID_WRL)
  - [Photovoltaic Prices](https://ourworldindata.org/grapher/solar-pv-prices)
  - [Solar Share of Global Electricity](https://ourworldindata.org/grapher/share-electricity-solar?tab=line&time=1985..2024&country=~OWID_WRL)
  - [Low-Carbon Electricity Share](https://ourworldindata.org/grapher/share-electricity-low-carbon?tab=line&country=OWID_EU27~CHN~USA)
- NOAA
  - [Atmospheric Carbon Concentrations](https://gml.noaa.gov/ccgg/trends/data.html)
- PatentsView
  - [CPC Codes](https://patentsview.org/download/data-download-tables)
  - [Applications](https://patentsview.org/download/data-download-tables)
  - [Citations](https://patentsview.org/download/data-download-tables)
  - [Inventors](https://patentsview.org/download/data-download-tables)
  - [Location Crosswalk](https://patentsview.org/download/data-download-tables)
- [Transportation Energy Data Book: Table 6.02](https://tedb.ornl.gov/data/)

### Contained in Raw Data:

- Regional Emissions from [2010 RICE](https://www.icpsr.umich.edu/web/ICPSR/studies/28461/summary)
- [IEA Public R&D Spending](https://www.iea.org/data-and-statistics/data-product/energy-technology-rd-and-d-budget-database-2)
- [Congressional Research Service Report IF11017](https://www.congress.gov/crs-product/IF11017)
- [Congressional Research Service Report IF10479](https://www.congress.gov/crs-product/IF10479)
- Crosswalks of Patents to Firms from [Kogan et al. (2017)](https://github.com/KPSS2017/Technological-Innovation-Resource-Allocation-and-Growth-Extended-Data) and [Arora et al. (2021)](https://zenodo.org/records/13619821)
- State-Level R&D Prices from [Lucking et al. (2019)](https://www.dropbox.com/s/d1nrtacxk6qke0a/spillovers_rep.zip?dl=0)

### Requires License:
- [Compustat](https://wrds-www.wharton.upenn.edu/)

## Software Requirements:

### Python

All of the replication codes run on Python `3.11.14`. Prior to running the codes, install the following packages:

| Package | Version |
|---------|---------|
| linearmodels | 7.0 |
| matplotlib | 3.10.8 |
| numba | 0.63.1 |
| numpy | 2.3.5 |
| openpyxl | 3.1.5 |
| pandas | 2.3.3 |
| quantecon | 0.10.1 |
| scipy | 1.17.0 |
| statsmodels | 0.14.6 |

## Description of Code:

### Setup Instructions

Before running the code, create the following folders in the repository root:

```
Raw Data/
Clean Data/
Results/
Results/Tables/
Results/Figures/
```

Download the [raw data](https://github.com/ericdonald/Spillovers-and-the-Direction-of-Innovation/releases/download/v1.0.0/Raw.Data.zip), unzip, and place the file(s) directly in Raw Data/.

## List of Tables and Figures:
