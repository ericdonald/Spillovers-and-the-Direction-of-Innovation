/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Cleaner

Last Modified: Eric Donald 4/24

Notes: This file unzips data and conducts minor cleaning. 
    
Output: Empirical/Raw Data/cpc_current.dta
		Empirical/Raw Data/application.dta
		Empirical/Raw Data/uspatentcitation.dta
		Empirical/Raw Data/EIA_Electricity_Revenue.dta
		Empirical/Raw Data/FRED_CPI.dta
		Empirical/Raw Data/EIA_Electricity_Share.dta
		Empirical/Raw Data/FRED_Vehicle_Revenue.dta
		Empirical/Raw Data/TEDB_Car_Clean_qShare.dta
		Empirical/Raw Data/FRED_Total_GDP.dta
		Empirical/Raw Data/EPA_C_Em.dta
		Empirical/Raw Data/OWID_CO2_Em.dta
		Empirical/Raw Data/OWID_CO2_Em_LU.dta
		Empirical/Raw Data/NOAA_CO2_PPM.dta
		Empirical/Raw Data/IED_RD_Sub.dta
		Empirical/Raw Data/FRED_RD.dta
		Empirical/Clean Data/RICE.dta

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Unzip and clean files.

*******************************************************************

cd "${project}/Empirical/Raw Data"
unzipfile "PatentsView.zip", replace
cd "${project}"


*****************************************
***PatentsView CPC Classification Data***
*****************************************
import delimited "Empirical/Raw Data/PatentsView/cpc_current.tsv", varnames(1) clear

tostring patent_id, replace

save "Empirical/Raw Data/cpc_current.dta", replace

erase "Empirical/Raw Data/PatentsView/cpc_current.tsv"



**********************************
***PatentsView Application Data***
**********************************
import delimited "Empirical/Raw Data/PatentsView/application.tsv", varnames(1) clear

gen app_year = year(date(date, "YMD"))

save "Empirical/Raw Data/application.dta", replace

erase "Empirical/Raw Data/PatentsView/application.tsv"



*******************************
***PatentsView Citation Data***
*******************************
import delimited "Empirical/Raw Data/PatentsView/uspatentcitation.tsv", varnames(1) clear

save "Empirical/Raw Data/uspatentcitation.dta", replace

erase "Empirical/Raw Data/PatentsView/uspatentcitation.tsv"


**Remove PatentsView folder
*rmdir "Empirical/Raw Data/PatentsView"
*rmdir "Empirical/Raw Data/__MACOSX/PatentsView"
*rmdir "Empirical/Raw Data/__MACOSX"



*************************************
***EIA US Electricity Revenue Data***
*************************************
import delimited "Empirical/Raw Data/EIA_Electricity_Revenue.csv", clear

rename period year

rename revenue elec_revenue
label variable elec_revenue "Nominal US electricity revenue in millions of dollars"

keep year elec_revenue

save "Empirical/Raw Data/EIA_Electricity_Revenue.dta", replace



*******************
***FRED CPI Data***
*******************
import excel "Empirical/Raw Data/FRED_CPI.xls", sheet("FRED Graph") cellrange(A11:B74) firstrow clear

gen year = year(observation_date)
drop observation_date

rename CPALTT01USA661S_NBD20120101 CPI
label variable CPI "CPI 2012=100"

save "Empirical/Raw Data/FRED_CPI.dta", replace



********************************************
***EIA US Electricity Quantity Share Data***
********************************************
import delimited "Empirical/Raw Data/EIA_Electricity_Share.csv", clear

rename period year

bysort year: egen Q_elec_dirty = min(generation)
bysort year: egen Q_elec = max(generation)


gen q_elec_clean = 1 - Q_elec_dirty / Q_elec

keep year q_elec_clean
label variable q_elec_clean "US clean electricity quantity share"


duplicates drop

save "Empirical/Raw Data/EIA_Electricity_Share.dta", replace



**********************************
***FRED US Vehicle Revenue Data***
**********************************
import delimited "Empirical/Raw Data/FRED_Vehicle_Revenue.csv", clear

gen year = year(date(date, "YMD"))
drop date

rename a953rc1q027sbea car_revenue
label variable car_revenue "Nominal US vehicle revenue in billions of dollars"

save "Empirical/Raw Data/FRED_Vehicle_Revenue.dta", replace




*************************************
***TEDB US Car Quantity Share Data***
*************************************
import excel "Empirical/Raw Data/TEDB_Car_Clean_qShare.xlsx", sheet("TEDB Edition 40") cellrange(B8:I31) firstrow clear

rename Calendaryear year

rename Alllightvehiclesalesthousan Q_car
label variable Q_car "Light vehicle quantity in thousands"

gen Q_car_clean = Hybridvehiclesalesthousands + Pluginhybridvehiclesalesth + Allelectricvehiclesalesthou
label variable Q_car_clean "US clean vehicle quantity in thousands"

gen q_car_clean = Hybridshareofalllightvehicl + Pluginhybridshareofalllig + Allelectricshareofalllight
label variable q_car_clean "US clean vehicle quantity share"

keep year Q_car Q_car_clean q_car_clean


save "Empirical/Raw Data/TEDB_Car_Clean_qShare.dta", replace



