"""""""""""
Processor Module

Notes: This file defines a class for processing the economy of "Spillovers and the Direction of Innovation".
    
Output: Results/Figures/Spillover_Network.png
        Results/Figures/Clean_Centrality.csv
        Results/Tables/Disagg_Results.csv
        Results/Figures/2010s_Transition.csv
        Results/Tables/Tens_Results.csv
        Results/Figures/LinearCompare.csv
        Results/Figures/TechPathBidenlow.csv
        Results/Figures/TechPathBidenhigh.csv
        Results/Figures/BasinsTax.csv
        Results/Figures/BasinsSub.csv
        Results/Figures/AmpDeterms.csv
        Results/Figures/TranDeterms.csv
        Results/Figures/TranPolicy.csv
        Results/Tables/PolicyX_Results.csv
        Results/Figures/IAMPolicy.csv
        Results/Figures/IAMPolicy_spilllow.csv
        Results/Figures/IAMPolicy_dischigh.csv
        Results/Figures/IAMPolicy_damhigh.csv
        Results/Figures/TempPathIAM.csv
        Results/Tables/IAM_Results.csv
        Results/Tables/Clean_Growth.pkl
        Results/Tables/CES_Results.csv
        Results/Figures/IAMPolicy_CES.csv

"""""""""""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import os
import io
import zipfile
from datetime import datetime
import requests as api
import Production_Functions as pf
import SteadyState_Functions as ssf
import Objective_Functions as of
import Research_Functions as rf
import Processing_Functions as gpf



