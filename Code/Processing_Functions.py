"""""""""""
Processing Functions

Notes: Functions that accomplish basic processing for the project.
    
"""""""""""

import numpy as np
import requests
import zipfile
import io
import pandas as pd



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



