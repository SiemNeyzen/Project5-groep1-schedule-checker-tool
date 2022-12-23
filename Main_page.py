# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 09:37:38 2022

@author: Siem Neyzen
"""

import streamlit as st
import pandas as pd

# This is the main page of the tool, the first page the user sees
# Its function is to inform the user about how to use the tool

st.set_page_config(
    page_title="Schedule-Checker tool",
    page_icon="🚌")

st.markdown("# Main page")

# The commands create some session state variables
# Session state allows variables to be used across the different pages 

if 'dataframe_dienstregeling' not in st.session_state:
    st.session_state['dataframe_dienstregeling'] = pd.read_excel("./data/Connexxion data - 2022-2023.xlsx", "Dienstregeling")
    
if 'dataframe_afstanden' not in st.session_state:
    st.session_state['dataframe_afstanden'] = pd.read_excel("./data/Connexxion data - 2022-2023.xlsx", "Afstand matrix")

if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False

if 'file2_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
         
# Below are the instructions that the user sees first when using the tool.   
st.write("""
         Welcome to the Schedule-Checker tool.
         
         You can check whether your schedule is valid and how well it performs.
         1. First, you upload your schedule on the upload page.
         2. Then, you can check if your schedule has any errors on the Error Check page.
         3. You can also check how well the schedule performs on the KPI page.
         4. Finally, the Gantt chart page gives a visual overview for the schedule of each bus. 
         
         You can navigate to different pages by using the sidebar on your left hand side.
         """)