class Processor:
    "Object Processing Simulated Economy"
    
    def __init__(self, E):
        "Initialize Processor Object"
        
        self.E = E
        self.Directory = Path(__file__).resolve().parent.parent.parent
        self.FRED_API = os.getenv("FRED_API")
        self.EIA_API = os.getenv("EIA_API")
        self.PPM_C = 2.13 #Atmospheric PPM of CO2 to GtC
        self.CO2_C = 12/44 #CO2 to Carbon Conversion
        
        self.classes = ["car", "elec"]
        self.types = ["clean", "dirty"]
        
        self.IED_classes = {("elec", "clean"): ["RENEWABLE", "NUCLEAR", "34BIOFUE"],
                            ("elec", "dirty"): ["21OILGAS", "22COAL"],
                            ("car",  "clean"): ["1311VBAT", "1312ADVA", "1314INFR"],
                            ("car",  "dirty"): ["1313ENGI", "21OILGAS"]}

        
        
    def Cleaner(self, ind_year=1800, CPI_year=2021):
        """""
        Clean Data
        
        Output: Raw Data/Patent_CPC.pkl
                Raw Data/Patent_Citations.pkl
                Clean Data/RICE.pkl
                Clean Data/cal_panel.pkl
                Clean Data/clim_cal_panel.pkl
        """""
   
    
        # ----------------------------------------------------------------

        # Unpack data sets.

        # ----------------------------------------------------------------
        
        # -------- #
        # FRED CPI #
        # -------- #
        FRED = api.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&frequency=a&api_key={self.FRED_API}&file_type=json')
        data = FRED.json()['observations']
        filtered_data = [{'year': entry['date'], 'CPI': entry['value']} for entry in data]
        FRED_CPI_df = pd.DataFrame(filtered_data)
        
        FRED_CPI_df['year'] = pd.to_datetime(FRED_CPI_df['year']).dt.year
        FRED_CPI_df['CPI'] = pd.to_numeric(FRED_CPI_df['CPI'], errors='coerce')
        FRED_CPI_df['CPI'] = FRED_CPI_df['CPI'] / FRED_CPI_df.loc[FRED_CPI_df['year'] == CPI_year, 'CPI'].values[0] #CPI indexed to 1 in CPI_year
                
        
        # ------------------------- #
        # FRED Motor Vehicle Output #
        # ------------------------- #
        FRED = api.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=A953RC1Q027SBEA#0&frequency=a&api_key={self.FRED_API}&file_type=json')
        data = FRED.json()['observations']
        filtered_data = [{'year': entry['date'], 'car_revenue': entry['value']} for entry in data]
        FRED_VR_df = pd.DataFrame(filtered_data)
        
        FRED_VR_df['year'] = pd.to_datetime(FRED_VR_df['year']).dt.year
        FRED_VR_df['car_revenue'] = pd.to_numeric(FRED_VR_df['car_revenue'], errors='coerce') #Nominal US vehicle revenue in billions of dollars
                
        
        # -------- #
        # FRED GDP #
        # -------- #
        FRED = api.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=GDP&frequency=a&api_key={self.FRED_API}&file_type=json')
        data = FRED.json()['observations']
        filtered_data = [{'year': entry['date'], 'GDP': entry['value']} for entry in data]
        FRED_Y_df = pd.DataFrame(filtered_data)
        
        FRED_Y_df['year'] = pd.to_datetime(FRED_Y_df['year']).dt.year
        FRED_Y_df['GDP'] = pd.to_numeric(FRED_Y_df['GDP'], errors='coerce') #Nominal US GDP in billions of dollars
                
        
        # ----------------------- #
        # FRED Total R&D Spending #
        # ----------------------- #
        FRED = api.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=Y694RC1Q027SBEA&frequency=a&api_key={self.FRED_API}&file_type=json')
        data = FRED.json()['observations']
        filtered_data = [{'year': entry['date'], 'RD': entry['value']} for entry in data]
        FRED_RD_df = pd.DataFrame(filtered_data)
        
        FRED_RD_df['year'] = pd.to_datetime(FRED_RD_df['year']).dt.year
        FRED_RD_df['RD'] = pd.to_numeric(FRED_RD_df['RD'], errors='coerce') #Nominal US R&D in billions of dollars
                
        
        # ----------------------- #
        # EIA Electricity Revenue #
        # ----------------------- #
        EIA = api.get(f'https://api.eia.gov/v2/electricity/retail-sales/data/?api_key={self.EIA_API}&frequency=annual&data[0]=revenue&facets[stateid][]=US&facets[sectorid][]=ALL&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000')
        data = EIA.json()["response"]["data"]
        filtered_data = [{'year': entry['period'], 'elec_revenue': entry['revenue']} for entry in data]
        EIA_Rev_df = pd.DataFrame(filtered_data)
        
        EIA_Rev_df['year'] = pd.to_datetime(EIA_Rev_df['year']).dt.year
        EIA_Rev_df['elec_revenue'] = pd.to_numeric(EIA_Rev_df['elec_revenue'], errors='coerce')
        
        EIA_Rev_df['elec_revenue'] = EIA_Rev_df['elec_revenue'] / 1000 #Nominal US electricity revenue in billions of dollars
        
        
        # -------------------------- #
        # EIA Electricity Quantities #
        # -------------------------- #
        EIA = api.get(f'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key={self.EIA_API}&frequency=annual&data[0]=generation&facets[fueltypeid][]=ALL&facets[fueltypeid][]=FOS&facets[location][]=US&facets[sectorid][]=99&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000')
        data = EIA.json()["response"]["data"]
        filtered_data = [{'year': entry['period'], 'type':entry['fueltypeid'], 'MWh': entry['generation']} for entry in data]
        EIA_Q_df = pd.DataFrame(filtered_data)
        
        EIA_Q_df['year'] = pd.to_datetime(EIA_Q_df['year']).dt.year
        EIA_Q_df['MWh'] = pd.to_numeric(EIA_Q_df['MWh'], errors='coerce')
        
        EIA_Q_df = EIA_Q_df.pivot(index="year", columns="type", values="MWh").reset_index()
        EIA_Q_df['q_elec_clean'] = 1 - EIA_Q_df['FOS'] / EIA_Q_df['ALL'] #US clean electricity quantity share
        EIA_Q_df = EIA_Q_df[['year', 'q_elec_clean']]
                
        
        # ---------------------------- #
        # EPA Greenhouse Gas Inventory #
        # ---------------------------- #
        r = api.get("https://www.epa.gov/system/files/other-files/2024-04/executive-summary.zip", headers={"User-Agent": "Mozilla/5.0"})
        
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            target = next(p for p in z.namelist() if p.lower().endswith("table es-5.csv"))
            with z.open(target) as f:
                EPA_df = pd.read_csv(f, skiprows=1, nrows=8)  
       
        EPA_df = EPA_df.set_index(EPA_df.columns[0]).T.reset_index(drop=False)
        EPA_df = EPA_df.rename(columns={"index": "year",
                                        "Transportation": "car_C_em",
                                        "Electric Power Industry": "elec_C_em",
                                        "Total Gross Emissions (Sources)": "total_C_em"})
        
        EPA_df['year'] = pd.to_numeric(EPA_df['year'], errors='coerce')
        
        EPA_df['car_C_em'] = EPA_df['car_C_em'] * self.CO2_C / 1000
        EPA_df['elec_C_em'] = EPA_df['elec_C_em'] * self.CO2_C / 1000
        EPA_df['total_C_em'] = EPA_df['total_C_em'] * self.CO2_C / 1000
        #Carbon emissions equivalent in gigatons
        
        EPA_df = EPA_df.dropna(subset=["year"])
        EPA_df = EPA_df[["year", "car_C_em", "elec_C_em", "total_C_em"]]
        
        
        # -------------------------------- #
        # OWID Global Industrial Emissions #
        # -------------------------------- #
        OWID_CO2_Ind_df = pd.read_csv("https://ourworldindata.org/grapher/annual-co2-emissions-per-country.csv?v=1&csvType=filtered&useColumnShortNames=true&country=~OWID_WRL&overlay=download-data", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        
        OWID_CO2_Ind_df = OWID_CO2_Ind_df[['Year', 'emissions_total']]
        OWID_CO2_Ind_df = OWID_CO2_Ind_df.rename(columns={"Year": "year", "emissions_total": "C_em_fossil"})
        
        OWID_CO2_Ind_df['C_em_fossil'] = OWID_CO2_Ind_df['C_em_fossil'] * self.CO2_C / 1000000000 #Carbon emissions in gigatons
                
        
        # ------------------------------ #
        # OWID Global Land-Use Emissions #
        # ------------------------------ #
        OWID_CO2_LU_df = pd.read_csv("https://ourworldindata.org/grapher/co2-land-use.csv?v=1&csvType=filtered&useColumnShortNames=true&tab=line&country=~OWID_WRL&overlay=download-data", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        
        OWID_CO2_LU_df = OWID_CO2_LU_df[['Year', 'emissions_from_land_use_change']]
        OWID_CO2_LU_df = OWID_CO2_LU_df.rename(columns={"Year": "year", "emissions_from_land_use_change": "C_em_LU"})
        
        OWID_CO2_LU_df['C_em_LU'] = OWID_CO2_LU_df['C_em_LU'] * self.CO2_C / 1000000000 #Carbon emissions in gigatons
        
        #Extrapolate linear trend from 1850–1950 back to 1800
        fit_slice = OWID_CO2_LU_df[(OWID_CO2_LU_df['year'] >= 1850) & (OWID_CO2_LU_df['year'] <= 1950)].dropna(subset=['C_em_LU'])
        x = fit_slice['year'].values.astype(float)
        y = fit_slice['C_em_LU'].values.astype(float)
        
        a, b = np.polyfit(x, y, deg=1)
        
        years_back = np.arange(ind_year, 1850)
        y_hat_back = a * years_back + b
        
        extrap_df = pd.DataFrame({'year': years_back, 'C_em_LU': y_hat_back})
        
        have_years = set(OWID_CO2_LU_df['year'])
        extrap_df = extrap_df[~extrap_df['year'].isin(have_years)]
        
        OWID_CO2_LU_df = (
            pd.concat([OWID_CO2_LU_df, extrap_df], ignore_index=True)
              .sort_values('year')
              .reset_index(drop=True)
        )
           
        
        # -------------------------------------- #
        # NOAA Atmospheric Carbon Concentrations #
        # -------------------------------------- #
        NOAA_df = pd.read_csv("https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.csv",
                              skiprows=43,
                              usecols=[0, 1])
        
        NOAA_df = NOAA_df.rename(columns={"mean": "C_stock"})
        NOAA_df['C_stock'] = NOAA_df['C_stock'] * self.PPM_C #Atmospheric carbon concentrations in gigatons
        
        
        # --------------------- #
        # PatentsView CPC Codes #
        # --------------------- #
        PV_CPC_df = gpf.Extract_PatentsView('g_cpc_current')
        
        PV_CPC_df.to_pickle(f'{self.Directory}/Raw Data/Patent_CPC.pkl')
        
        
        # ------------------------ #
        # PatentsView Applications #
        # ------------------------ #
        PV_applications_df = gpf.Extract_PatentsView('g_application')
        
        PV_applications_df["year"] = pd.to_datetime(PV_applications_df["filing_date"], errors="coerce").dt.year
        PV_applications_df = PV_applications_df.dropna(subset=["year"])
        PV_applications_df = PV_applications_df[(PV_applications_df["year"] >= 1900) & (PV_applications_df["year"] <= datetime.now().year)]
        
        
        # --------------------- #
        # PatentsView Citations #
        # --------------------- #
        PV_citations_df = gpf.Extract_PatentsView('g_us_patent_citation')
        
        PV_citations_df.to_pickle(f'{self.Directory}/Raw Data/Patent_Citations.pkl')
        
        del PV_citations_df
        
        
        # ------------------------------------------- #
        # Transportation Energy Data Book: Table 6.02 #
        # ------------------------------------------- #
        url = "https://tedb.ornl.gov/wp-content/uploads/2022/06/Table6_02_06012022.xlsx"

        headers = {"User-Agent": "Mozilla/5.0"}
        r = api.get(url, headers=headers)
        
        TEDB_df = pd.read_excel(io.BytesIO(r.content),
                                sheet_name="TEDB Edition 40",
                                header=0,        
                                usecols="B:I",   
                                skiprows=7,      
                                nrows=24         
                            )
        
        TEDB_df = TEDB_df.rename(columns={
                    "Calendar year": "year",
                    "All light vehicle sales (thousands)": "Q_car" #Light vehicle quantity in thousands
                })
        
        TEDB_df['Hybrid vehicle sales (thousands)'] = pd.to_numeric(TEDB_df['Hybrid vehicle sales (thousands)'], errors='coerce')
        TEDB_df = TEDB_df.dropna(subset=["year"])
        
        TEDB_df["Q_car_clean"] = (
                        TEDB_df["Hybrid vehicle sales (thousands)"].fillna(0)
                      + TEDB_df["Plug-in hybrid vehicle sales (thousands)"].fillna(0)
                      + TEDB_df["All-electric vehicle sales (thousands)"].fillna(0)
                    ) #US clean vehicle quantity in thousands
        
        TEDB_df["q_car_clean"] = (
                        TEDB_df["Hybrid share of all light vehicles"].fillna(0)
                      + TEDB_df["Plug-in hybrid share of \nall light vehicles"].fillna(0)
                      + TEDB_df["All-electric share of all light vehicles"].fillna(0)
                    ) #US clean vehicle quantity share
        
        TEDB_df = TEDB_df[["year", "Q_car", "Q_car_clean", "q_car_clean"]]
        
        
        # --------- #
        # 2010 RICE #
        # --------- #
        RICE_df = pd.read_excel(f'{self.Directory}/Raw Data/RICE.xlsx', sheet_name="Results", header=0)
        
        RICE_df["year"] = pd.to_numeric(RICE_df["year"], errors="coerce").astype("Int64")
        
        needed_years = [2010, 3000]
        have = set(RICE_df["year"].dropna().tolist())
        to_add = [y for y in needed_years if y not in have]
        
        if to_add:
            add_df = pd.DataFrame({"year": to_add})
            RICE_df = pd.concat([RICE_df, add_df], ignore_index=True)
                
        RICE_df = RICE_df.sort_values("year")
        
        yr_min, yr_max = int(RICE_df["year"].min()), int(RICE_df["year"].max())
        full_years = pd.Index(range(yr_min, yr_max + 1), name="year")
        RICE_df = RICE_df.set_index("year").reindex(full_years).reset_index()
        
        em_cols = [
            "Optimal_Global_Em",
            "Optimal_US_Em",
            "Baseline_Global_Em",
            "Baseline_US_Em",
        ] #Carbon emissions in gigatons
        
        for c in em_cols:
            if c in RICE_df.columns:
                RICE_df[c] = pd.to_numeric(RICE_df[c], errors="coerce")
                RICE_df.loc[RICE_df["year"] > 2595, c] = 0.0
        
        RICE_df[em_cols] = RICE_df[em_cols].interpolate(
            method="linear", limit_direction="both", axis=0
        )
        
        RICE_df.to_pickle(f'{self.Directory}/Clean Data/RICE.pkl')
                
        
        # ----------------------- #
        # IEA Public R&D Spending #
        # ----------------------- #
        IEA_df = pd.read_csv(f'{self.Directory}/Raw Data/IED_RD_Sub.csv')
                              
        IEA_df = IEA_df[IEA_df["flagcodes"] != "L"]
        IEA_df = IEA_df.rename(columns={"time": "year"})
        
        IEA_df = IEA_df[["flow", "v6", "year", "value"]]
        
        for c in self.classes:
            for t in self.types:
                col = f"{c}_{t}"
                codes = self.IED_classes[(c, t)]
                IEA_df[col] = IEA_df["flow"].isin(codes).astype(float)
        
        IEA_df.loc[IEA_df["flow"] == "34BIOFUE", "elec_clean"] = -1.0
        IEA_df.loc[IEA_df["flow"] == "21OILGAS", "elec_dirty"] = 0.5
        IEA_df.loc[IEA_df["flow"] == "21OILGAS", "car_dirty"] = 0.5
        
        for c in self.classes:
            for t in self.types:
                flag_col = f"{c}_{t}"
                spend_col = f"{c}_{t}_class_spend"
                out_col = f"{c}_{t}_RD_sub"
                IEA_df[spend_col] = IEA_df["value"] * IEA_df[flag_col]
                IEA_df[out_col] = IEA_df.groupby("year")[spend_col].transform("sum") / 1000 #Nominal public R&D expenditures in billions of dollars
        
        rd_cols = [f"{c}_{t}_RD_sub" for c in self.classes for t in self.types]
        IEA_df = IEA_df[["year"] + rd_cols].drop_duplicates().sort_values("year").reset_index(drop=True)
        
        
        # -------------------------------------- #
        # Congressional Research Service Reports #
        # -------------------------------------- #
        CRS_data = {"year": [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
                    "car_clean_sub": [0.1, 0.2, 0.4, 0.2, 0.2, 0.3, 0.8, 1.2, 1.5, 1.7, 1.7],
                    "elec_clean_sub": [0.5, 0.5, 0.5, 0.6, 1.2, 2.5, 1.9, 2.8, 3.5, 6.8, 7.6]
                    } #Manually enter
        
        CRS_df = pd.DataFrame(CRS_data) #Nominal tax credit expenditures in billions of dollars


        # ----------------------------------------------------------------

        # Label patent technology classes.

        # ----------------------------------------------------------------
        
        
        # ----------------------------------------------------------------

        # Create panel of calibration moments.

        # ----------------------------------------------------------------
        
        cal_panel_df = FRED_CPI_df.copy()
        ##Sort out dates!!!
        
        # ----------- #
        # Electricity #
        # ----------- #
        cal_panel_df = pd.merge(cal_panel_df,
                                     EIA_Rev_df,
                                     on='year',
                                     how='inner'
                                     )
        
        cal_panel_df['Y_elec'] = cal_panel_df['elec_revenue'] / cal_panel_df['CPI']
        
        cal_panel_df = pd.merge(cal_panel_df,
                                     EIA_Q_df,
                                     on='year',
                                     how='inner'
                                     )
        
        
        # --------- #
        # Transport #
        # --------- #
        cal_panel_df = pd.merge(cal_panel_df,
                                     FRED_VR_df,
                                     on='year',
                                     how='inner'
                                     )
        
        cal_panel_df['Y_car'] = cal_panel_df['car_revenue'] / cal_panel_df['CPI']
        
        cal_panel_df = pd.merge(cal_panel_df,
                                     TEDB_df,
                                     on='year',
                                     how='inner'
                                     )
        
        
        # ------------ #
        # Final Output #
        # ------------ #
        cal_panel_df = pd.merge(cal_panel_df,
                                     FRED_Y_df,
                                     on='year',
                                     how='inner'
                                     )
        
        cal_panel_df['GDP'] = cal_panel_df['GDP'] / cal_panel_df['CPI']
        cal_panel_df['S_elec'] = cal_panel_df['Y_elec'] / cal_panel_df['GDP']
        cal_panel_df['S_car'] = cal_panel_df['Y_car'] / cal_panel_df['GDP']
        
        
        # ------------------ #
        # Sectoral Emissions #
        # ------------------ #
        cal_panel_df = pd.merge(cal_panel_df,
                                     EPA_df,
                                     on='year',
                                     how='inner'
                                     )
        
        cal_panel_df['elec_C_relem'] = cal_panel_df['elec_C_em'] / cal_panel_df['total_C_em']
        cal_panel_df['car_C_relem'] = cal_panel_df['car_C_em'] / cal_panel_df['total_C_em']
        
        
        # -------------------- #
        # Status Quo Subsidies #
        # -------------------- #
        cal_panel_df = pd.merge(cal_panel_df,
                                     CRS_df,
                                     on='year',
                                     how='outer'
                                     )
        
        cal_panel_df['elec_clean_sub'] = cal_panel_df['elec_clean_sub'] / cal_panel_df['CPI']
        cal_panel_df['elec_clean_relsub'] = cal_panel_df['elec_clean_sub'] / cal_panel_df['Y_elec']
        
        cal_panel_df['car_clean_sub'] = cal_panel_df['car_clean_sub'] / cal_panel_df['CPI']
        cal_panel_df['car_clean_relsub'] = cal_panel_df['car_clean_sub'] / cal_panel_df['Y_car']
        
        
        cal_panel_df = pd.merge(cal_panel_df,
                                     IEA_df,
                                     on='year',
                                     how='outer'
                                     )
        
        cal_panel_df.to_pickle(f'{self.Directory}/Clean Data/cal_panel.pkl')
        
        
        # ----------------------------------------------------------------

        # Create carbon emissions and atmospheric concentrations series.

        # ----------------------------------------------------------------
        
        clim_cal_panel_df = pd.merge(OWID_CO2_Ind_df,
                                     OWID_CO2_LU_df,
                                     on='year',
                                     how='inner'
                                     )
        
        clim_cal_panel_df['C_em'] = clim_cal_panel_df['C_em_fossil'] + clim_cal_panel_df['C_em_LU']
        
        clim_cal_panel_df = pd.merge(clim_cal_panel_df,
                                     NOAA_df,
                                     on='year',
                                     how='outer'
                                     )
        
        clim_cal_panel_df.to_pickle(f'{self.Directory}/Clean Data/clim_cal_panel.pkl')
         
        
         
    def Calibrate(self):
        """""
        Calibrate Parameters and Initial Conditions
        
        Output: Results/Figures/Carbon_Match.csv
                Results/Tables/Calibrate_Results.csv
        """""
        
        self.E.Calibrate()
        Calibrate_Results = gpf.ResultsTable()
        
        ω_prop = ((self.E.ω[3]-self.E.ω[1])/self.E.ω[1])*100
        Calibrate_Results.add('Relative Increase in Elec Carbon Intensity', gpf.clean_round(ω_prop, 1))
        
        # -------------------------------- #
        # Plot Match of Climate Parameters #
        # -------------------------------- #
        clim_cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/clim_cal_panel.dta')
        
        Em = clim_cal_panel.loc[(clim_cal_panel.year >= 1960) & (clim_cal_panel.year <= 2020), ['C_em']].to_numpy().reshape(61)
        C_data = clim_cal_panel.loc[(clim_cal_panel.year >= 1960) & (clim_cal_panel.year <= 2020), ['C_stock']].to_numpy().reshape(61)
        
        C1_Start = self.E.C_bar + self.E.ψ_p*np.sum(clim_cal_panel.loc[clim_cal_panel.year <= 1960, ['C_em']].to_numpy())
        C2_start = C_data[0] - C1_Start
        
        C1 = np.ones(Em.size)*C1_Start
        C2 = np.ones(Em.size)*C2_start
        
        for t in range(1, Em.size):
            C1[t] = pf.Perm_Carb(C1[t-1], Em[t], self.E.ψ_p)
            C2[t] = pf.Tran_Carb(C2[t-1], Em[t], self.E.ψ_p, self.E.ψ_0, self.E.ψ)
        
        C = C1 + C2
            
        DF_CM = pd.DataFrame(np.hstack((np.arange(1960, 2020+1).reshape((-1,1)), C_data.reshape((-1,1)), C.reshape((-1,1)))), 
                             columns=['Year', 'Data', 'Model'])
        DF_CM.to_csv(f'{self.Directory}/Results/Figures/Carbon_Match.csv', index=False)
        
        # -------------- #
        # Record Results #
        # -------------- #
        Calibrate_Results.add('Climate Persistence Parameter', gpf.clean_round(self.E.ψ, 3))
        Calibrate_Results.add('Climate Absorption Parameter', gpf.clean_round(self.E.ψ_0, 3))
        
        Calibrate_Results.add('General to General Citation Share', gpf.clean_round(self.E.φ_tilde_0[-1,-1]*100, 1))
        
        cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        S_θ_nu = cal_panel.loc[(cal_panel.year >= 2000) & (cal_panel.year <= 2020), ['S_car','S_elec']].to_numpy()
        Mom_nu = np.mean(S_θ_nu, 0)
        
        Calibrate_Results.add('Average Income Share for Transport', gpf.clean_round(Mom_nu[0]*100, 1))
        Calibrate_Results.add('Average Income Share for Electricity', gpf.clean_round(Mom_nu[1]*100, 1))
        Calibrate_Results.add('CES Share for Transport', gpf.clean_round(self.E.ν[0], 3))
        Calibrate_Results.add('CES Share for Electricity', gpf.clean_round(self.E.ν[1], 3))
        
        Calibrate_Results.to_csv(f'{self.Directory}/Results/Tables/Calibrate_Results.csv')
        
    
    
    def SpillAnalysis(self):
        "Spillover Network Analysis"
        
        # ----------------------------------------------------------------

        # Spillover network heat map.

        # ----------------------------------------------------------------

        tech_label_list = ['Clean Car', 'Dirty Car', 'Clean Elec', 'Dirty Elec', 'Gen']
        fig, ax = plt.subplots(1,1)
        img = ax.matshow(self.E.φ_tilde_0[:-1,:])
        ax.set_xticks([0,1,2,3,4])
        ax.set_xticklabels(tech_label_list)
        ax.set_yticks([0,1,2,3])
        ax.set_yticklabels(tech_label_list[:-1])
        ax.set(xlabel='Sender', ylabel='Receiver')
        ax.xaxis.set_label_position('top')
        fig.colorbar(img)
        plt.savefig(f'{self.Directory}/Results/Figures/Spillover_Network.png', bbox_inches='tight', pad_inches=0.01, dpi=666)
        plt.show()
        
        
        # ----------------------------------------------------------------

        # Stability of clean centrality.

        # ----------------------------------------------------------------

        spill_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/spillover_stability.dta')
        
        citer = spill_panel['tech_citer'].unique()
        citee = spill_panel['tech_citee'].unique()
        years = spill_panel['t_int'].unique()

        citer_index = {value: idx for idx, value in enumerate(sorted(citer))}        
        citee_index = {value: idx for idx, value in enumerate(sorted(citee))}
        year_index = {value: idx for idx, value in enumerate(sorted(years))}

        φ_tilde_t = np.zeros((len(citer), len(citee), len(years)))

        for _, row in spill_panel.iterrows():
            r_idx = citer_index[row['tech_citer']]
            s_idx = citee_index[row['tech_citee']]
            y_idx = year_index[row['t_int']]
            φ_tilde_t[r_idx, s_idx, y_idx] = row['φ_tilde']
            
        clean_centrality = np.zeros((φ_tilde_t.shape[2], 2))
        for t in range(φ_tilde_t.shape[2]):
            κ = np.linalg.eig(φ_tilde_t[:,:,t].T)[0]
            unit = np.argmin(np.abs(κ-1))
            Cent = np.linalg.eig(φ_tilde_t[:,:,t].T)[1][:,unit]
            Cent = Cent / np.sum(Cent)*100
            clean_centrality[t,0] = Cent[0]
            clean_centrality[t,1] = Cent[2]
            
        DF_cleancent = pd.DataFrame(np.hstack((years.reshape((-1,1)), clean_centrality)), 
                             columns=['Year', 'Clean Transport Centrality', 'Clean Electricity Centrality'])
        DF_cleancent.to_csv(f'{self.Directory}/Results/Figures/Clean_Centrality.csv', index=False)
        
        
        # ----------------------------------------------------------------

        # Centrality in disaggregrated network.

        # ----------------------------------------------------------------
        
        Disagg_Results = gpf.ResultsTable()
        
        # ----------------------- #
        # Compute Citation Shares #
        # ----------------------- #
        df_cpc = pd.read_stata(f'{self.Directory}/Empirical/Raw Data/cpc_current.dta')
        df_cpc = df_cpc[['patent_id', 'subsection_id']]
        
        df_relevant = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/relevant_patents.dta')
        df_relevant = df_relevant[
            [
                'patent_id',
                'gen_patent',
                'car_clean_patent',
                'car_dirty_patent',
                'elec_clean_patent',
                'elec_dirty_patent'
            ]
        ]
        
       
        df_tech = pd.merge(
            df_relevant,
            df_cpc,
            on='patent_id',
            how='inner'
        )
        
        del df_cpc, df_relevant
                
        # Keep only one observation for each climate patent
        df_clim = df_tech[df_tech['gen_patent'] == 0].drop_duplicates(subset='patent_id', keep='first')
        df_gen = df_tech[df_tech['gen_patent'] == 1]
        df_merged = pd.concat([df_clim, df_gen], ignore_index=True)
        
        del df_tech, df_clim, df_gen
        
        # Weight general patents for consistency with base case
        df_merged['citee_weight'] = 1 / df_merged.groupby('patent_id')['patent_id'].transform('count')
        
     
        long_data = []
        for _, row in df_merged.iterrows():
            if row['gen_patent'] == 1:
                # Only subsection_id as tech_class
                long_data.append((row['patent_id'], row['subsection_id'], row['citee_weight']))
            else:
                # For each of these four flags, add a row if flag == 1
                if row['car_clean_patent'] == 1:
                    long_data.append((row['patent_id'], 'car_clean_patent', row['citee_weight']))
                if row['car_dirty_patent'] == 1:
                    long_data.append((row['patent_id'], 'car_dirty_patent', row['citee_weight']))
                if row['elec_clean_patent'] == 1:
                    long_data.append((row['patent_id'], 'elec_clean_patent', row['citee_weight']))
                if row['elec_dirty_patent'] == 1:
                    long_data.append((row['patent_id'], 'elec_dirty_patent', row['citee_weight']))
        
        df_long = pd.DataFrame(long_data, columns=['patent_id', 'tech_class', 'citee_weight'])
        
        del df_merged, long_data
        
        
        df_citations  = pd.read_stata(f'{self.Directory}/Empirical/Raw Data/uspatentcitation.dta')
        df_citations = df_citations[['patent_id', 'citation_id']]
        
        df_cite_matrix = pd.merge(
            df_long,
            df_citations,
            on='patent_id',
            how='inner'
        )
            
        del df_citations
        
        df_cite_matrix = df_cite_matrix[['tech_class', 'citation_id']]
        df_cite_matrix.rename(columns={'tech_class': 'citer_tech_class', 'citation_id': 'patent_id'}, inplace=True)
        
        df_cite_matrix = df_cite_matrix.groupby(['citer_tech_class', 'patent_id']).size().reset_index(name='citer_weight')
        
        df_cite_matrix = pd.merge(
            df_cite_matrix,
            df_long,
            on='patent_id',
            how='inner'
        )

        del df_long
        df_cite_matrix['cite_weight'] = df_cite_matrix['citer_weight'] * df_cite_matrix['citee_weight']
        df_cite_matrix.rename(columns={'tech_class': 'citee_tech_class'}, inplace=True)
        df_cite_matrix = df_cite_matrix[['citer_tech_class', 'citee_tech_class', 'cite_weight']]
        
        
        df_cite_matrix['total_cites'] = df_cite_matrix.groupby('citer_tech_class')['cite_weight'].transform('sum')
        df_cite_matrix['pairwise_cites'] = df_cite_matrix.groupby(['citer_tech_class', 'citee_tech_class'])['cite_weight'].transform('sum')
        df_cite_matrix['pairwise_cite_share'] = df_cite_matrix['pairwise_cites'] / df_cite_matrix['total_cites']
        
        df_cite_matrix = df_cite_matrix[['citer_tech_class', 'citee_tech_class', 'pairwise_cite_share']]
        df_cite_matrix = df_cite_matrix.drop_duplicates()
        
        
        # ------------------------ #
        # Gross Spillover Matrices #
        # ------------------------ #
        priority_order = [
            'car_clean_patent',
            'car_dirty_patent',
            'elec_clean_patent',
            'elec_dirty_patent'
        ]
        
        all_tech_classes = set(df_cite_matrix['citer_tech_class']).union(
            df_cite_matrix['citee_tech_class']
        )
        
        non_priority_classes = sorted(all_tech_classes - set(priority_order))
        ordered_classes = priority_order + non_priority_classes
        
        df_pivot = df_cite_matrix.pivot(
            index='citer_tech_class',
            columns='citee_tech_class',
            values='pairwise_cite_share'
        )
        
        df_pivot = df_pivot.reindex(index=ordered_classes, columns=ordered_classes, fill_value=0)
        df_pivot.fillna(0, inplace=True)
        
        disagg_spill_matrix = df_pivot.values
        
        
        # ---------------------- #
        # Eigenvector Centrality #
        # ---------------------- #
        κ = np.linalg.eig(disagg_spill_matrix.T)[0]
        unit = np.argmin(np.abs(κ-1))
        Cent = np.real(np.linalg.eig(disagg_spill_matrix.T)[1][:,unit])
        Cent = np.round(Cent / np.sum(Cent)*100, 2)
        
        Disagg_Results.add('Disaggregated Eigenvector Centrality for Clean Transport', Cent[0])
        Disagg_Results.add('Disaggregated Eigenvector Centrality for Dirty Transport', Cent[1])
        Disagg_Results.add('Disaggregated Eigenvector Centrality for Clean Electricity', Cent[2])
        Disagg_Results.add('Disaggregated Eigenvector Centrality for Dirty Electricity', Cent[3])
        
        Disagg_Results.to_csv(f'{self.Directory}/Results/Tables/Disagg_Results.csv')
        
        
        
    def TensGraph(self, Year_start, Year_end):
        "Graph Match of 2010s Experience"
        
        Tens_Results = gpf.ResultsTable()
        
        # ---------------------- #
        # Derive Simulated Paths #
        # ---------------------- #
        (q_θc, q_θc_low, A_start, ξ_0, ξ_0low) = self.E.TensMatch(Year_start, Year_end)
        
        # -------------- #
        # Empirical Path #
        # -------------- #
        cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        
        q_car_clean = cal_panel.loc[(cal_panel.year >= Year_start) & (cal_panel.year <= Year_end), ['q_car_clean']].to_numpy()
        q_elec_clean = cal_panel.loc[(cal_panel.year >= Year_start) & (cal_panel.year <= Year_end), ['q_elec_clean']].to_numpy()
        
        # ------------------------------- #
        # Plot Quantity Share Predictions #
        # ------------------------------- #
        DF_tens = pd.DataFrame(np.hstack((np.arange(Year_start, Year_end+1).reshape((-1,1)), q_car_clean.reshape((-1,1)), q_elec_clean.reshape((-1,1)), q_θc, q_θc_low)), 
                             columns=['Year', 'Data_Transport', 'Data_Electricity', 'Model_Transport', 'Model_Electricity', 'Model_Transport_Low', 'Model_Electricity_Low'])
        DF_tens.to_csv(f'{self.Directory}/Results/Figures/2010s_Transition.csv', index=False)

        
        # ----------------- #
        # Spectral Analysis #
        # ----------------- #
        J = 2*self.E.Θ + 1
        r_tilde = (1-self.E.ξbar_0)*self.E.r
        Abar_start = pf.var_bar(A_start, J)
        
        Abar_ss = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde, ξ_0, self.E.Θ, self.E.o)
        Jake = ssf.Jacob(Abar_ss, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o) 
        κ = np.linalg.eig(Jake)[0]
        Q = np.linalg.eig(Jake)[1]
        A_fan = np.log(Abar_start) - np.log(Abar_ss)
        β = np.linalg.inv(Q) @ A_fan
        
        HL = ssf.Half_Life(Q, κ, β, self.E.Θ)
        
        φ_hat_low = np.eye(J)
        Abar_ss_low = ssf.Abar_SS(self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde, ξ_0low, self.E.Θ, self.E.o)
        Jake_low = ssf.Jacob(Abar_ss_low, self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, r_tilde, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o) 
        κ_low = np.linalg.eig(Jake_low)[0]
        
        # -------------- #
        # Record Results #
        # -------------- #
        Tens_Results.add('2010s Input Subsidy for Clean Transport', gpf.clean_round(self.E.ξbar_0[0], 3))
        Tens_Results.add('2010s Input Subsidy for Clean Electricity', gpf.clean_round(self.E.ξbar_0[2], 3))
        Tens_Results.add('2010s Innovation Subsidy for Clean Transport', gpf.clean_round(ξ_0[0], 3))
        Tens_Results.add('2010s Innovation Subsidy for Dirty Transport', gpf.clean_round(ξ_0[1], 3))
        Tens_Results.add('2010s Innovation Subsidy for Clean Electricity', gpf.clean_round(ξ_0[2], 3))
        Tens_Results.add('2010s Innovation Subsidy for Dirty Electricity', gpf.clean_round(ξ_0[3], 3))
        Tens_Results.add('2010s Innovation Subsidy for Clean Transport (No Spillover)', gpf.clean_round(ξ_0low[0], 3))
        Tens_Results.add('2010s Innovation Subsidy for Dirty Transport (No Spillover)', gpf.clean_round(ξ_0low[1], 3))
        Tens_Results.add('2010s Innovation Subsidy for Clean Electricity (No Spillover)', gpf.clean_round(ξ_0low[2], 3))
        Tens_Results.add('2010s Innovation Subsidy for Dirty Electricity (No Spillover)', gpf.clean_round(ξ_0low[3], 3))
        
        Tens_Results.add('2021 Clean Quantity Share for Transport (Data)', gpf.clean_round(100*q_car_clean[-1,0], 1))
        Tens_Results.add('2021 Clean Quantity Share for Electricity (Data)', gpf.clean_round(100*q_elec_clean[-1,0], 1))
        Tens_Results.add('2010 Clean Quantity Share for Transport (Data)', gpf.clean_round(100*q_car_clean[0,0], 1))
        Tens_Results.add('2010 Clean Quantity Share for Electricity (Data)', gpf.clean_round(100*q_elec_clean[0,0], 1))
        Tens_Results.add('2021 Clean Quantity Share for Transport', gpf.clean_round(100*q_θc[-1,0], 1))
        Tens_Results.add('2021 Clean Quantity Share for Electricity', gpf.clean_round(100*q_θc[-1,1], 1))
        Tens_Results.add('2021 Clean Quantity Share for Transport (No Spillover)', gpf.clean_round(100*q_θc_low[-1,0], 1))
        Tens_Results.add('2021 Clean Quantity Share for Electricity (No Spillover)', gpf.clean_round(100*q_θc_low[-1,1], 1))
        
        Tens_Results.add('2010s Spectral Radius', gpf.clean_round(np.max(np.abs(κ)), 3))
        Tens_Results.add('2010s Half-Life for Transportation', HL[0])
        Tens_Results.add('2010s Half-Life for Electricity', HL[1])
        Tens_Results.add('2010s Spectral Radius (No Spillover)', gpf.clean_round(np.max(np.abs(κ_low)), 3))
        
        Tens_Results.to_csv(f'{self.Directory}/Results/Tables/Tens_Results.csv')
        
        
        
    def PolicyExperiments(self, T_time):
        "Processing of Policy Experiments"
        
        J = 2*self.E.Θ + 1
        X = ssf.X_mat(self.E.Θ)
        I = np.eye(J-1)
        Abar_0 = pf.var_bar(self.E.A_0, J)
        
        PolicyX_Results = gpf.ResultsTable()
        
        
        # ---------------------------- #
        # Derive Hypothetical Policies #
        # ---------------------------- #
        cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        
        Y_start = cal_panel.loc[cal_panel.year == self.E.Year_0, ['GDP']].to_numpy()[0,0]
        
        τ_biden_dollar_low = 51
        τ_biden_dollar_high = 190
        
        τ_biden_low = (self.E.Y0 / Y_start) * τ_biden_dollar_low * (self.CO2_C**(-1))
        τ_biden_high = (self.E.Y0 / Y_start) * τ_biden_dollar_high * (self.CO2_C**(-1))
        
        r_tilde_low = self.E.r + self.E.ω * τ_biden_low
        r_tilde_high = self.E.r + self.E.ω * τ_biden_high
        
        ξ_lf = np.ones(J)
        ξ_clean = 1/0.7
        ξ_cleansub = np.array([ξ_clean, 1, ξ_clean, 1, 1])
        
        cases = ["Low Biden Carbon Price", "High Biden Carbon Price"]
        
        
        # ------------------------------ #
        # Alternative Spillover Networks #
        # ------------------------------ #
        φ_hat_low = np.eye(J)
        
        φtilde_noθ = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/citation_shares.dta').to_numpy()
        for θ in range(self.E.Θ):
            φtilde_noθ[2*θ,2*θ] = self.E.φ_tilde_0[2*θ,2*θ] + self.E.φ_tilde_0[2*θ,2*θ+1]
            φtilde_noθ[2*θ,2*θ+1] = 0

        for θ in range(self.E.Θ):
            φtilde_noθ[2*θ+1,2*θ+1] = self.E.φ_tilde_0[2*θ+1,2*θ+1] + self.E.φ_tilde_0[2*θ+1,2*θ]
            φtilde_noθ[2*θ+1,2*θ] = 0
                    
        φtilde_nogen = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/citation_shares.dta').to_numpy()
        φtilde_nogen = φtilde_nogen + np.diag(np.append(φtilde_nogen[:-1,-1],0))
        φtilde_nogen[:-1,-1] = np.zeros(J-1)
        
        φ_Dub = 2*self.E.φ_tilde_0 + (1-2) * np.eye(J) #Only works for Cobb-Douglas
            
        
        # ------------------------------ #
        # Comparison of Linearized Model #
        # ------------------------------ #
        Abar_ss = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
        Jake = ssf.Jacob(Abar_ss, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        A_fan_0 = np.log(Abar_0) - np.log(Abar_ss)
        
        A_real = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, self.E.φ_hat, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)[1]
        Abar_real = pf.var_bar(A_real, J)
        Afan_real = np.log(Abar_real) - np.log(np.tile(Abar_ss, (T_time+1,1)))
        
        Afan_lin = np.zeros((T_time+1, J-1))
        Afan_lin[0,:] = A_fan_0
        
        for t in range(1,T_time+1):
            Afan_lin[t,:] = Jake @ Afan_lin[t-1,:]
        
        Bfan_real = Afan_real @ X.T
        Bfan_lin = Afan_lin @ X.T
        
        DF_Lin = pd.DataFrame(np.hstack((np.arange(self.E.Year_0, self.E.Year_0+T_time+1).reshape((-1,1)), Bfan_lin, Bfan_real)), 
                             columns=['Year', 'Bfan_lin_Transport', 'Bfan_lin_Electricity', 'Bfan_real_Transport', 'Bfan_real_Electricity'])
        DF_Lin.to_csv(f'{self.Directory}/Results/Figures/LinearCompare.csv', index=False)

        
        # ------------------------ #
        # Tables of Policy Impacts #
        # ------------------------ #
        Abar_ss_lf = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, self.E.r, ξ_lf, self.E.Θ, self.E.o)
        Amy_lf = ssf.Amp(Abar_ss_lf, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.r, self.E.Θ, self.E.o)
        Σ_lf = ssf.Sigma(Abar_ss_lf, self.E.r, self.E.α, self.E.σ, self.E.λ, self.E.Θ)
        
        Abar_ss_lowlf = ssf.Abar_SS(self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.ν, self.E.r, ξ_lf, self.E.Θ, self.E.o)
        Amy_lowlf = ssf.Amp(Abar_ss_lowlf, self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.r, self.E.Θ, self.E.o)
        Σ_lowlf = ssf.Sigma(Abar_ss_lowlf, self.E.r, self.E.α, self.E.σ, self.E.λ, self.E.Θ)
        
        Abar_ss_Dublf = ssf.Abar_SS(self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, self.E.ν, self.E.r, ξ_lf, self.E.Θ, self.E.o)
        Amy_Dublf = ssf.Amp(Abar_ss_Dublf, self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, self.E.r, self.E.Θ, self.E.o)
        Σ_Dublf = ssf.Sigma(Abar_ss_Dublf, self.E.r, self.E.α, self.E.σ, self.E.λ, self.E.Θ)
        
        ωbar_ss_lf = pf.omega_bar(self.E.r, np.append(Abar_ss_lf,1), self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        ωbar_sscorn_lowlf = ssf.omega_bar_corn(self.E.α, self.E.λ, self.E.ν, self.E.ω, self.E.r, ξ_lf, self.E.Θ, 1, 1)
        ωbar_ss_Dublf = pf.omega_bar(self.E.r, np.append(Abar_ss_Dublf,1), self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        
        A_lf = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, self.E.φ_hat, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Em_35_lf = pf.GHG(self.E.r, A_lf[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        Em_60_lf = pf.GHG(self.E.r, A_lf[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)        
        
        A_lowlf = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, φ_hat_low, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Em_35_lowlf = pf.GHG(self.E.r, A_lowlf[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        Em_60_lowlf = pf.GHG(self.E.r, A_lowlf[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        
        A_Dublf = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, φ_Dub, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Em_35_Dublf = pf.GHG(self.E.r, A_Dublf[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        Em_60_Dublf = pf.GHG(self.E.r, A_Dublf[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
        
        for c in cases:
            if c == "Low Biden Carbon Price":
                r_tilde_impact = r_tilde_low
                ξ_impact = ξ_cleansub
                car_tech = 1
                elec_tech = 0
            if c == "High Biden Carbon Price":
                r_tilde_impact = r_tilde_high
                ξ_impact = ξ_cleansub
                car_tech = 1
                elec_tech = 0
        
            dlnR = np.log(pf.var_bar(r_tilde_impact, J)) - np.log(pf.var_bar(self.E.r, J))
            dlnΞ = np.log(pf.var_bar(ξ_impact, J)) - np.log(pf.var_bar(ξ_lf, J))
            
            Abar_ss_impact = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)
            Jake_impact = ssf.Jacob(Abar_ss_impact, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde_impact, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            κ_impact = np.linalg.eig(Jake_impact)[0]
            
            Abar_ss_low_impact = ssf.Abar_SS(self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)
            Jake_low_impact = ssf.Jacob(Abar_ss_low_impact, self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, r_tilde_impact, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            κ_low_impact = np.linalg.eig(Jake_low_impact)[0]
            
            Abar_ss_Dub_impact = ssf.Abar_SS(self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)
            Jake_Dub_impact = ssf.Jacob(Abar_ss_Dub_impact, self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, r_tilde_impact, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            κ_Dub_impact = np.linalg.eig(Jake_Dub_impact)[0]
            
            dlnAbar_ss = self.E.η * Amy_lf @ (dlnΞ - self.E.α * (Σ_lf - I) @ dlnR)
            dlnBbar_ss = dlnAbar_ss @ X.T * 100
            
            dlnAbar_sslow = self.E.η * Amy_lowlf @ (dlnΞ - self.E.α * (Σ_lowlf - I) @ dlnR)
            dlnBbar_sslow = dlnAbar_sslow @ X.T * 100
            
            dlnAbar_ssDub = self.E.η * Amy_Dublf @ (dlnΞ - self.E.α * (Σ_Dublf - I) @ dlnR)
            dlnBbar_ssDub = dlnAbar_ssDub @ X.T * 100
            
            ωbar_ss = pf.omega_bar(r_tilde_impact, np.append(Abar_ss_impact,1), self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            Δω_bar = ((ωbar_ss - ωbar_ss_lf)/ωbar_ss_lf) * 100
            
            ωbar_sscorn_low = ssf.omega_bar_corn(self.E.α, self.E.λ, self.E.ν, self.E.ω, r_tilde_impact, ξ_impact, self.E.Θ, car_tech, elec_tech)
            Δω_bar_low = ((ωbar_sscorn_low - ωbar_sscorn_lowlf)/ωbar_sscorn_lowlf) * 100
            
            ωbar_ss_Dub = pf.omega_bar(r_tilde_impact, np.append(Abar_ss_Dub_impact,1), self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            Δω_bar_Dub = ((ωbar_ss_Dub - ωbar_ss_Dublf)/ωbar_ss_Dublf) * 100
            
            A_impact = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, self.E.φ_hat, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Em_35 = pf.GHG(r_tilde_impact, A_impact[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_35 = ((Em_35 - Em_35_lf)/Em_35_lf) * 100
            Em_60 = pf.GHG(r_tilde_impact, A_impact[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_60 = ((Em_60 - Em_60_lf)/Em_60_lf) * 100
            
            A_impact_low = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, φ_hat_low, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Em_35low = pf.GHG(r_tilde_impact, A_impact_low[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_35low = ((Em_35low - Em_35_lowlf)/Em_35_lowlf) * 100
            Em_60low = pf.GHG(r_tilde_impact, A_impact_low[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_60low = ((Em_60low - Em_60_lowlf)/Em_60_lowlf) * 100
            
            A_impact_Dub = of.Eqbm_Path(self.E.A_0, 2060 - self.E.Year_0, self.E.η, φ_Dub, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Em_35_Dub = pf.GHG(r_tilde_impact, A_impact_Dub[2035 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_35_Dub = ((Em_35_Dub - Em_35_Dublf)/Em_35_Dublf) * 100
            Em_60_Dub = pf.GHG(r_tilde_impact, A_impact_Dub[2060 - self.E.Year_0,:], self.E.α, self.E.σ, self.E.λ, self.E.ν, 1, self.E.L, self.E.ω, self.E.Θ)
            ΔEm_60_Dub = ((Em_60_Dub - Em_60_Dublf)/Em_60_Dublf) * 100
            
            PolicyX_Results.add(f'{c} First-Order Change in Transport Relative Technology', gpf.clean_round(dlnBbar_ss[0], 1))
            PolicyX_Results.add(f'{c} First-Order Change in Electricity Relative Technology', gpf.clean_round(dlnBbar_ss[1], 1))
            PolicyX_Results.add(f'{c} Change in Emissions Intensity', gpf.clean_round(Δω_bar[0], 1))
            PolicyX_Results.add(f'{c} Change in 2035 Emissions', gpf.clean_round(ΔEm_35[0], 1))
            PolicyX_Results.add(f'{c} Change in 2060 Emissions', gpf.clean_round(ΔEm_60[0], 1))
            PolicyX_Results.add(f'{c} Spectral Radius', gpf.clean_round(np.max(np.abs(κ_impact)), 3))
            
            PolicyX_Results.add(f'{c} First-Order Change in Transport Relative Technology (No Spillovers)', -gpf.clean_round(dlnBbar_sslow[0], 1))
            PolicyX_Results.add(f'{c} First-Order Change in Electricity Relative Technology (No Spillovers)', -gpf.clean_round(dlnBbar_sslow[1], 1))
            PolicyX_Results.add(f'{c} Change in Emissions Intensity (No Spillovers)', gpf.clean_round(Δω_bar_low[0], 1))
            PolicyX_Results.add(f'{c} Change in 2035 Emissions (No Spillovers)', gpf.clean_round(ΔEm_35low[0], 1))
            PolicyX_Results.add(f'{c} Change in 2060 Emissions (No Spillovers)', gpf.clean_round(ΔEm_60low[0], 1))
            PolicyX_Results.add(f'{c} Spectral Radius (No Spillovers)', gpf.clean_round(np.max(np.abs(κ_low_impact)), 3))
            
            PolicyX_Results.add(f'{c} First-Order Change in Transport Relative Technology (Double Spillovers)', gpf.clean_round(dlnBbar_ssDub[0], 1))
            PolicyX_Results.add(f'{c} First-Order Change in Electricity Relative Technology (Double Spillovers)', gpf.clean_round(dlnBbar_ssDub[1], 1))
            PolicyX_Results.add(f'{c} Change in Emissions Intensity (Double Spillovers)', gpf.clean_round(Δω_bar_Dub[0], 1))
            PolicyX_Results.add(f'{c} Change in 2035 Emissions (Double Spillovers)', gpf.clean_round(ΔEm_35_Dub[0], 1))
            PolicyX_Results.add(f'{c} Change in 2060 Emissions (Double Spillovers)', gpf.clean_round(ΔEm_60_Dub[0], 1))
            PolicyX_Results.add(f'{c} Spectral Radius (Double Spillovers)', gpf.clean_round(np.max(np.abs(κ_Dub_impact)), 3))
        
        
        # --------------------------- #
        # Figures of Technology Paths #
        # --------------------------- #
        A_lf = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, self.E.φ_hat, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Abar_lf = pf.var_bar(A_lf, J)
        lnBbar_lf = np.log(Abar_lf) @ X.T
        
        A_lowlf = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, φ_hat_low, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Abar_lowlf = pf.var_bar(A_lowlf, J)
        lnBbar_lowlf = np.log(Abar_lowlf) @ X.T
       
        A_Dublf = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, φ_Dub, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, self.E.r, ξ_lf, self.E.Θ, self.E.o)[1]
        Abar_Dublf = pf.var_bar(A_Dublf, J)
        lnBbar_Dublf = np.log(Abar_Dublf) @ X.T
       
        for c in cases:
            if c == "Low Biden Carbon Price":
                r_tilde_impact = r_tilde_low
                ξ_impact = ξ_cleansub
                file = "Bidenlow"
            if c == "High Biden Carbon Price":
                r_tilde_impact = r_tilde_high
                ξ_impact = ξ_cleansub
                file = "Bidenhigh"
           
            A = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, self.E.φ_hat, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Abar = pf.var_bar(A, J)
            lnBbar = np.log(Abar) @ X.T
           
            A_low = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, φ_hat_low, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Abar_low = pf.var_bar(A_low, J)
            lnBbar_low = np.log(Abar_low) @ X.T
            
            A_Dub = of.Eqbm_Path(self.E.A_0, T_time, self.E.η, φ_Dub, self.E.χ, self.E.γ, self.E.α, self.E.λ, self.E.ν, self.E.σ, self.E.L, r_tilde_impact, ξ_impact, self.E.Θ, self.E.o)[1]
            Abar_Dub = pf.var_bar(A_Dub, J)
            lnBbar_Dub = np.log(Abar_Dub) @ X.T
           
            DF_techpath = pd.DataFrame(np.hstack((np.arange(self.E.Year_0, self.E.Year_0+T_time+1).reshape((-1,1)), lnBbar_lf, lnBbar, lnBbar_lowlf, lnBbar_low, lnBbar_Dublf, lnBbar_Dub)), 
                                 columns=['Year', 'lnBbar_lf_Transport', 'lnBbar_lf_Electricity', 'lnBbar_Transport', 'lnBbar_Electricity', 'lnBbar_lowlf_Transport', 'lnBbar_lowlf_Electricity', 'lnBbar_low_Transport', 'lnBbar_low_Electricity', 'lnBbar_Dublf_Transport', 'lnBbar_Dublf_Electricity', 'lnBbar_Dub_Transport', 'lnBbar_Dub_Electricity'])
            DF_techpath.to_csv(f'{self.Directory}/Results/Figures/TechPath{file}.csv', index=False)
            
            
        # --------------------------------------------------- #
        # Spectral Radius for Applicant Only Citation Network #
        # --------------------------------------------------- #
        φ_tilde_ao = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/citation_shares_applicant.dta').to_numpy()
        
        Abar_ss_ao = ssf.Abar_SS(self.E.η, φ_tilde_ao, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
        Jake_ao = ssf.Jacob(Abar_ss_ao, self.E.η, φ_tilde_ao, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_ao = np.linalg.eig(Jake_ao)[0]
        
        PolicyX_Results.add('Applicant Only Spectral Radius', gpf.clean_round(np.max(np.abs(κ_ao)), 3))
        
        
        # ----------------------------------- #
        # Basins of Attraction by Policy Tool #
        # ----------------------------------- #
        
        #Carbon Price
        P = 2000
        τ_dollar_pd = np.linspace(0, P, P)
        τ_pd = (self.E.Y0 / Y_start) * τ_dollar_pd * (self.CO2_C**(-1))
        
        r_tilde_pd = np.zeros((P, J))
        Abar_ss_low_pd = np.zeros((P, J-1))
        Jake_low_pd = np.zeros((P, J-1, J-1))
        A_fan_low_pd = np.zeros((P, J-1))
        ΔB_fan_low_pd = np.zeros((P, self.E.Θ))
        
        for p in range(P):
            r_tilde_pd[p,:] = self.E.r + self.E.ω * τ_pd[p]
            Abar_ss_low_pd[p,:] = ssf.Abar_SS(self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_pd[p,:], ξ_cleansub, self.E.Θ, self.E.o)
            Jake_low_pd[p,:,:] = ssf.Jacob(Abar_ss_low_pd[p,:], self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, r_tilde_pd[p,:], self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            A_fan_low_pd[p,:] = np.log(Abar_0) - np.log(Abar_ss_low_pd[p,:])
            ΔB_fan_low_pd[p,:] = X @ (Jake_low_pd[p,:,:] - I) @ A_fan_low_pd[p,:] * 100
        
        PolicyX_Results.add('Carbon Price for Clean Growth in Transport (No Spillover)', int(τ_dollar_pd[np.argmin(np.abs(ΔB_fan_low_pd[:,0]))]))
        PolicyX_Results.add('Carbon Price for Clean Growth in Electricity (No Spillover)', int(τ_dollar_pd[np.argmin(np.abs(ΔB_fan_low_pd[:,1]))]))
    
        
        τ_dollar_pd = τ_dollar_pd[:500]
        ΔB_fan_low_pd = ΔB_fan_low_pd[:500,:]
        
        DF_taxbasin = pd.DataFrame(np.hstack((τ_dollar_pd.reshape((-1,1)), ΔB_fan_low_pd)), 
                             columns=['τ_dollar_pd', 'ΔB_fan_low_pd_Transport', 'ΔB_fan_low_pd_Electricity'])
        DF_taxbasin.to_csv(f'{self.Directory}/Results/Figures/BasinsTax.csv', index=False)
        
        
        #Innovation Subsidies
        ξ_clean_pd = np.linspace(1, 5, P).reshape((P,1))
        ξ_pd = np.hstack((ξ_clean_pd, np.ones((P,1)), ξ_clean_pd, np.ones((P,1)), np.ones((P,1))))
        
        Abar_ss_low_subpd = np.zeros((P, J-1))
        Jake_low_subpd = np.zeros((P, J-1, J-1))
        A_fan_low_subpd = np.zeros((P, J-1))
        ΔB_fan_low_subpd = np.zeros((P, self.E.Θ))
        
        for p in range(P):
            Abar_ss_low_subpd[p,:] = ssf.Abar_SS(self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_pd[p,:], self.E.Θ, self.E.o)
            Jake_low_subpd[p,:,:] = ssf.Jacob(Abar_ss_low_subpd[p,:], self.E.η, φ_hat_low, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            A_fan_low_subpd[p,:] = np.log(Abar_0) - np.log(Abar_ss_low_subpd[p,:])
            ΔB_fan_low_subpd[p,:] = X @ (Jake_low_subpd[p,:,:] - I) @ A_fan_low_subpd[p,:] * 100
        
        PolicyX_Results.add('Clean Innovation Subsidy for Clean Growth in Transport (No Spillover)', gpf.clean_round(ξ_clean_pd[np.argmin(np.abs(ΔB_fan_low_subpd[:,0])),0], 2))
        PolicyX_Results.add('Clean Innovation Subsidy for Clean Growth in Electricity (No Spillover)', gpf.clean_round(ξ_clean_pd[np.argmin(np.abs(ΔB_fan_low_subpd[:,1])),0], 2))
        
        ξ_clean_pd = ξ_clean_pd[:500]
        ΔB_fan_low_subpd = ΔB_fan_low_subpd[:500,:]
        
        DF_subbasin = pd.DataFrame(np.hstack((ξ_clean_pd.reshape((-1,1)), ΔB_fan_low_subpd)), 
                             columns=['ξ_clean_pd', 'ΔB_fan_low_subpd_Transport', 'ΔB_fan_low_subpd_Electricity'])
        DF_subbasin.to_csv(f'{self.Directory}/Results/Figures/BasinsSub.csv', index=False)
        
        
        # --------------------- #
        # Plot Half-Life Charts #
        # --------------------- #
        Abar_ss = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
        Jake = ssf.Jacob(Abar_ss, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ = np.linalg.eig(Jake)[0]
        idx = np.argsort(κ)
        κ = np.sort(κ)
        Q = np.linalg.eig(Jake)[1][:,idx]
        A_fan_0 = np.log(Abar_0) - np.log(Abar_ss)
        β = np.linalg.inv(Q) @ A_fan_0
        t_half_tech = ssf.Half_Life(Q, κ, β, self.E.Θ)
        Δ_half = (t_half_tech[1]/t_half_tech[0] - 1)*100
        t_half = np.concatenate((np.ceil(np.log(1/2)/np.log(κ)), t_half_tech)) * self.E.T
        
        Abar_ss_noθ = ssf.Abar_SS(self.E.η, φtilde_noθ, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
        Jake_noθ = ssf.Jacob(Abar_ss_noθ, self.E.η, φtilde_noθ, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_noθ = np.linalg.eig(Jake_noθ)[0]
        idx_noθ = np.argsort(κ_noθ)
        κ_noθ = np.sort(κ_noθ)
        Q_noθ = np.linalg.eig(Jake_noθ)[1][:,idx_noθ]
        A_fan_0_noθ = np.log(Abar_0) - np.log(Abar_ss_noθ)
        β_noθ = np.linalg.inv(Q_noθ) @ A_fan_0_noθ
        t_half_tech_noθ = ssf.Half_Life(Q_noθ, κ_noθ, β_noθ, self.E.Θ)
        t_half_noθ = np.concatenate((np.ceil(np.log(1/2)/np.log(κ_noθ)), t_half_tech_noθ)) * self.E.T
        
        Abar_ss_Dub = ssf.Abar_SS(self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
        Jake_Dub = ssf.Jacob(Abar_ss_Dub, self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_Dub = np.linalg.eig(Jake_Dub)[0]
        idx_Dub = np.argsort(κ_Dub)
        κ_Dub = np.sort(κ_Dub)
        Q_Dub = np.linalg.eig(Jake_Dub)[1][:,idx_Dub]
        A_fan_0_Dub = np.log(Abar_0) - np.log(Abar_ss_Dub)
        β_Dub = np.linalg.inv(Q_Dub) @ A_fan_0_Dub
        t_half_tech_Dub = ssf.Half_Life(Q_Dub, κ_Dub, β_Dub, self.E.Θ)
        t_half_Dub = np.concatenate((np.ceil(np.log(1/2)/np.log(κ_Dub)), t_half_tech_Dub)) * self.E.T
        
        Abar_ss_nogen = ssf.Abar_SS(self.E.η, φtilde_nogen, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_lf, self.E.Θ, self.E.o)
        Jake_nogen = ssf.Jacob(Abar_ss_nogen, self.E.η, φtilde_nogen, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_nogen = np.linalg.eig(Jake_nogen)[0]
        
        PolicyX_Results.add('Half-Life for ES1', int(t_half[0]))
        PolicyX_Results.add('Half-Life for ES2', int(t_half[1]))
        PolicyX_Results.add('Half-Life for ES3', int(t_half[2]))
        PolicyX_Results.add('Half-Life for ES4', int(t_half[3]))
        PolicyX_Results.add('Half-Life for Transportation', int(t_half[4]))
        PolicyX_Results.add('Half-Life for Electricity', int(t_half[5]))
        PolicyX_Results.add('Percent Difference in Half-Lives', gpf.clean_round(Δ_half,1))
        
        PolicyX_Results.add('Half-Life for ES1 (No Sector Spillovers)', int(t_half_noθ[0]))
        PolicyX_Results.add('Half-Life for ES2 (No Sector Spillovers)', int(t_half_noθ[1]))
        PolicyX_Results.add('Half-Life for ES3 (No Sector Spillovers)', int(t_half_noθ[2]))
        PolicyX_Results.add('Half-Life for ES4 (No Sector Spillovers)', int(t_half_noθ[3]))
        PolicyX_Results.add('Half-Life for Transportation (No Sector Spillovers)', int(t_half_noθ[4]))
        PolicyX_Results.add('Half-Life for Electricity (No Sector Spillovers)', int(t_half_noθ[5]))
        
        PolicyX_Results.add('Half-Life for ES1 (Double Spillovers)', int(t_half_Dub[0]))
        PolicyX_Results.add('Half-Life for ES2 (Double Spillovers)', int(t_half_Dub[1]))
        PolicyX_Results.add('Half-Life for ES3 (Double Spillovers)', int(t_half_Dub[2]))
        PolicyX_Results.add('Half-Life for ES4 (Double Spillovers)', int(t_half_Dub[3]))
        PolicyX_Results.add('Half-Life for Transportation (Double Spillovers)', int(t_half_Dub[4]))
        PolicyX_Results.add('Half-Life for Electricity (Double Spillovers)', int(t_half_Dub[5]))
        
        PolicyX_Results.add('Spectral Radius (No Sector Spillovers)', gpf.clean_round(np.max(np.abs(κ_noθ)), 3))
        PolicyX_Results.add('Spectral Radius (No General Spillovers)', gpf.clean_round(np.max(np.abs(κ_nogen)), 3))
    
        
        Abar_ss_high = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_high, ξ_cleansub, self.E.Θ, self.E.o)
        Jake_high = ssf.Jacob(Abar_ss_high, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde_high, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_high = np.linalg.eig(Jake_high)[0]
        idx_high = np.argsort(κ_high)
        κ_high = np.sort(κ_high)
        Q_high = np.linalg.eig(Jake_high)[1][:,idx_high]
        A_fan_0_high = np.log(Abar_0) - np.log(Abar_ss_high)
        β_high = np.linalg.inv(Q_high) @ A_fan_0_high
        t_half_tech_high = ssf.Half_Life(Q_high, κ_high, β_high, self.E.Θ) * self.E.T
        
        Abar_ss_Dub_high = ssf.Abar_SS(self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_high, ξ_cleansub, self.E.Θ, self.E.o)
        Jake_Dub_high = ssf.Jacob(Abar_ss_Dub_high, self.E.η, φ_Dub, self.E.α, self.E.σ, self.E.λ, r_tilde_high, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
        κ_Dub_high = np.linalg.eig(Jake_Dub_high)[0]
        idx_Dub_high = np.argsort(κ_Dub_high)
        κ_Dub_high = np.sort(κ_Dub_high)
        Q_Dub_high = np.linalg.eig(Jake_Dub_high)[1][:,idx_Dub_high]
        A_fan_0_Dub_high = np.log(Abar_0) - np.log(Abar_ss_Dub_high)
        β_Dub_high = np.linalg.inv(Q_Dub_high) @ A_fan_0_Dub_high
        t_half_tech_Dub_high = ssf.Half_Life(Q_Dub_high, κ_Dub_high, β_Dub_high, self.E.Θ) * self.E.T
        PolicyX_Results.add('Half-Life for Transportation (High Biden Carbon Price)', int(t_half_tech_high[0]))
        PolicyX_Results.add('Half-Life for Electricity (High Biden Carbon Price)', int(t_half_tech_high[1]))
        PolicyX_Results.add('Half-Life for Transportation (High Biden Carbon Price, Double Spillovers)', int(t_half_tech_Dub_high[0]))
        PolicyX_Results.add('Half-Life for Electricity (High Biden Carbon Price, Double Spillovers)', int(t_half_tech_Dub_high[1]))
    
        
        # -------------------------------------------------------- #
        # Determinants of Amplification Matrix & Transition Matrix #
        # -------------------------------------------------------- #
        P = 200
        dlnR = np.log(pf.var_bar(r_tilde_low, J)) - np.log(pf.var_bar(self.E.r, J))
        dlnΞ = np.log(pf.var_bar(ξ_cleansub, J)) - np.log(pf.var_bar(ξ_lf, J))
        
        σ_var_A = np.linspace(1.25, 2.13, P)
        σ_var_J = np.linspace(1.25, 2.35, P)
        Amy_sub = np.zeros((P,J-1,J-1))
        Σ_sub = np.zeros((P,J-1,J-1))
        dlnBbar_sub = np.zeros((P,self.E.Θ))
        Jake_sub = np.zeros((P,J-1,J-1))
        spec_sub = np.zeros(P)
        
        ζ_A = np.linspace(0.8, 1.2, P)
        ζ_J = np.linspace(0.62, 1.1, P)
        Amy_spill = np.zeros((P,J-1,J-1))
        Σ_spill = np.zeros((P,J-1,J-1))
        dlnBbar_spill = np.zeros((P,self.E.Θ))
        Jake_spill = np.zeros((P,J-1,J-1))
        spec_spill = np.zeros(P)
        
        for p in range(P):
            Abar_ss_sublf = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, σ_var_A[p], self.E.λ, self.E.ν, self.E.r, ξ_lf, self.E.Θ, self.E.o)
            Abar_ss_sub = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, σ_var_J[p], self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
            
            Amy_sub[p,:,:] = ssf.Amp(Abar_ss_sublf, self.E.η, self.E.φ_hat, self.E.α, σ_var_A[p], self.E.λ, self.E.r, self.E.Θ, self.E.o)
            Σ_sub[p,:,:] = ssf.Sigma(Abar_ss_sublf, self.E.r, self.E.α, σ_var_A[p], self.E.λ, self.E.Θ)
            dlnBbar_sub[p,:] = self.E.η * Amy_sub[p,:,:] @ (dlnΞ - self.E.α * (Σ_sub[p,:,:] - I) @ dlnR) @ X.T * 100
            
            Jake_sub[p,:,:] = ssf.Jacob(Abar_ss_sub, self.E.η, self.E.φ_hat, self.E.α, σ_var_J[p], self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            spec_sub[p] = np.max(np.abs(np.linalg.eig(Jake_sub[p,:,:])[0]))
            
            φ_var_A = ζ_A[p] * self.E.φ_tilde_0 + (1-ζ_A[p]) * np.eye(J) #Only works for Cobb-Douglas
            φ_var_J = ζ_J[p] * self.E.φ_tilde_0 + (1-ζ_J[p]) * np.eye(J) #Only works for Cobb-Douglas
            Abar_ss_spilllf = ssf.Abar_SS(self.E.η, φ_var_A, self.E.α, self.E.σ, self.E.λ, self.E.ν, self.E.r, ξ_lf, self.E.Θ, self.E.o)
            Abar_ss_spill = ssf.Abar_SS(self.E.η, φ_var_J, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_cleansub, self.E.Θ, self.E.o)
            
            Amy_spill[p,:,:] = ssf.Amp(Abar_ss_spilllf, self.E.η, φ_var_A, self.E.α, self.E.σ, self.E.λ, self.E.r, self.E.Θ, self.E.o)
            Σ_spill[p,:,:] = ssf.Sigma(Abar_ss_spilllf, self.E.r, self.E.α, self.E.σ, self.E.λ, self.E.Θ)
            dlnBbar_spill[p,:] = self.E.η * Amy_spill[p,:,:] @ (dlnΞ - self.E.α * (Σ_spill[p,:,:] - I) @ dlnR) @ X.T * 100
            
            Jake_spill[p,:,:] = ssf.Jacob(Abar_ss_spill, self.E.η, φ_var_J, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            spec_spill[p] = np.max(np.abs(np.linalg.eig(Jake_spill[p,:,:])[0]))
                        
        DF_AD = pd.DataFrame(np.hstack((ζ_A.reshape((-1,1)), σ_var_A.reshape((-1,1)), dlnBbar_spill, dlnBbar_sub)), 
                             columns=['ζ_A', 'σ_var_A', 'dlnBbar_spill_Transport' ,'dlnBbar_spill_Electricity', 'dlnBbar_sub_Transport' ,'dlnBbar_sub_Electricity'])
        DF_AD.to_csv(f'{self.Directory}/Results/Figures/AmpDeterms.csv', index=False)
        
        DF_TD = pd.DataFrame(np.hstack((ζ_J.reshape((-1,1)), σ_var_J.reshape((-1,1)), spec_spill.reshape((-1,1)), spec_sub.reshape((-1,1)))), 
                             columns=['ζ_J', 'σ_var_J', 'spec_spill' ,'spec_sub'])
        DF_TD.to_csv(f'{self.Directory}/Results/Figures/TranDeterms.csv', index=False)
        
        PolicyX_Results.add('Spillover Scale for Path Dependence', gpf.clean_round(ζ_J[np.argmin(np.abs(spec_spill-1))]*100, 1))
        PolicyX_Results.add('ES for Path Dependence', gpf.clean_round(σ_var_J[np.argmin(np.abs(spec_sub-1))], 2))
        
        
        # ---------------------------------- #
        # Policy Effect on Transition Matrix #
        # ---------------------------------- #
        P = 500
        
        τ_var = np.linspace(0, 500, P)
        ξ_clean_var = np.linspace(1, 5, P).reshape((P,1))
        ξ_var = np.hstack((ξ_clean_var, np.ones((P,1)), ξ_clean_var, np.ones((P,1)), np.ones((P,1))))
        
        Jake_τ = np.zeros((P,J-1,J-1))
        Jake_ξ = np.zeros((P,J-1,J-1))
        κ_τ = np.zeros((P,J-1))
        κ_ξ = np.zeros((P,J-1))
        
        for p in range(P):
            r_tilde = self.E.r + self.E.ω * τ_var[p]
            
            Abar_ss_τ_J = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde, ξ_cleansub, self.E.Θ, self.E.o)
            Abar_ss_ξ_J = ssf.Abar_SS(self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, self.E.ν, r_tilde_low, ξ_var[p,:], self.E.Θ, self.E.o)
            
            Jake_τ[p,:,:] = ssf.Jacob(Abar_ss_τ_J, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            Jake_ξ[p,:,:] = ssf.Jacob(Abar_ss_ξ_J, self.E.η, self.E.φ_hat, self.E.α, self.E.σ, self.E.λ, r_tilde_low, self.E.χ, self.E.γ, self.E.Θ, self.E.ν, self.E.o)
            κ_τ[p,:] = np.sort(np.linalg.eig(Jake_τ[p,:,:])[0])
            κ_ξ[p,:] = np.sort(np.linalg.eig(Jake_ξ[p,:,:])[0])
            
        DF_ΤP = pd.DataFrame(np.hstack((τ_var.reshape((-1,1)), ξ_clean_var.reshape((-1,1)), κ_τ, κ_ξ)), 
                             columns=['τ_var', 'ξ_clean_var', 'κ_τ0', 'κ_τ1', 'κ_τ2', 'κ_τ3', 'κ_ξ0', 'κ_ξ1', 'κ_ξ2', 'κ_ξ3'])
        DF_ΤP.to_csv(f'{self.Directory}/Results/Figures/TranPolicy.csv', index=False)
        
        PolicyX_Results.to_csv(f'{self.Directory}/Results/Tables/PolicyX_Results.csv')
        
            
            
    def IAM(self, Periods, T_time):
        "Processing of IAM"
        
        J = 2*self.E.Θ + 1
        IAM_Results = gpf.ResultsTable()
        
        # ----------------------------------------------------------------

        # Benchmark policy paths.

        # ----------------------------------------------------------------
        
        # ----------------- #
        # Load Policy Paths #
        # ----------------- #
        (τ_FB, C_FB, ξtilde_FB, A_FB) = self.E.IAM(Periods, T_time, 1, 0, 0, 0)
        (τ_ten, C_ten, ξtilde_ten, A_ten) = self.E.IAM(Periods, T_time, 0.1, 0, 0, 0)
        (τ_zero, C_zero, ξtilde_zero, A_zero) = self.E.IAM(Periods, T_time, 0, 0, 0, 0)
        
        
        # ---------- #
        # Parameters #
        # ---------- #
        ρ_h = (1+self.E.ρ_h)**self.E.T - 1
        ρ_l = (1+self.E.ρ_l)**self.E.T - 1
        
        cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        
        Y_start = cal_panel.loc[cal_panel.year == self.E.Year_0, ['GDP']].to_numpy()[0,0]
        
        r_adjust = np.tile(self.E.r.reshape((1,J)), (T_time, 1))
        ν_adjust = np.tile(self.E.ν.reshape((1,self.E.Θ+1)), (T_time, 1))
        ω_adjust = np.tile(self.E.ω.reshape((1,J)), (T_time, 1))
        
        C_ω = cal_panel.loc[(cal_panel.year >= 2000) & (cal_panel.year <= 2020), ['car_C_relem','elec_C_relem']].to_numpy()
        relEm = np.sum(np.mean(C_ω, 0))
        IAM_Results.add('Average US Emission Share of Transport and Electricity', gpf.clean_round(relEm*100, 1))


        # -------------------------- #
        # Make Policy Comprehensible #
        # -------------------------- #
        τ_FB_dollar = τ_FB * (Y_start / self.E.Y0) * (self.CO2_C)
        
        X_τ = np.ones((1,J))
        τ_adjust_FB = τ_FB @ X_τ
        r_tilde_FB = r_adjust + ω_adjust*τ_adjust_FB
        
        τ_adjust_ten = τ_ten @ X_τ
        r_tilde_ten = r_adjust + ω_adjust*0.1*τ_adjust_ten
        
        r_tilde_zero = r_adjust
        
        xs = np.array([[1],[0]])
        Xs = np.ascontiguousarray(np.kron(np.eye(self.E.Θ+1), xs)[:-1,:-1])
        
        S_j_FB = pf.Shares_j(r_tilde_FB, A_FB, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_FB, Abar_ss_FB) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ_l, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_FB = ssf.Growth_SS(Abar_ss_FB, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_FB = (1+g_ss_FB)**(1-self.E.var_θ) / (1+ρ_l)
        ξ_hat_FB = ((self.E.γ-1) * (1-R_tilde_inv_FB) * ξtilde_FB / S_j_FB) @ Xs
        
        S_j_ten = pf.Shares_j(r_tilde_ten, A_ten, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_ten, Abar_ss_ten) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ_l, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_ten = ssf.Growth_SS(Abar_ss_ten, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_ten = (1+g_ss_ten)**(1-self.E.var_θ) / (1+ρ_l)
        ξ_hat_ten = ((self.E.γ-1) * (1-R_tilde_inv_ten) * ξtilde_ten / S_j_ten) @ Xs
        
        S_j_zero = pf.Shares_j(r_adjust, A_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        g_ss_zero = 0
        R_tilde_inv_zero = (1+g_ss_zero)**(1-self.E.var_θ) / (1+ρ_l)
        ξ_hat_zero = ((self.E.γ-1) * (1-R_tilde_inv_zero) * ξtilde_zero / S_j_zero) @ Xs
        
        
        # -------------- #
        # Record Results #
        # -------------- #
        κ = np.linalg.eig(self.E.φ_tilde_0.T)[0]
        unit = np.argmin(np.abs(κ-1))
        Cent = np.linalg.eig(self.E.φ_tilde_0.T)[1][:,unit]
        Cent = np.round(Cent / np.sum(Cent)*100, 2)
        IAM_Results.add('Eigenvector Centrality for Clean Transport', round(Cent[0], 2))
        IAM_Results.add('Eigenvector Centrality for Dirty Transport', round(Cent[1], 2))
        IAM_Results.add('Eigenvector Centrality for Clean Electricity', round(Cent[2], 2))
        IAM_Results.add('Eigenvector Centrality for Dirty Electricity', round(Cent[3], 2))
        
        
        ξ_hat_FB_avg = np.mean(ξ_hat_FB[:100,:],0)*100
        IAM_Results.add('Average 100 Year Clean Transport Subsidy (First-Best)', gpf.clean_round(ξ_hat_FB_avg[0], 1))
        IAM_Results.add('Average 100 Year Clean Electricity Subsidy (First-Best)', gpf.clean_round(ξ_hat_FB_avg[1], 1))
   
        
        A_ss_FB = np.append(Abar_ss_FB, 1)
        p_j = pf.PseudoP_j(self.E.r, A_ss_FB, self.E.α)
        p_θ = np.array([p_j[0], p_j[2], p_j[-1]])
        P = (np.sum(self.E.ν * p_θ**(1-self.E.λ)))**(1/(1-self.E.λ))
        S_θ = self.E.ν * (p_θ / P)**(1-self.E.λ) * 100
        IAM_Results.add('Steady-State Clean Transport Income Share (First-Best)', gpf.clean_round(S_θ[0], 1))
        IAM_Results.add('Steady-State Clean Electricity Income Share (First-Best)', gpf.clean_round(S_θ[1], 1))
    
        
        # ----------------- #
        # Plot Policy Paths #
        # ----------------- #
        DF_policy = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+T_time+1).reshape((-1,1)), τ_FB_dollar, ξ_hat_FB, ξ_hat_ten, ξ_hat_zero)), 
                             columns=['Year', 'τ_FB_dollar', 'ξ_hat_FB_Transport', 'ξ_hat_FB_Electricity', 'ξ_hat_ten_Transport', 'ξ_hat_ten_Electricity', 'ξ_hat_zero_Transport', 'ξ_hat_zero_Electricity'])
        DF_policy.to_csv(f'{self.Directory}/Results/Figures/IAMPolicy.csv', index=False)
        
        
        # --------------------------- #
        # Pollution & Growth Outcomes #
        # --------------------------- #
        Ω_FB = pf.Damage(C_FB, self.E.C_bar, self.E.var_ρ)
        Em_FB = pf.GHG(r_tilde_FB, A_FB, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_FB, self.E.L, ω_adjust, self.E.Θ)[1:,:]
        Ygross_FB = pf.Output(r_tilde_FB, A_FB, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_FB, self.E.L, self.E.Θ) / Ω_FB
        g_FB = np.log(Ygross_FB)[1:,:] - np.log(Ygross_FB)[:-1,:]
        
        Ω_ten = pf.Damage(C_ten, self.E.C_bar, self.E.var_ρ)
        Em_ten = pf.GHG(r_tilde_ten, A_ten, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_ten, self.E.L, ω_adjust, self.E.Θ)[1:,:]
        Ygross_ten = pf.Output(r_tilde_ten, A_ten, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_ten, self.E.L, self.E.Θ) / Ω_ten
        g_ten = np.log(Ygross_ten)[1:,:] - np.log(Ygross_ten)[:-1,:]
        
        Ω_zero = pf.Damage(C_zero, self.E.C_bar, self.E.var_ρ)
        Em_zero = pf.GHG(r_tilde_zero, A_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_zero, self.E.L, ω_adjust, self.E.Θ)[1:,:]
        Ygross_zero = pf.Output(r_tilde_zero, A_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_zero, self.E.L, self.E.Θ) / Ω_zero
        g_zero = np.log(Ygross_zero)[1:,:] - np.log(Ygross_zero)[:-1,:]
        
        IAM_Results.add('2200 Emissions (First-Best)', gpf.clean_round(Em_FB[2200 - (self.E.Year_0+2),0], 2))
        IAM_Results.add('2200 Gross Output Growth (First-Best)', gpf.clean_round(g_FB[2200 - (self.E.Year_0+2),0]*100, 2))
        IAM_Results.add('2200 Emissions (Ten)', gpf.clean_round(Em_ten[2200 - (self.E.Year_0+2),0], 2))
        IAM_Results.add('2200 Gross Output Growth (Ten)', gpf.clean_round(g_ten[2200 - (self.E.Year_0+2),0]*100, 2))
        IAM_Results.add('2200 Emissions (Zero)', gpf.clean_round(Em_zero[2200 - (self.E.Year_0+2),0], 2))
        IAM_Results.add('2200 Gross Output Growth (Zero)', gpf.clean_round(g_zero[2200 - (self.E.Year_0+2),0]*100, 2))
   
        
        # -------------------- #
        # Emissions Elasticity #
        # -------------------- #
        ΔlnEm_zero = pf.δGHG_δA(r_tilde_zero, A_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, ω_adjust, self.E.Θ) / (pf.omega_bar(r_tilde_zero, A_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, Ω_zero, self.E.L, ω_adjust, self.E.Θ) @ np.ones((1, J)) )
        ΔlnEm_zero_avg = np.mean(ΔlnEm_zero[:100,:],0)
        IAM_Results.add('Average 100 Year Clean Transport Emissions Elasticity (Zero)', gpf.clean_round(ΔlnEm_zero_avg[0], 2))
        IAM_Results.add('Average 100 Year Clean Electricity Emissions Elasticity (Zero)', gpf.clean_round(ΔlnEm_zero_avg[2], 2))
    
        
        # ----------------------------------------------------------------

        # Alternative policy paths.

        # ----------------------------------------------------------------
        
        # ----------------- #
        # Load Policy Paths #
        # ----------------- #
        (τ_spilllow, C_spilllow, ξtilde_spilllow, A_spilllow) = self.E.IAM(Periods, T_time, 1, 0, 1, 0)
        
        (τ_dischigh_FB, C_dischigh_FB, ξtilde_dischigh_FB, A_dischigh_FB) = self.E.IAM(Periods, T_time, 1, 1, 0, 0)
        (τ_dischigh_ten, C_dischigh_ten, ξtilde_dischigh_ten, A_dischigh_ten) = self.E.IAM(Periods, T_time, 0.1, 1, 0, 0)
        (τ_dischigh_zero, C_dischigh_zero, ξtilde_dischigh_zero, A_dischigh_zero) = self.E.IAM(Periods, T_time, 0, 1, 0, 0)
        
        (τ_damhigh, C_damhigh, ξtilde_damhigh, A_damhigh) = self.E.IAM(Periods, T_time, 1, 0, 0, 1)
        
        τ_spilllow_dollar = τ_spilllow * (Y_start / self.E.Y0) * (self.CO2_C)
        
        τ_adjust_spilllow = τ_spilllow @ X_τ
        r_tilde_spilllow = r_adjust + ω_adjust*τ_adjust_spilllow
        
        
        τ_dischigh_FB_dollar = τ_dischigh_FB * (Y_start / self.E.Y0) * (self.CO2_C)
        
        τ_adjust_dischigh_FB = τ_dischigh_FB @ X_τ
        r_tilde_dischigh_FB = r_adjust + ω_adjust*τ_adjust_dischigh_FB
        
        τ_adjust_dischigh_ten = τ_dischigh_ten @ X_τ
        r_tilde_dischigh_ten = r_adjust + ω_adjust*0.1*τ_adjust_dischigh_ten
        
        
        τ_damhigh_dollar = τ_damhigh * (Y_start / self.E.Y0) * (self.CO2_C)
        
        τ_adjust_damhigh = τ_damhigh @ X_τ
        r_tilde_damhigh = r_adjust + ω_adjust*τ_adjust_damhigh
        
        
        S_j_spilllow = pf.Shares_j(r_tilde_spilllow, A_spilllow, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        g_ss_spilllow = np.log(self.E.γ) * self.E.χ
        R_tilde_inv_spilllow = (1+g_ss_spilllow)**(1-self.E.var_θ) / (1+ρ_l)
        ξ_hat_spilllow = ((self.E.γ-1) * (1-R_tilde_inv_spilllow) * ξtilde_spilllow / S_j_spilllow) @ Xs
        IAM_Results.add('Initial Innovation Subsidy for Clean Transport (No Spillovers)', gpf.clean_round(ξ_hat_spilllow[0,0]*100, 1))
        IAM_Results.add('Initial Innovation Subsidy for Clean Electricity (No Spillovers)', gpf.clean_round(ξ_hat_spilllow[0,1]*100, 1))
    
        
        S_j_dischigh_FB = pf.Shares_j(r_tilde_dischigh_FB, A_dischigh_FB, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_dischigh_FB, Abar_ss_dischigh_FB) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ_h, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_dischigh_FB = ssf.Growth_SS(Abar_ss_dischigh_FB, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_dischigh_FB = (1+g_ss_dischigh_FB)**(1-self.E.var_θ) / (1+ρ_h)
        ξ_hat_dischigh_FB = ((self.E.γ-1) * (1-R_tilde_inv_dischigh_FB) * ξtilde_dischigh_FB / S_j_dischigh_FB) @ Xs
        
        S_j_dischigh_ten = pf.Shares_j(r_tilde_dischigh_ten, A_dischigh_ten, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_dischigh_ten, Abar_ss_dischigh_ten) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ_h, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_dischigh_ten = ssf.Growth_SS(Abar_ss_dischigh_ten, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_dischigh_ten = (1+g_ss_dischigh_ten)**(1-self.E.var_θ) / (1+ρ_h)
        ξ_hat_dischigh_ten = ((self.E.γ-1) * (1-R_tilde_inv_dischigh_ten) * ξtilde_dischigh_ten / S_j_dischigh_ten) @ Xs
        
        S_j_dischigh_zero = pf.Shares_j(r_adjust, A_dischigh_zero, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        R_tilde_inv_dischigh_zero = (1+g_ss_zero)**(1-self.E.var_θ) / (1+ρ_h)
        ξ_hat_dischigh_zero = ((self.E.γ-1) * (1-R_tilde_inv_dischigh_zero) * ξtilde_dischigh_zero / S_j_dischigh_zero) @ Xs

        
        S_j_damhigh = pf.Shares_j(r_tilde_damhigh, A_damhigh, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_damhigh, Abar_ss_damhigh) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ_l, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_damhigh = ssf.Growth_SS(Abar_ss_damhigh, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_damhigh = (1+g_ss_damhigh)**(1-self.E.var_θ) / (1+ρ_l)
        ξ_hat_damhigh = ((self.E.γ-1) * (1-R_tilde_inv_damhigh) * ξtilde_damhigh / S_j_damhigh) @ Xs
        
        
        # ----------------- #
        # Plot Policy Paths #
        # ----------------- #
        DF_policy_spilllow = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+T_time+1).reshape((-1,1)), τ_spilllow_dollar, ξ_hat_spilllow)), 
                             columns=['Year', 'τ_spilllow_dollar', 'ξ_hat_spilllow_Transport', 'ξ_hat_spilllow_Electricity'])
        DF_policy_spilllow.to_csv(f'{self.Directory}/Results/Figures/IAMPolicy_spilllow.csv', index=False)
        
        DF_policy_dischigh = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+T_time+1).reshape((-1,1)), τ_dischigh_FB_dollar, ξ_hat_dischigh_FB, ξ_hat_dischigh_ten, ξ_hat_dischigh_zero)), 
                             columns=['Year', 'τ_dischigh_FB_dollar', 'ξ_hat_dischigh_FB_Transport', 'ξ_hat_dischigh_FB_Electricity', 'ξ_hat_dischigh_ten_Transport', 'ξ_hat_dischigh_ten_Electricity', 'ξ_hat_dischigh_zero_Transport', 'ξ_hat_dischigh_zero_Electricity'])
        DF_policy_dischigh.to_csv(f'{self.Directory}/Results/Figures/IAMPolicy_dischigh.csv', index=False)
        
        DF_policy_damhigh = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+T_time+1).reshape((-1,1)), τ_damhigh_dollar, ξ_hat_damhigh)), 
                             columns=['Year', 'τ_damhigh_dollar', 'ξ_hat_damhigh_Transport', 'ξ_hat_damhigh_Electricity'])
        DF_policy_damhigh.to_csv(f'{self.Directory}/Results/Figures/IAMPolicy_damhigh.csv', index=False)
        
        
        # ----------------------------------------------------------------

        # Plot long-run temperature.

        # ----------------------------------------------------------------
        
        # ----------------- #
        # Load Policy Paths #
        # ----------------- #
        (τ_FB_long, C_FB_long, ξtilde_FB_long, A_FB_long) = self.E.IAM(Periods, Periods, 1, 0, 0, 0)
        (τ_ten_long, C_ten_long, ξtilde_ten_long, A_ten_long) = self.E.IAM(Periods, Periods, 0.1, 0, 0, 0)
        (τ_zero_long, C_zero_long, ξtilde_zero_long, A_zero_long) = self.E.IAM(Periods, Periods, 0, 0, 0, 0)
        
        # ----------------- #
        # Temperature Paths #
        # ----------------- #
        Temp_FB = pf.Temp(C_FB_long, self.E.C_bar)
        Temp_ten = pf.Temp(C_ten_long, self.E.C_bar)
        Temp_zero = pf.Temp(C_zero_long, self.E.C_bar)
        
        DF_temppath = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+Periods+1).reshape((-1,1)), Temp_FB, Temp_ten, Temp_zero)), 
                             columns=['Year', 'Temp_FB', 'Temp_ten', 'Temp_zero'])
        DF_temppath.to_csv(f'{self.Directory}/Results/Figures/TempPathIAM.csv', index=False)
         
        # ----------------------------------------------------------------

        # Consumption equivalence.

        # ----------------------------------------------------------------
        
        # --------------------- #
        # Low Discounting Paths #
        # --------------------- #
        r_adjust_long = np.tile(self.E.r.reshape((1,J)), (Periods, 1))
        ν_adjust_long = np.tile(self.E.ν.reshape((1,self.E.Θ+1)), (Periods, 1))
        ω_adjust_long = np.tile(self.E.ω.reshape((1,J)), (Periods, 1))
        
        τ_adjust_FB_long = τ_FB_long @ X_τ
        r_tilde_FB_long = r_adjust_long + ω_adjust_long*τ_adjust_FB_long
        
        τ_adjust_ten_long = τ_ten_long @ X_τ
        r_tilde_ten_long = r_adjust_long + ω_adjust_long*0.1*τ_adjust_ten_long
        
        Ω_FB_long = pf.Damage(C_FB_long, self.E.C_bar, self.E.var_ρ)
        c_FB_long = pf.Consump(r_adjust_long, r_tilde_FB_long, A_FB_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_FB_long, self.E.L, self.E.Θ)
        
        Ω_ten_long = pf.Damage(C_ten_long, self.E.C_bar, self.E.var_ρ)
        c_ten_long = pf.Consump(r_adjust_long, r_tilde_ten_long, A_ten_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_ten_long, self.E.L, self.E.Θ)
        W_ten = of.Welfare(c_ten_long, self.E.var_θ, Periods, ρ_l, g_ss_ten)
    
        CE_ten = 100 - of.Consump_Eq(W_ten, c_FB_long, self.E.var_θ, Periods, ρ_l, g_ss_FB) * 100
        IAM_Results.add('Second-Best Consumption Equivalent Loss (Ten)', gpf.clean_round(CE_ten[0], 2))
        
        Ω_zero_long = pf.Damage(C_zero_long, self.E.C_bar, self.E.var_ρ)
        c_zero_long = pf.Consump(r_adjust_long, r_adjust_long, A_zero_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_zero_long, self.E.L, self.E.Θ)
        W_zero = of.Welfare(c_zero_long, self.E.var_θ, Periods, ρ_l, g_ss_zero)
        
        CE_zero = 100 - of.Consump_Eq(W_zero, c_FB_long, self.E.var_θ, Periods, ρ_l, g_ss_FB) * 100
        IAM_Results.add('Second-Best Consumption Equivalent Loss (Zero)', gpf.clean_round(CE_zero[0], 2))
        
        
        # ---------------------- #
        # High Discounting Paths #
        # ---------------------- #
        (τ_dischigh_FB_long, C_dischigh_FB_long, ξtilde_dischigh_FB_long, A_dischigh_FB_long) = self.E.IAM(Periods, Periods, 1, 1, 0, 0)
        (τ_dischigh_ten_long, C_dischigh_ten_long, ξtilde_dischigh_ten_long, A_dischigh_ten_long) = self.E.IAM(Periods, Periods, 0.1, 1, 0, 0)
        (τ_dischigh_zero_long, C_dischigh_zero_long, ξtilde_dischigh_zero_long, A_dischigh_zero_long) = self.E.IAM(Periods, Periods, 0, 1, 0, 0)
        
        τ_adjust_dischigh_FB_long = τ_dischigh_FB_long @ X_τ
        r_tilde_dischigh_FB_long = r_adjust_long + ω_adjust_long*τ_adjust_dischigh_FB_long
        
        τ_adjust_dischigh_ten_long = τ_dischigh_ten_long @ X_τ
        r_tilde_dischigh_ten_long = r_adjust_long + ω_adjust_long*0.1*τ_adjust_dischigh_ten_long
        
        Ω_dischigh_FB_long = pf.Damage(C_dischigh_FB_long, self.E.C_bar, self.E.var_ρ)
        c_dischigh_FB_long = pf.Consump(r_adjust_long, r_tilde_dischigh_FB_long, A_dischigh_FB_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_dischigh_FB_long, self.E.L, self.E.Θ)
        
        Ω_dischigh_ten_long = pf.Damage(C_dischigh_ten_long, self.E.C_bar, self.E.var_ρ)
        c_dischigh_ten_long = pf.Consump(r_adjust_long, r_tilde_dischigh_ten_long, A_dischigh_ten_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_dischigh_ten_long, self.E.L, self.E.Θ)
        W_dischigh_ten = of.Welfare(c_dischigh_ten_long, self.E.var_θ, Periods, ρ_h, g_ss_dischigh_ten)
        
        CE_dischigh_ten = 100 - of.Consump_Eq(W_dischigh_ten, c_dischigh_FB_long, self.E.var_θ, Periods, ρ_h, g_ss_dischigh_FB) * 100
        IAM_Results.add('Second-Best Consumption Equivalent Loss (Ten, High Disc)', gpf.clean_round(CE_dischigh_ten[0], 2))
        
        Ω_dischigh_zero_long = pf.Damage(C_dischigh_zero_long, self.E.C_bar, self.E.var_ρ)
        c_dischigh_zero_long = pf.Consump(r_adjust_long, r_adjust_long, A_dischigh_zero_long, self.E.α, self.E.σ, self.E.λ, ν_adjust_long, Ω_dischigh_zero_long, self.E.L, self.E.Θ)
        W_dischigh_zero = of.Welfare(c_dischigh_zero_long, self.E.var_θ, Periods, ρ_h, g_ss_zero)
        
        CE_dischigh_zero = 100 - of.Consump_Eq(W_dischigh_zero, c_dischigh_FB_long, self.E.var_θ, Periods, ρ_h, g_ss_dischigh_FB) * 100
        IAM_Results.add('Second-Best Consumption Equivalent Loss (Zero, High Disc)', gpf.clean_round(CE_dischigh_zero[0], 2))
        
        IAM_Results.to_csv(f'{self.Directory}/Results/Tables/IAM_Results.csv')
        
        
        # ----------------------------------------------------------------

        # Clean technology growth rates (for X-risk paper).

        # ----------------------------------------------------------------
        
        # ---------------------------------- #
        # Save Clean Technology Growth Rates #
        # ---------------------------------- #
        A_lag = np.vstack((self.E.A_0.reshape((1,J)), A_dischigh_FB_long[:-1,:]))
        gc = np.log(A_dischigh_FB_long) - np.log(A_lag)
        df_gc = pd.DataFrame(gc[:,[0,2]])
        df_gc.columns = ['Clean Car Growth', 'Clean Electricity Growth']
        df_gc.to_pickle(f'{self.Directory}/Results/Tables/Clean_Growth.pkl')
        
        

    def CES_Spill(self, Periods, T_time, o):
        "Processing of CES Spillover Robustness"
        
        J = 2*self.E.Θ + 1
        CES_Results = gpf.ResultsTable()       
        
        ρ = (1+self.E.ρ_l)**self.E.T - 1
        
        cal_panel = pd.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        
        r_adjust = np.tile(self.E.r.reshape((1,J)), (T_time, 1))
        ν_adjust = np.tile(self.E.ν.reshape((1,self.E.Θ+1)), (T_time, 1))
        ω_adjust = np.tile(self.E.ω.reshape((1,J)), (T_time, 1))
        
        X_τ = np.ones((1,J))
        xs = np.array([[1],[0]])
        Xs = np.ascontiguousarray(np.kron(np.eye(self.E.Θ+1), xs)[:-1,:-1])
        
        
        # ---------------- #
        # Load Policy Path #
        # ---------------- #
        (τ_CES, C_CES, ξtilde_CES, A_CES) = self.E.CES_IAM(Periods, T_time, o)        


        # -------------------------- #
        # Make Policy Comprehensible #
        # -------------------------- #
        τ_adjust_CES = τ_CES @ X_τ
        r_tilde_CES = r_adjust + ω_adjust*τ_adjust_CES
        
        S_j_CES = pf.Shares_j(r_tilde_CES, A_CES, self.E.α, self.E.σ, self.E.λ, ν_adjust, self.E.Θ)
        (ξtilde_ss_CES, Abar_ss_CES) = ssf.Opt_SS(self.E.r, self.E.α, self.E.λ, self.E.γ, self.E.χ, self.E.ν, self.E.η, self.E.φ_hat, ρ, self.E.var_θ, self.E.Θ, self.E.o)
        g_ss_CES = ssf.Growth_SS(Abar_ss_CES, self.E.φ_hat, self.E.η, self.E.ν, self.E.γ, self.E.χ, self.E.Θ, self.E.o)
        R_tilde_inv_CES = (1+g_ss_CES)**(1-self.E.var_θ) / (1+ρ)
        ξ_hat_CES = ((self.E.γ-1) * (1-R_tilde_inv_CES) * ξtilde_CES / S_j_CES) @ Xs
        
        
        # -------------- #
        # Record Results #
        # -------------- #
        φ_tilde_ss_CES = rf.SpillNet(self.E.φ_hat, np.append(Abar_ss_CES,1), self.E.o)[0,:,:] + np.eye(J)
        κ_CES = np.linalg.eig(φ_tilde_ss_CES.T)[0]
        unit_CES = np.argmin(np.abs(κ_CES-1))
        Cent_CES = np.linalg.eig(φ_tilde_ss_CES.T)[1][:,unit_CES]
        Cent_CES = np.round(Cent_CES / np.sum(Cent_CES)*100, 2)
        CES_Results.add('Eigenvector Centrality for Clean Transport (CES)', round(Cent_CES[0], 2))
        CES_Results.add('Eigenvector Centrality for Clean Electricity (CES)', round(Cent_CES[2], 2))
    
        
        A_ss_CES = np.append(Abar_ss_CES, 1)
        p_j = pf.PseudoP_j(self.E.r, A_ss_CES, self.E.α)
        p_θ = np.array([p_j[0], p_j[2], p_j[-1]])
        P = (np.sum(self.E.ν * p_θ**(1-self.E.λ)))**(1/(1-self.E.λ))
        S_θ = self.E.ν * (p_θ / P)**(1-self.E.λ) * 100
        CES_Results.add('Steady-State Clean Transport Income Share (CES)', gpf.clean_round(S_θ[0], 2))
        CES_Results.add('Steady-State Clean Electricity Income Share (CES)', gpf.clean_round(S_θ[1], 2))
        
        CES_Results.to_csv(f'{self.Directory}/Results/Tables/CES_Results.csv')
        
        
        # ---------------- #
        # Plot Policy Path #
        # ---------------- #
        DF_policy_CES = pd.DataFrame(np.hstack((np.arange(self.E.Year_0+1, self.E.Year_0+T_time+1).reshape((-1,1)), ξ_hat_CES)), 
                             columns=['Year', 'ξ_hat_CES_Transport', 'ξ_hat_CES_Electricity'])
        DF_policy_CES.to_csv(f'{self.Directory}/Results/Figures/IAMPolicy_CES.csv', index=False)
