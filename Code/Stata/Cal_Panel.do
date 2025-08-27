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



