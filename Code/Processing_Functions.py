"""""""""""
Processing Functions

Notes: Functions that accomplish basic processing for the project.
    
"""""""""""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
import requests
import zipfile
import io



class ResultsTable:
    "Object for Saving Results in CSV File"
    
    def __init__(self):
        "Initialize Results Table Object"
        
        self.rows = []


    def add(self, variable, value):
        "Add Row to Table"
        
        self.rows.append({"Variable": variable, "Value": value})


    def to_csv(self, path):
        "Save Table to CSV"
        
        pd.DataFrame(self.rows).to_csv(path, index=False)
        
        
        
def clean_round(number, decimals):
    "Cut a Hanging Zero"
    
    rounded_number = np.round(number, decimals)
    if decimals == 0:
        if rounded_number == int(rounded_number):
            return int(rounded_number)
    elif decimals > 0:
        if rounded_number == np.round(rounded_number, decimals-1):
            return np.round(rounded_number, decimals-1)
    return rounded_number
    


def Extract_PatentsView(Table):
    "Download and Extract a PatentsView Bulk Table"
    
    url = f"https://s3.amazonaws.com/data.patentsview.org/download/{Table}.tsv.zip"

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        tsv_name = f"{Table}.tsv"
        with z.open(tsv_name) as f:
            df = pd.read_csv(f, sep="\t", low_memory=False)
    
    return df



def citation_shares(citations_df, relevant_df, classes, types):
    "Compute Citation Network"
    
    # ----------------------- #
    # Technology Class Labels #
    # ----------------------- #
    tech_pairs = [(c, t) for c in classes for t in types]
    col_labels = [f"{c}_{t}" for (c, t) in tech_pairs] + ["gen"]
    tech_cols  = [f"{lab}_patent" for lab in col_labels]


    # --------------------- #
    # Process into Matrices #
    # --------------------- #
    pid_to_idx = pd.Series(relevant_df.index.values, index=relevant_df['patent_id']).to_dict()

    ci = citations_df['patent_id'].map(pid_to_idx)
    cj = citations_df['citation_patent_id'].map(pid_to_idx)
    mask = ci.notna() & cj.notna()
    if not mask.any():
        K = len(tech_cols)
        return np.zeros((K, K), float), col_labels, col_labels

    ci = ci[mask].astype(int).to_numpy()
    cj = cj[mask].astype(int).to_numpy()

    F = relevant_df[tech_cols].to_numpy(dtype=float, copy=False)

    Fciting = F[ci, :]
    Fcited  = F[cj, :]


    # -------------- #
    # Compute Shares #
    # -------------- #
    counts = Fciting.T @ Fcited  # (K x K)

    row_sums = counts.sum(axis=1, keepdims=True)
    with np.errstate(invalid='ignore', divide='ignore'):
        shares = np.divide(counts, row_sums, out=np.zeros_like(counts), where=row_sums > 0)

    return shares



def run_reg(y, X, model, clusters=[]):
    "Run Regressions"
    
    if model == 'sm':
        model = sm.OLS(y, X)
        res = model.fit(cov_type="cluster", cov_kwds={"groups": clusters})
        
    if model == 'panel':
        model = PanelOLS(y, X,
                         entity_effects=True, 
                         time_effects=True)
        res = model.fit(cov_type='clustered', cluster_entity=True)

    return res



def reg_out(res, name, fmt=lambda x: f"{x:.3f}", sefmt=lambda x: f"({x:.2f})"):
    "Regression Output"
    
    b = res.params.get(name, np.nan)
    se = res.bse.get(name, np.nan)
    p = res.pvalues.get(name, np.nan)
    
    return fmt(b) + star(p), sefmt(se)



def star(p):
    "Regression Coefficient Stars"
    
    if p < 0.01: return "***"
    elif p < 0.05: return "**"
    elif p < 0.1: return "*"
    else: return ""
    
    
    