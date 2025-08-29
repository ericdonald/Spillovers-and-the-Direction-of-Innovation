/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
Executer

Last Modified: Eric Donald 4/24

Notes: This file executes the other do-files associated with Spillovers and the Direction of Innovation. 
    
Output: 

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
clear all



*******************************************************************

* Define project globals.

*******************************************************************




*******************************************************************

* Run do-files.

*******************************************************************

cd "${project}"


*********************
***Citation Shares***
*********************
run "Empirical/Code/Citation_Shares.do"


*************************
***Spillover Stability***
*************************
run "Empirical/Code/Spillover_Stability.do"



