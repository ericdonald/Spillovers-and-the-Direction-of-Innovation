/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Spillover Stability

Last Modified: Eric Donald 8/24

Notes: Regressions to estimate citation share stability.
    
Output: Empirical/Clean Data/spillover_stability.dta

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Generate citations shares by technology class in five year intervals.

*******************************************************************

use "Empirical/Raw Data/uspatentcitation.dta", clear

merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate

foreach c in $class {
		foreach i in $type {
			
			rename `c'_`i'_patent citer_`c'_`i'_patent

	}
}

rename gen_patent citer_gen_patent
rename patent_id id_citer_patent

gen t_int = 0
forvalues y = 1975(5)2015 {
	replace t_int = `y' if year > `y'-5 & year <= `y'
}
drop if t_int == 0

keep t_int citer* id_citer_patent citation_id sequence

rename citation_id patent_id
merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate

foreach c in $class {
		foreach i in $type {
			
			rename `c'_`i'_patent citee_`c'_`i'_patent

	}
}

rename gen_patent citee_gen_patent
rename patent_id id_citee_patent

keep t_int citer* citee* id_citer_patent id_citee_patent sequence

gen type_string = ""
replace type_string = type_string + "a" if citer_car_clean_patent == 1
replace type_string = type_string + "b" if citer_car_dirty_patent == 1
replace type_string = type_string + "c" if citer_elec_clean_patent == 1
replace type_string = type_string + "d" if citer_elec_dirty_patent == 1
replace type_string = type_string + "e" if citer_gen_patent == 1

egen citer_classes = rowtotal(citer*)

expand citer_classes

bysort id_citer_patent id_citee_patent sequence: gen citer_class = substr(type_string, _n, 1)

gen tech_citer = ""
replace tech_citer = "car_clean" if citer_class == "a"
replace tech_citer = "car_dirty" if citer_class == "b"
replace tech_citer = "elec_clean" if citer_class == "c"
replace tech_citer = "elec_dirty" if citer_class == "d"
replace tech_citer = "gen" if citer_class == "e"

drop type_string citer*


gen type_string = ""
replace type_string = type_string + "a" if citee_car_clean_patent == 1
replace type_string = type_string + "b" if citee_car_dirty_patent == 1
replace type_string = type_string + "c" if citee_elec_clean_patent == 1
replace type_string = type_string + "d" if citee_elec_dirty_patent == 1
replace type_string = type_string + "e" if citee_gen_patent == 1

egen citee_classes = rowtotal(citee*)

expand citee_classes

bysort id_citer_patent id_citee_patent sequence tech_citer: gen citee_class = substr(type_string, _n, 1)

gen tech_citee = ""
replace tech_citee = "car_clean" if citee_class == "a"
replace tech_citee = "car_dirty" if citee_class == "b"
replace tech_citee = "elec_clean" if citee_class == "c"
replace tech_citee = "elec_dirty" if citee_class == "d"
replace tech_citee = "gen" if citee_class == "e"

drop type_string citee*


bysort t_int tech_citer: gen tot_cites = _N
bysort t_int tech_citer tech_citee: gen cites = _N
gen φ_tilde = cites / tot_cites

keep t_int tech_citer tech_citee φ_tilde
duplicates drop

fillin t_int tech_citer tech_citee
drop _fillin
replace φ_tilde = 0 if φ_tilde==.

save "Empirical/Clean Data/spillover_stability.dta", replace

gen tech_pair = tech_citer + tech_citee
egen tech_index = group(tech_pair)

xtset tech_index t_int, delta(5)

reg φ_tilde l1.φ_tilde, noconstant vce(cluster tech_citer)

gen clean_sender = 0
replace clean_sender = 1 if tech_citee == "car_clean"
replace clean_sender = 1 if tech_citee == "elec_clean"

gen clean_trend = clean_sender * (t_int-1975)
reg φ_tilde l1.φ_tilde clean_trend, noconstant vce(cluster tech_citer)

gen car_clean_sender = 0
replace car_clean_sender = 1 if tech_citee == "car_clean"

gen elec_clean_sender = 0
replace elec_clean_sender = 1 if tech_citee == "elec_clean"

gen car_clean_trend = car_clean_sender * (t_int-1975)
gen elec_clean_trend = elec_clean_sender * (t_int-1975)

reg φ_tilde l1.φ_tilde car_clean_trend elec_clean_sender, noconstant vce(cluster tech_citer)







