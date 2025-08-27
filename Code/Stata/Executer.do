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



*Relevant Patent Classes
global elec_clean_classes Y02E10 Y02E30 Y02E60/10 Y02E60/13 Y02E60/14 Y02E60/16 Y02B10/10
global elec_dirty_classes F22 F23 F27 C10J F01K F02C F02G F02B7 F02B11 F02B49 F25B27/02 F02B1/12 F02B1/14 F02B3/06 F02B3/08 F02B3/10 F02B3/12 F02B13/02 F02B13/04 B01J8/20 B01J8/22 B01J8/24 B01J8/26 B01J8/28 B01J8/30
global car_clean_classes B60L B60K1 B60K6 H01M8 B60W20 B60W10/08 B60W10/24 B60W10/26 B60W10/28 Y02T10/64 Y02T10/70 Y02T10/7072 Y02T10/72 Y02T10/92 Y02T90/10 Y02T90/12 Y02T90/14 Y02T90/16 Y02T90/167 Y02T90/40 Y02T10/62
global car_dirty_classes F02B F02D F02F F02M F02N F02P Y02T10/12 Y02T10/40
**Classes follow both CPC and IPC classification, but there is no discordance between CPC and IPC for these classes.




*******************************************************************

* Run do-files.

*******************************************************************

cd "${project}"


**********************
***Relevant Patents***
**********************
run "Empirical/Code/Relevant_Patents.do"


*********************
***Citation Shares***
*********************
run "Empirical/Code/Citation_Shares.do"


*************************
***Spillover Stability***
*************************
run "Empirical/Code/Spillover_Stability.do"


***********************
***Calibration Panel***
***********************
run "Empirical/Code/Cal_Panel.do"


