/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Calibration Panel

Last Modified: Eric Donald 2/25

Notes: Creates panel of calibration moments.
    
Output: Empirical/Clean Data/cal_panel.dta
		Empirical/Clean Data/clim_cal_panel.dta

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Generate revenue and quantity share series.

*******************************************************************


*****************
***Electricity***
*****************
use "Empirical/Raw Data/EIA_Electricity_Revenue.dta", clear

tset year, yearly

*Make electricity revenue real and convert from millions to billions
merge 1:1 year using "Empirical/Raw Data/FRED_CPI.dta", keep(master match) nogenerate

gen Y_elec = elec_revenue * 100 / CPI
replace Y_elec = Y_elec / 1000
label variable Y_elec "US electricity revenue in billions of 2012 dollars"
drop elec_revenue

*Load quantity shares
merge 1:1 year using "Empirical/Raw Data/EIA_Electricity_Share.dta", keep(master match) nogenerate



**********
***Cars***
**********
merge 1:1 year using "Empirical/Raw Data/FRED_Vehicle_Revenue.dta", keep(master match) nogenerate


*Make vehicle revenue real
gen Y_car = car_revenue * 100 / CPI
label variable Y_car "US vehicle revenue in billions of 2012 dollars"
drop car_revenue

*Derive quantity shares
merge 1:1 year using "Empirical/Raw Data/TEDB_Car_Clean_qShare.dta", keep(master match) nogenerate

replace q_car_clean = 0 if year<1999
replace Q_car_clean = 0 if year<1999



******************
***Final Output***
******************
merge 1:1 year using "Empirical/Raw Data/FRED_Total_GDP.dta", keep(master match) nogenerate

gen S_car = Y_car / GDP
label variable S_car "Car income share"

gen S_elec = Y_elec / GDP
label variable S_elec "Electricity income share"



*******************************
***Sectoral Carbon Emissions***
*******************************
merge 1:1 year using "Empirical/Raw Data/EPA_C_Em.dta", keep(master match) nogenerate

gen car_C_relem = car_C_em / total_C_em
label variable car_C_relem "Proportion of total US emissions in transport"

gen elec_C_relem = elec_C_em / total_C_em
label variable elec_C_relem "Proportion of total US emissions in electricity"



*******************************
***Status Quo Subsidies***
*******************************

*Manually enter EV tax credit expenditures from US Congressional Research Service Report IF11017.

replace car_clean_sub = car_clean_sub * 100 / CPI

gen car_clean_relsub = car_clean_sub / Y_car
label variable car_clean_relsub "Proportion of US vehicle revenue funded by EV tax credit"


*Manually enter energy investment tax credit expenditures from US Congressional Research Service Report IF10479.

replace elec_clean_sub = elec_clean_sub * 100 / CPI

gen elec_clean_relsub = elec_clean_sub / Y_elec
label variable elec_clean_relsub "Proportion of US electricity revenue funded by energy investment tax credit"


*Innovation Subsidies from IEA
merge 1:1 year using "Empirical/Raw Data/IED_RD_Sub.dta", keep(master match) nogenerate

*Make innovation subsidies real
foreach c in $class {
	foreach i in $type {

		replace `c'_`i'_RD_sub = `c'_`i'_RD_sub * 100 / CPI
		replace `c'_`i'_RD_sub = `c'_`i'_RD_sub / 1000
		label variable `c'_`i'_RD_sub "`c'_`i' innovation subsidies in billions of 2012 dollars"

	}
}

*Total R&D Spending
merge 1:1 year using "Empirical/Raw Data/FRED_RD.dta", keep(master match) nogenerate

*Create proportional innovation subsidies
foreach c in $class {
	foreach i in $type {

		gen `c'_`i'_RD_relsub = `c'_`i'_RD_sub / RD
		label variable `c'_`i'_RD_relsub "Proportion of R&D funded by `c'_`i' innovation subsidies"

	}
}

save "Empirical/Clean Data/cal_panel.dta", replace



