# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 18:57:58 2022

@author: Siem Neyzen
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff

st.set_page_config(
    page_title="Schedule-Checker tool",
    page_icon="🚌")

st.markdown("# Gantt Chart page")

if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
    
if 'file2_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
    
def create_gantt_chart(dataframe, nummer):
    dataframe_gantt = dataframe.copy(deep=True)
    
    st.write("A Gantt chart will be opened on a new page.")
    st.write("Caution: visiting this page after the first time will result in a new empty Gantt chart.")
    
    dataframe_gantt.replace(float('nan'), 0, inplace = True)
    
    day = '2021-10-01 '
    day2 = '2021-10-02 '
    
    dataframe_gantt['starttijd'] = [day2 + time if (int(time[1]) < 3) and (int(time[0]) == 0) else day + time for time in dataframe_gantt['starttijd']]
    dataframe_gantt['eindtijd'] = [day2 + time if (int(time[1]) < 3) and (int(time[0]) ==0) else day + time for time in dataframe_gantt['eindtijd']]
    
    df = [dict(Task = i[1]['omloop nummer'], 
          Start = i[1]['starttijd'], 
          Finish = i[1]['eindtijd'],
          Resource = i[1]['activiteit']
         ) for i in dataframe_gantt.iterrows()]
    
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True, title="Schedule " + str(nummer) + " Gantt Chart")
    #fig.show()
    st.plotly_chart(fig)
    

if st.session_state['file_uploaded'] == True:   
    dataframe = st.session_state['data']
    create_gantt_chart(dataframe, 1)
    if st.session_state['file2_uploaded'] == True:
        dataframe2 = st.session_state['data2']
        create_gantt_chart(dataframe2, 2)
        
    
else:
    st.write("A file has to be uploaded at the 'upload page' before the schedule is viewable as Gantt chart here.")