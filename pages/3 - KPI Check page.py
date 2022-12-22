# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 10:51:31 2022

@author: Siem Neyzen
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Schedule-Checker tool",
    page_icon="🚌")

st.markdown("# KPI page")

st.write("This is the KPI page. "
         "An important insight to note, is that a good performance with 1 KPI doesn't mean that the schedule is good. "
         "It is important to have a good balance between performance across all KPI's.")

kolom1 = ['Number of busses the schedule uses',
          'Value of DD',
          'kWh that could be given back to the network']

#%%

def measure_performance(dataframe):
    kolom2 = [0,0,0]
    
    kolom2[0] = dataframe['omloop nummer'].nunique()
    
    totaaltijd = 0
    diensttijd = 0
    for index, row in dataframe.iterrows():
        starttijd = int(row['starttijd'][:2])*60 + int(row['starttijd'][3:5])
        eindtijd = int(row['eindtijd'][:2])*60 + int(row['eindtijd'][3:5])
        totaaltijd += eindtijd-starttijd
        if row['activiteit'] == 'dienst rit':
            diensttijd += eindtijd-starttijd
    kolom2[1] = totaaltijd/diensttijd
    
    StateOfHealth_capaciteit = 0.9
    dataframe['state of charge'] = 350*StateOfHealth_capaciteit
    bespaarde_hoeveelheid = 0
    busnummers = []
    dataframe_tijd = st.session_state['dataframe_afstanden']
    #dataframe_tijd = pd.read_excel("C:\\Users\\Siem Neyzen\\Downloads\\Connexxion data - 2022-2023.xlsx", "Afstand matrix")
    for index, row in dataframe.iterrows():
        if row['activiteit'] not in ['opladen','idle']:
            startlocatie = row['startlocatie']
            eindlocatie = row['eindlocatie']
            buslijn = row['buslijn']
            a = dataframe_tijd.loc[dataframe_tijd['startlocatie']==startlocatie]
            b = a[a['eindlocatie']==eindlocatie]
            if buslijn in [400, 401]:
                b = b[b['buslijn']==buslijn]
            elif len(b) > 1:
                b = b[b['buslijn']!=400]
                b = b[b['buslijn']!=401]
            aantal_kilometer = b.iloc[0]['afstand in meters']/1000 
            verbruik = aantal_kilometer * 1.75084
            if row['omloop nummer'] not in busnummers:
                busnummers.append(row['omloop nummer'])
                if row['state of charge'] == 350*StateOfHealth_capaciteit: 
                    dataframe.at[index, 'state of charge'] = (350*StateOfHealth_capaciteit) - verbruik
                else:
                    # assumptie wordt gemaakt dat het verbruik van de eerste rit in dat geval al mee is genomen
                    bespaarde_hoeveelheid += (350*StateOfHealth_capaciteit) - row['state of charge']
            else:
                dataframe.at[index, 'state of charge'] = float(dataframe.iloc[index-1]['state of charge']) - verbruik
        else:
            starttijd = int(row['starttijd'][:2])*60 + int(row['starttijd'][3:5])
            eindtijd = int(row['eindtijd'][:2])*60 + int(row['eindtijd'][3:5])
            # voor wanneer de klok van 23:.. naar 00:.. gaat:    
            if int(row['starttijd'][:2]) == 23 and int(row['eindtijd'][:2]) < 23:
                eindtijd = (24+int(row['eindtijd'][:2]))*60 + int(row['eindtijd'][3:5])
            tijd = eindtijd-starttijd
            
            if row['activiteit'] == 'idle':
                verbruik = tijd/60 * 0.01
                dataframe.at[index, 'state of charge'] = float(dataframe.iloc[index-1]['state of charge']) - verbruik
            
            elif row['activiteit'] == 'opladen':
                kwh_tot_90_procent = (350*StateOfHealth_capaciteit)*0.9 - float(dataframe.iloc[index-1]['state of charge'])
                tijd_tot_90_procent = kwh_tot_90_procent/250 * 60
                if tijd_tot_90_procent > tijd:
                    opladen_eerste_deel = tijd_tot_90_procent/60 * 250
                    opladen_tweede_deel = (tijd - tijd_tot_90_procent)/60 * 60
                    opladen = opladen_eerste_deel + opladen_tweede_deel
                else:    
                    opladen = tijd/60 * 250
                if float(dataframe.iloc[index-1]['state of charge']) + opladen < 350*StateOfHealth_capaciteit:
                    dataframe.at[index, 'state of charge'] = float(dataframe.iloc[index-1]['state of charge']) + opladen
                else:
                    dataframe.at[index, 'state of charge'] = 350*StateOfHealth_capaciteit      
    kolom2[2] = bespaarde_hoeveelheid
        
    return(kolom2)


