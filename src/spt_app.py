import sys
import os

import base64
import pandas as pd
import streamlit as st
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw
import itertools
import numpy as np
import json

from data import *
from run_predictions import *
from login import *

#import misc.simple_evaluation as se

#from tern_plot import calc_LLE_from_outputdf

# add src to the search path 



# Global Variables
pure_property_models = {
    'Critical values': ['base_crit_081123',{'y0': 'Tcrit', 'y1': 'Pcrit', 'y2': 'Acentric factor'}],
    'Heat of formation': ['base_crit_081123', {'y5': 'dHform'}],
    'Melting enthalpy': ['base_dHfuss_081123', {'y0': 'dHfuss'}],
    'Melting temperature': ['base_t_melt_081123', {'y0': 'Tmelt'}],
    'Heat capacity (DIPPR E107)': ['base_dHfuss_081123', {'y0': 'Cp'}], 
    'Liquid density (DIPPR E105)': ['pure_density_base', {'y0': 'rho'}],
    'Vapor pressure (DIPPR E101)': ['pure_psat_base', {'y0': 'Psat'}],
}

pure_properties = list(pure_property_models.keys())

binary_property_models = {
    'NRTL-T': ['base_NRTL_081123', {'a_1':'a_1','a_2':'a_2','t_12_1':'t_12_1','t_12_2':'t_12_2','t_12_3':'t_12_3','t_12_4':'t_12_4', 't_21_1': 't_21_1', 't_21_2': 't_21_2', 't_21_3': 't_21_3', 't_21_4': 't_21_4'}],
}
binary_properties = list(binary_property_models.keys())

# Helper Functions
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def add_sidebar_logo(image_path):
    base64_image = get_base64_image(image_path)
    logo_html = f'''
    <div style="text-align: center; margin-top: -100px; margin-bottom: -75px;">
        <img src="data:image/png;base64,{base64_image}" style="width: 100%;" />
    </div>
    '''
    st.sidebar.markdown(logo_html, unsafe_allow_html=True)

# App Layout
def app_layout():
    add_sidebar_logo('logo.png')

    st.sidebar.title('Property Prediction')
    st.sidebar.subheader('Select the desired molecular properties:')

    # Update the property selection based on the property type
    property_type = st.sidebar.radio('Type', ['Pure Properties', 'Binary Properties'])

    # Update the property selection based on the property type
    if property_type == 'Pure Properties':
        st.sidebar.write("Select Pure Component Properties:")
        selected_properties = [prop for prop in pure_properties if st.sidebar.checkbox(prop, key=prop)]
    elif property_type == 'Binary Properties':
        st.sidebar.write("Select Binary Component Properties:")
        selected_properties = [prop for prop in binary_properties if st.sidebar.checkbox(prop, key=prop)]

    # Input Options for data
    st.sidebar.subheader('Input Options:')
    input_type = st.sidebar.radio('Input Type:', ['SMILES Text', 'CSV File'])

    # Show the number of tokens used
    if 'username' in st.session_state:
        tokens_used, max_tokens = get_token_info(st.session_state['username'])
        st.sidebar.write(f"Tokens used: {tokens_used}/{max_tokens}")

    # Logout Button
    st.sidebar.markdown("---")  # Optional: Adds a line for visual separation
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()  # Rerun the app to show the login page

    if property_type == 'Pure Properties':
        if input_type == 'SMILES Text':
            process_smiles_input(selected_properties)
        else:
            process_csv_input(selected_properties)          
    elif property_type == 'Binary Properties':
        if input_type == 'SMILES Text':
            process_binary_smiles_input(selected_properties)
        else:
            process_binary_csv_input(selected_properties)

def process_smiles_input(selected_properties):
    st.subheader('Input SMILES Text:')
    input_smiles = st.text_area('Enter SMILES Text:', key="smiles_input")
    
    if st.button('Show Molecular Structure'):
        show_molecular_structure(input_smiles)

    if st.button('Run Prediction'):
        # check if input_smiles empty
        if input_smiles == '':
            st.error('Please enter SMILES text.')
            return
        input_df = smiles_to_dataframe(input_smiles)
        run_prediction(selected_properties, input_df, property_type='Pure Properties')