**********************
***FRED US GDP Data***
**********************
import excel "Empirical/Raw Data/FRED_Total_GDP.xls", sheet("FRED Graph") cellrange(A11:B87) firstrow clear

gen year = year(observation_date)
drop observation_date

rename GDPC1 GDP
label variable GDP "US GDP in billions of 2012 dollars"

save "Empirical/Raw Data/FRED_Total_GDP.dta", replace



*************************************
***EPA US Emissions Inventory Data***
*************************************
import delimited "Empirical/Raw Data/EPA_CO2e.csv", clear

*Data starts in MMT of CO2e

rename transportation car_C_em
replace car_C_em = car_C_em / 1000
replace car_C_em = car_C_em * $CO2_C
label variable car_C_em "US transport carbon emissions in gigatons"

rename electricpowerindustry elec_C_em
replace elec_C_em = elec_C_em / 1000
replace elec_C_em = elec_C_em * $CO2_C
label variable elec_C_em "US electricity carbon emissions in gigatons"

rename grosstotal total_C_em
replace total_C_em = total_C_em / 1000
replace total_C_em = total_C_em * $CO2_C
label variable total_C_em "US total carbon emissions in gigatons"

keep year car_C_em elec_C_em total_C_em

save "Empirical/Raw Data/EPA_C_Em.dta", replace



*************************
***OWID Emissions Data***
*************************
import delimited "Empirical/Raw Data/OWID_CO2_Em.csv", clear

keep if entity == "World"
drop entity code
drop if year < $ind_year

rename annualcoemissions C_em_fossil

save "Empirical/Raw Data/OWID_CO2_Em.dta", replace

import delimited "Empirical/Raw Data/OWID_CO2_Em_LU.csv", clear

keep if entity == "World"
drop entity code annualcoemissions annualcoemissionsincludinglandu

rename annualcoemissionsfromlandusecha C_em_LU_1850

save "Empirical/Raw Data/OWID_CO2_Em_LU.dta", replace



*************************************
***NOAA Carbon Concentrations Data***
*************************************
import delimited "Empirical/Raw Data/NOAA_CO2_PPM.csv", clear

rename mean C_stock

save "Empirical/Raw Data/NOAA_CO2_PPM.dta", replace



***********************
***IED R&D Subsidies***
***********************
import delimited "Empirical/Raw Data/IED_RD_Sub.csv", clear

drop if flagcodes == "L"
rename time year

keep flow v6 year value

foreach c in $class {
	foreach i in $type {

		gen `c'_`i' = 0

		*Classify research classes
		foreach class in ${`c'_`i'_IED_classes} {
		replace `c'_`i' = 1 if flow == "`class'"
		}

	}
}

replace elec_clean = -1 if flow == "34BIOFUE"
replace elec_dirty = 1/2 if flow == "21OILGAS"
replace car_dirty = 1/2 if flow == "21OILGAS"

foreach c in $class {
	foreach i in $type {

		gen `c'_`i'_class_spend = value * `c'_`i'
		bysort year: egen `c'_`i'_RD_sub = total(`c'_`i'_class_spend)

	}
}

keep year *_RD_sub
duplicates drop

save "Empirical/Raw Data/IED_RD_Sub.dta", replace



**********************
***FRED US R&D Data***
**********************
import excel "Empirical/Raw Data/FRED_RD.xls", sheet("FRED Graph") cellrange(A11:B87) firstrow clear

gen year = year(observation_date)
drop observation_date

rename Y694RX1Q020SBEA RD
label variable RD "US R&D in billions of 2012 dollars"


save "Empirical/Raw Data/FRED_RD.dta", replace



****************************
***RICE Outside Emissions***
****************************
import excel "Empirical/Raw Data/RICE.xlsx", sheet("Results") firstrow clear

tsset year
local new = _N + 1
set obs `new'
replace year = 2010 in `new'
local new = _N + 1
set obs `new'
replace year = 3000 in `new'
sort year
tsfill

replace Optimal_Global_Em = 0 if year > 2595
replace Optimal_US_Em = 0 if year > 2595
replace Baseline_Global_Em = 0 if year > 2595
replace Baseline_US_Em = 0 if year > 2595

*Interpolate emissions by year
ipolate Optimal_Global_Em year, generate(Optimal_Global_Em_1) epolate
drop Optimal_Global_Em
rename Optimal_Global_Em_1 Optimal_Global_Em
label variable Optimal_Global_Em "Optimal global emissions in GtC"

ipolate Optimal_US_Em year, generate(Optimal_US_Em_1) epolate
drop Optimal_US_Em
rename Optimal_US_Em_1 Optimal_US_Em
label variable Optimal_US_Em "Optimal US emissions in GtC"

ipolate Baseline_Global_Em year, generate(Baseline_Global_Em_1) epolate
drop Baseline_Global_Em
rename Baseline_Global_Em_1 Baseline_Global_Em
label variable Baseline_Global_Em "Baseline global emissions in GtC"

ipolate Baseline_US_Em year, generate(Baseline_US_Em_1) epolate
drop Baseline_US_Em
rename Baseline_US_Em_1 Baseline_US_Em
label variable Baseline_US_Em "Baseline US emissions in GtC"


save "Empirical/Clean Data/RICE.dta", replace
