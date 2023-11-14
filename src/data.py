
import pandas as pd
import numpy as np
import itertools

# Input Processing Functions
def smiles_to_dataframe(smiles_text, binary=False):

    smiles_list = [smiles.strip() for smiles in smiles_text.split('\n')]
    smiles_list = [smiles for smiles in smiles_list if smiles != '']
    # if binary split by comma
    if binary:
        smiles_list = [smiles.split(',') for smiles in smiles_list]
        smiles0, smiles1 = zip(*smiles_list)
        df = pd.DataFrame({'SMILES0': smiles0, 'SMILES1': smiles1})
    else:
        df = pd.DataFrame({'SMILES0': smiles_list})
    
    df['c0'] = 1
    df['c1'] = 298.15
    df['c2'] = 0.0
    df['c3'] = 0.0
    return df


def csv_to_dataframe(csv_file, binary=False):
    df = pd.read_csv(csv_file, header=0)
    
    if binary:
        if 'SMILES1' not in df.columns:
            if 'SMILES0' in df.columns:
                # Get all binary combinations
                combinations = list(itertools.combinations(df['SMILES0'], 2))
                smiles0, smiles1 = zip(*combinations)
                df = pd.DataFrame({'SMILES0': smiles0, 'SMILES1': smiles1})
            else:
                raise ValueError("CSV file must have at least one column named 'SMILES0' or both 'SMILES0' and 'SMILES1'")
        else:
            df = df[['SMILES0', 'SMILES1']]
    else:
        if 'SMILES0' not in df.columns:
            raise ValueError("CSV file must have a column named 'SMILES0'")
        df = df[['SMILES0']]

    df['c0'] = 1
    df['c1'] = 298.15
    df['c2'] = 0.0
    df['c3'] = 0.0

    df = pd.concat([df.iloc[0:1], df], ignore_index=True)

    return df

def lle_to_dataframe(smiles_list):

    combinations = list(itertools.combinations(smiles_list, 2))
    smiles0, smiles1 = zip(*combinations)
    df = pd.DataFrame({'SMILES0': smiles0, 'SMILES1': smiles1})

    df['c0'] = 1
    df['c1'] = 298.15
    df['c2'] = 0.0
    df['c3'] = 0.0
    df['y0'] = 0.0
    df['y1'] = 0.0
    df['y2'] = 0.0

    # add a copy off the first row to the top of the dataframe
    df = pd.concat([df.iloc[0:1], df], ignore_index=True)
    
    return df

def smiles_to_dataframe_multiple():
    pass