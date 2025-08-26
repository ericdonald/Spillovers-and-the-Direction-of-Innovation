/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Cleaner

Last Modified: Eric Donald 4/24

Notes: This file unzips data and conducts minor cleaning. 
    
Output: Empirical/Raw Data/cpc_current.dta
		Empirical/Raw Data/application.dta
		Empirical/Raw Data/uspatentcitation.dta
		Empirical/Raw Data/EIA_Electricity_Revenue.dta
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