def process_csv_input(selected_properties):
    st.subheader('Upload CSV File:')
    input_file = st.file_uploader('Choose a CSV file', type='csv')
    if st.button('Run Prediction'):
        if input_file is None:
            st.error('Please upload a CSV file.')
            return
        input_df = csv_to_dataframe(input_file)
        run_prediction(selected_properties, input_df, property_type='Pure Properties')

def process_binary_smiles_input(selected_properties):
    # Create two columns for the binary SMILES input
    st.subheader('Input SMILES Text:')
    input_smiles = st.text_area('''Enter SMILES Text.
        , seperate mixtures with ,:''', key="smiles_input")

    if st.button('Run Prediction'):
        # check if input_smiles empty
        if input_smiles == '':
            st.error('Please enter SMILES text.')
            return
        input_df = smiles_to_dataframe(input_smiles, binary=True)
        run_prediction(selected_properties, input_df, property_type='Binary Properties')

def process_binary_csv_input(selected_properties):
    st.subheader('Upload CSV File:')
    input_file = st.file_uploader('Choose a CSV file for Component 1', type=['csv', 'txt'], key="csv_file1")
    
    if st.button('Run Prediction'):
        if input_file is None:
            st.error('Please upload a CSV file.')
            return
        input_df = csv_to_dataframe(input_file, binary=True) 
        run_prediction(selected_properties, input_df, property_type='Binary Properties')

def show_molecular_structure(input_smiles):
    smiles_list = input_smiles.split('\n')
    last_smiles = smiles_list[-1].strip()
    mol = Chem.MolFromSmiles(last_smiles)
    if mol is not None:
        img = Draw.MolToImage(mol)
        st.image(img, caption='Molecular Structure')
    else:
        st.write('Invalid SMILES code')

def run_prediction(selected_properties, input_df, property_type):
    if not selected_properties:
        st.error('Please select at least one property.')
        return

    if property_type == 'Pure Properties':
        selected_models = [pure_property_models[prop] for prop in selected_properties]
        binary = False
    elif property_type == 'Binary Properties':
        selected_models = [binary_property_models[prop] for prop in selected_properties]
        binary = True

    if len(input_df) < get_token_info(st.session_state['username'])[1] - get_token_info(st.session_state['username'])[0]:
    
        output_dfs = main_prediction(selected_models, input_df, binary)
    
        update_token_usage(st.session_state['username'], len(input_df))
    
        for model_name, df, prop in zip(selected_models, output_dfs, selected_properties):
            st.subheader(f'Output for {prop}:')
            st.write(df)

        # If you want the gPROMS download button for each model:
        
            # Initialize an empty dictionary for the JSON object
        json_object = {}

        # Iterate over each DataFrame and property
        for model_name, df, prop in zip(selected_models, output_dfs, selected_properties):
            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                smiles = row['SMILES0']  # Assuming the column name for SMILES codes is 'SMILES0'
                if smiles not in json_object:
                    json_object[smiles] = {}  # Initialize a new dictionary for this SMILES code
                json_object[smiles][prop] = row.drop('SMILES0').to_dict()  # Add the property data

        # Convert the dictionary to a JSON string
        json_string = json.dumps(json_object, indent=4)
        
        
        
        st.download_button(
            label=f"Download Output as JSON",
            data=json_string,
            file_name=f"output.json",
            mime="application/json",
        )
            
    else:
        st.write('Not enough tokens')


def add_footer():
    st.sidebar.markdown(
        "<div style='position: fixed; bottom: 0; right: 0; text-align: center; color: lightgray;'>"
        "© 2023 Benedikt Winter. All rights reserved."
        "</div>",
        unsafe_allow_html=True
    )

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if verify_user(username, password):  # Assuming verify_user is your authentication function
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password")

def main():
    # Initialize session state for logged_in if not present
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    logo_img = Image.open('logo.png')
    st.set_page_config(page_title="SPT", page_icon=logo_img, layout="wide", initial_sidebar_state="expanded")

    if not st.session_state["logged_in"]:
        login_page()
    else:
        # If logged in, run the main app
        app_layout()
        add_footer()


if __name__ == '__main__':
    main()

