/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Relevant Patents

Last Modified: Eric Donald 3/25

Notes: Creates a dataset of patents with technology classifications and application dates.
    
Output: Empirical/Clean Data/relevant_patents.dta

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Identify relevant patents.

*******************************************************************

use "Empirical/Raw Data/cpc_current.dta", clear

gen subgroup_idfive = substr(subgroup_id, 1, 5)
gen subgroup_idsix = substr(subgroup_id, 1, 6)
gen gen_patent = 1

foreach c in $class {
	foreach i in $type {

		gen `c'_`i' = 0

		*Classify relevant patents
		foreach class in ${`c'_`i'_classes} {
		replace `c'_`i' = 1 if subsection_id=="`class'" | group_id=="`class'" | subgroup_idfive=="`class'" | subgroup_idsix=="`class'" | subgroup_id=="`class'"
		}

		*Label entire patent if any classifications fit
		bysort patent_id: egen `c'_`i'_patent = max(`c'_`i')

		drop `c'_`i'
		
		*Label patent not general if specific class
		replace gen_patent = 0 if `c'_`i'_patent == 1
	}
}



*Keep one observation per patent
duplicates drop patent_id, force


*******************************************************************

* Merge in application data.

*******************************************************************

merge 1:1 patent_id using "Empirical/Raw Data/application.dta", keep(match) nogenerate
rename app_year year

*Drop inappropriate years
drop if year < 1900 | year > 2025

*Only keep relevant variables
keep patent_id gen_patent car_clean_patent car_dirty_patent elec_clean_patent elec_dirty_patent year


save "Empirical/Clean Data/relevant_patents.dta", replace

