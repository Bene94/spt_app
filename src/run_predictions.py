import pandas as pd
import streamlit as st
import torch

# improt se form ~/SPT/src/misc/simple_evaluation.py
import sys
import os

spt_dir = '../SPT/src'

sys.path.append(os.path.abspath(spt_dir))
import misc.simple_evaluation as se

from contextlib import contextmanager

@contextmanager
def temporary_directory_change(new_directory):
    """Context manager to temporarily change the working directory."""
    original_directory = os.getcwd()
    try:
        os.chdir(new_directory)
        yield
    finally:
        os.chdir(original_directory)

def process_input_df(input_df, model):
    # Process input dataframe and run evaluation based on the model
    input_df['c0'] = 1
    input_df['c1'] = 298.15

    return input_df

def main_prediction(models,input_df, binary=False):

    print('Selected models: ', models)

    if input_df is not None:
        output_dfs = []

        for model, out_parameter in models:

            print('Running model: ', model)

            input_df_temp = process_input_df(input_df, model)

            with temporary_directory_change(spt_dir):
                model, config, criterion  = se.model_loader(model)
                temp_results = se.simpel_evaluation(model, config, criterion, input_df_temp)
                torch.cuda.empty_cache()

            output_df = pd.DataFrame.from_dict(temp_results)

            output_df = post_processing(output_df, out_parameter, binary)

            output_dfs.append(output_df)   

    return output_dfs         

def post_processing(output_df, out_parameter, binary=False):
    
    if binary:
        fields = ['SMILES0', 'SMILES1'] + list(out_parameter.keys())
    else:
        fields = ['SMILES0'] + list(out_parameter.keys())
    
    output_df = output_df[fields]
    output_df = output_df.rename(columns=out_parameter)

    return output_df