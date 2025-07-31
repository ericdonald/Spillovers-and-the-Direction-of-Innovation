/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Citation Shares

Last Modified: Eric Donald 8/24

Notes: Creates citation share matrix by technology class.
    
Output: Empirical/Clean Data/citation_shares.dta
		Empirical/Clean Data/citation_shares_applicant.dta

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Generate citations shares by technology class.

*******************************************************************

use "Empirical/Raw Data/uspatentcitation.dta", clear



foreach c in $class {
	foreach i in $type {
		preserve
		
		merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
		keep if `c'_`i'_patent==1

		keep citation_id
		
		rename citation_id patent_id
		merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
		gen cites = 0
		
		foreach k in $class {
			foreach j in $type {
				egen cites_`k'_`j' = total(`k'_`j'_patent)
				replace cites = cites + cites_`k'_`j'
			}
		}
		egen cites_gen = total(gen_patent)
		replace cites = cites + cites_gen
		
		keep cites*
		duplicates drop 
		
		foreach k in $class {
			foreach j in $type {
				gen φ_tilde_`k'`j' = cites_`k'_`j' / cites
			}
		}
		gen φ_tilde_gen = cites_gen / cites
		
		keep φ_tilde*
		gen tech = "`c'_`i'"
		
		
		tempfile spill_`c'_`i'
		save `spill_`c'_`i''
		
		restore
	}
}



merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
keep if gen_patent==1

keep citation_id

rename citation_id patent_id
merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate

gen cites = 0

foreach k in $class {
	foreach j in $type {
		egen cites_`k'_`j' = total(`k'_`j'_patent)
		replace cites = cites + cites_`k'_`j'
	}
}
egen cites_gen = total(gen_patent)
replace cites = cites + cites_gen

keep cites*
duplicates drop 

foreach k in $class {
	foreach j in $type {
		gen φ_tilde_`k'`j' = cites_`k'_`j' / cites
	}
}
gen φ_tilde_gen = cites_gen / cites

keep φ_tilde*
gen tech = "gen"





foreach c in $class {
	foreach i in $type {
		append using `spill_`c'_`i''
	}
}

egen tech_index = group(tech)
sort tech_index
drop tech_index tech


save "Empirical/Clean Data/citation_shares.dta", replace


*******************************************************************

* Generate citations shares by technology class (applicant only).

*******************************************************************

use "Empirical/Raw Data/uspatentcitation.dta", clear

keep if category=="cited by applicant"

foreach c in $class {
	foreach i in $type {
		preserve
		
		merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
		keep if `c'_`i'_patent==1

		keep citation_id
		
		rename citation_id patent_id
		merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
		gen cites = 0
		
		foreach k in $class {
			foreach j in $type {
				egen cites_`k'_`j' = total(`k'_`j'_patent)
				replace cites = cites + cites_`k'_`j'
			}
		}
		egen cites_gen = total(gen_patent)
		replace cites = cites + cites_gen
		
		keep cites*
		duplicates drop 
		
		foreach k in $class {
			foreach j in $type {
				gen φ_tilde_`k'`j' = cites_`k'_`j' / cites
			}
		}
		gen φ_tilde_gen = cites_gen / cites
		
		keep φ_tilde*
		gen tech = "`c'_`i'"
		
		
		tempfile spill_`c'_`i'
		save `spill_`c'_`i''
		
		restore
	}
}



merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate
		
keep if gen_patent==1

keep citation_id

rename citation_id patent_id
merge m:1 patent_id using "Empirical/Clean Data/relevant_patents.dta", keep(match) nogenerate

gen cites = 0

foreach k in $class {
	foreach j in $type {
		egen cites_`k'_`j' = total(`k'_`j'_patent)
		replace cites = cites + cites_`k'_`j'
	}
}
egen cites_gen = total(gen_patent)
replace cites = cites + cites_gen

keep cites*
duplicates drop 

foreach k in $class {
	foreach j in $type {
		gen φ_tilde_`k'`j' = cites_`k'_`j' / cites
	}
}
gen φ_tilde_gen = cites_gen / cites

keep φ_tilde*
gen tech = "gen"





foreach c in $class {
	foreach i in $type {
		append using `spill_`c'_`i''
	}
}

egen tech_index = group(tech)
sort tech_index
drop tech_index tech


save "Empirical/Clean Data/citation_shares_applicant.dta", replace
