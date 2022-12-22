# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 12:54:22 2022

@author: Siem Neyzen
"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Schedule-Checker tool",
    page_icon="🚌")

st.markdown("# Upload page")

st.write("""
         Upload a schedule using the right format and as a '.xslx' file.
         """)

if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
    
if 'file2_uploaded' not in st.session_state:
    st.session_state['file2_uploaded'] = False


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        dataframe = pd.read_excel(uploaded_file, engine='openpyxl')
        if list(dataframe.columns) == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer'] or list(dataframe.columns) == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer','state of charge']:
            if 'data' not in st.session_state:
                st.session_state['data'] = dataframe
                st.session_state['file_uploaded'] = True
        else:
         st.write("The uploaded file does not have the right format."
                  "The file should have the following columns:")
         st.write("'startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer' (and having a column 'state of charge' is optional to gain more insight)")
         st.write("Please try again using a file with the correct format.")
    else:
        st.write("The uploaded file is not an .xlsx file. Please try again using the correct file type.")
        
if st.session_state['file_uploaded'] == True:
    st.write("you can upload a second schedule if you want to compare the performance between the two.")
    uploaded_file2 = st.file_uploader("(Optional) Choose a second file")
        
    if uploaded_file2 is not None:
        if uploaded_file2.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            dataframe2 = pd.read_excel(uploaded_file2, engine='openpyxl')
            if list(dataframe2.columns) == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer'] or list(dataframe2.columns) == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer','state of charge']:
                if 'data2' not in st.session_state:
                    st.session_state['data2'] = dataframe2
                    st.session_state['file2_uploaded'] = True
            else:
             st.write("The uploaded file does not have the right format."
                      "The file should have the following columns:")
             st.write("'startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer' (and having a column 'state of charge' is optional to gain more insight)")
             st.write("Please try again using a file with the correct format.")
        else:
            st.write("The uploaded file is not an .xlsx file. Please try again using the correct file type.")