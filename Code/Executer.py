"""""""""""
Executor for "Spillovers and the Direction of Innovation"

Last Modified: Eric Donald 8/25

Notes:
    
Output:
"""""""""""

import Economy as e
import Processor as p



"Define Objects"
E = e.Economy()
P = p.Processor(E)


"Calibrate"
P.Calibrate()


"Spillover Network Analysis"
P.SpillAnalysis()


"Graph of 2010s"
P.TensGraph(2010, 2021)


"Policy Reform"
P.PolicyExperiments(200)


"IAM"
P.IAM(500, 200)


"CES Spillover Robustness"
P.CES_Spill(500,200,1.25)