#%%


if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False

if st.session_state['file_uploaded'] == True:         
    dataframe = st.session_state['data']
    kolom_planning1 = measure_performance(dataframe)
    if st.session_state['file2_uploaded'] == True:
        dataframe2 = st.session_state['data2']
        kolom_planning2 = measure_performance(dataframe2)
        st.write("""
                 The table below compares the performance of the two different schedules. 
                 Below it are bar charts that visualise the differences between the two for each KPI.
                 """)
        performance_vergelijken_dictionary = {'KPI': kolom1, 'Performance - Schedule 1': kolom_planning1, 'Performance - Schedule 2': kolom_planning2}
        performance_vergelijken_dataframe = pd.DataFrame(data = performance_vergelijken_dictionary)
        
        st.table(performance_vergelijken_dataframe)
        
        st.header(" ")
        st.header("Number of buses")
        fig = px.bar(pd.DataFrame(data=[kolom_planning1[0],kolom_planning2[0]], index=['schedule 1', 'schedule 2'], columns=['number of buses']))
        st.plotly_chart(fig)
        st.write("The chart above compares the amount of buses both schedules use. "
                 "It is generally better to have this number be as low as possible.")
        
        st.header(" ")
        st.header("\n Value of DD")
        fig = px.bar(pd.DataFrame(data=[kolom_planning1[1],kolom_planning2[1]], index=['schedule 1', 'schedule 2'], columns=['value of DD']), range_y=[1,2])
        st.plotly_chart(fig)
        st.write("The chart above compares the value of DD of both schedules. "
                 "This value represents how many hours a bus drives in total, to drive 1 hour as a bus service. "
                 "The goal is to have this value be as low as possible, with the lowest value possible being 1. "
                 "Generally, values between 1,2 and 1,7 can be expected.")
        
        st.header(" ")
        st.header("\n kWh back to network")
        fig = px.bar(pd.DataFrame(data=[kolom_planning1[2],kolom_planning2[2]], index=['schedule 1', 'schedule 2'], columns=['kWh back to network']))
        st.plotly_chart(fig)
        st.write("The chart above compares amount of kWh that can be given back to the network of both schedules. "
                 "This happens when a bus starts with a State of Charge value lower than 315 kWh, which is the maximum. "
                 "The goal is to have this value be as high as possible, because it means that more electricity can be sold back to the provider. "
                 "However, it is important that performing well with this KPI doesn't negatively influence the performance for the other KPI's. "
                 "Checking if that isn't the case is advisable.")
        
    else:
        KPI_dictionary = {'KPI': kolom1, 'Performance': kolom_planning1}
        KPI_dataframe = pd.DataFrame(data = KPI_dictionary)
        st.table(KPI_dataframe)
        
        st.header(" ")
        st.header("Number of buses")
        st.write("The schedule uses " + str(kolom_planning1[0]) + " buses.")
        st.write("It is generally preferable to have the amount of buses be as low as possible.")
        st.subheader('🚌'*kolom_planning1[0])
        
        st.header(" ")
        st.header("Value of DD")
        st.write("The value of DD is " + str(round(kolom_planning1[1],4)) + ".")
        st.write("The goal is to have DD be as low as possible, with 1 being to lowest it can be. "
                 "This value represents how many hours a bus drives in total, to drive 1 hour as a bus service. "
                 "Generally, the value can be expected to be between 1,2 and 1,7 or close to those values.")
        
        st.header(" ")
        st.header("kWh back to network")
        st.write("The amount of kWh that goes back to the network is " + str(round(kolom_planning1[2],4)) + ".")
        st.write("This happens when a bus starts with a State of Charge value lower than 315 kWh, which is the maximum. "
            "The higher this amount is, the more money can be made by selling electricity back to the provider. "
                 "However, it is important that performing well with this KPI doesn't negatively influence the performance for the other KPI's. "
                 "Checking if that isn't the case is advisable.")

    
else:
    st.write("A file has to be uploaded at the 'upload page' before its performance becomes visible here.")