"""""""""""
Executor

Notes: This file executes the code for "Spillovers and the Direction of Innovation".
    
"""""""""""

import Economy as e
import Processor as p


# ----------------------------------------------------------------

# Define project objects.

# ----------------------------------------------------------------

E = e.Economy()
P = p.Processor(E)


# ----------------------------------------------------------------

# Run project methods.

# ----------------------------------------------------------------

# ---------- #
# Clean Data #
# ---------- #
P.Cleaner()


# -------------------------- #
# Spillover Network Analysis #
# -------------------------- #
P.SpillAnalysis()


# --------------------- #
# Spillover Regressions #
# --------------------- #
P.SpillReg()


# --------- #
# Calibrate #
# --------- #
P.Calibrate()


# -------------- #
# Graph of 2010s #
# -------------- #
P.TensGraph(2010, 2021)


# ------------- #
# Policy Reform #
# ------------- #
P.PolicyExperiments(200)


# --- #
# IAM #
# --- #
P.IAM(500, 200)


# ------------------------ #
# CES Spillover Robustness #
# ------------------------ #
P.CES_Spill(500, 200, 1.25)


# ----------------------- #
# Record Package Versions #
# ----------------------- #
packages = ["linearmodels", "matplotlib", "numba", "numpy", "openpyxl", "pandas", "quantecon", "scipy", "statsmodels"]
P.write_package_versions(packages)




