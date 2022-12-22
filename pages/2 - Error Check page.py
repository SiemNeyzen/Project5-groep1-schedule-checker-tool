# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 10:49:17 2022

@author: Siem Neyzen
"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Schedule-Checker tool",
    page_icon="🚌")

st.markdown("# Error Check page")

kolom1 = ['A bus has an incorrect starting- or final destination',
          'A bus departs from a wrong destination',
          'Number of times that a bus service is not covered by a bus',
          'Number of times a bus service is covered by more than 1 bus',
          'A bus does not have enough time to go from one location to the next',
          'A bus is given too much time to go from one location to the next',
          'A bus is below the desired minimum state of charge while still driving',
          'A bus charges for less then 15 minutes']

if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False

#%%
# function to check for errors

def checking_errors(dataframe):
    kolom2 = [0,0,0,0,0,0,0,0]
    index_lijsten_voor_fouten = [[],[[],[]],[],[[],[]],[],[],[],[]]
    
    # Error 0: Incorrect starting- or final destination
    # This occurs when a bus doesn't start or end in the garage
    planning_andersom = dataframe[::-1]
    aantal_omlopen = dataframe['omloop nummer'].value_counts().count()
    fout_startpunt = []
    fout_eindpunt = []
    for i in range(aantal_omlopen):
        eerste_index = dataframe[dataframe['omloop nummer']==i+1].index[0]
        eerste_locatie = dataframe['startlocatie'][eerste_index]
        if eerste_locatie != 'ehvgar':
            fout_startpunt.append(i+1)
        laatste_index = planning_andersom[planning_andersom['omloop nummer']==i+1].index[0]
        laatste_locatie = planning_andersom['eindlocatie'][laatste_index]
        if laatste_locatie != 'ehvgar':
            fout_eindpunt.append(i+1)
    kolom2[0] += len(fout_startpunt) + len(fout_eindpunt)
    index_lijsten_voor_fouten[0].extend(fout_startpunt + fout_eindpunt)
    
    
    # Error 1: A bus departs from a wrong destination
    # This occurs when a startlocation of bus differs from its most recent location 
    
    totaal_index = 0
    for i in range(aantal_omlopen+1)[1::]:
        dataframe_omloop = dataframe[dataframe['omloop nummer'] == i]                   #making a new dataframe that only includes bus i
        dataframe_omloop['startlocatie'] = dataframe_omloop['startlocatie'].shift(-1)   #move all rows in the column 'startlocatie' 1 up
        dataframe_omloop = dataframe_omloop[:-1]                                        #lowest row isn't needed, which is why it's removed
        for j in range(len(dataframe_omloop['startlocatie'])):                                        #repeat this for every row for each dataframe
            if dataframe_omloop.iloc[j]['startlocatie'] != dataframe_omloop.iloc[j]['eindlocatie']:
                if i not in index_lijsten_voor_fouten[1][0]:
                    index_lijsten_voor_fouten[1][0].append(i)
                    index_lijsten_voor_fouten[1][1].append([])
                if i == 1:
                    index_fout = totaal_index + j
                else:
                    index_fout = totaal_index + j + 1
                index_lijsten_voor_fouten[1][1][-1].append(index_fout)
                kolom2[1] += 1
        if i == 1:
            totaal_index += j + 1
        else:
            totaal_index += j + 2
    
    
    # Error 2 & 3: Number of times that a bus service is not covered by a bus, or covered more than once
    
    dataframe_dienstregeling = st.session_state['dataframe_dienstregeling']
    #dataframe_dienstregeling = pd.read_excel("C:\\Users\\Siem Neyzen\\Downloads\\Connexxion data - 2022-2023.xlsx", "Dienstregeling")
    
    bussen_bezetting_lijst = [[] for i in range(len(dataframe_dienstregeling.index))]
    
    for index, row in dataframe.iterrows():
        if row['buslijn'] in [400, 401]:
            tijd = row['starttijd'][:-3] # Slicing to remove the seconds
            index_dienst = dataframe_dienstregeling.index[dataframe_dienstregeling['vertrektijd']==tijd].tolist()
            dataframe_zelfde_tijd = dataframe_dienstregeling[dataframe_dienstregeling['vertrektijd']==tijd]
            if len(index_dienst) > 0:
                for index2, row2 in dataframe_zelfde_tijd.iterrows():
                    if row['startlocatie'] == row2['startlocatie']:
                        bussen_bezetting_lijst[index_dienst[index_dienst.index(index2)]].append(row['omloop nummer'])
            
    for i in range(len(bussen_bezetting_lijst)):
        if len(bussen_bezetting_lijst[i]) == 0:
            kolom2[2] += 1
            index_lijsten_voor_fouten[2].append(i)
        elif len(bussen_bezetting_lijst[i]) > 1:
            kolom2[3] += 1
            index_lijsten_voor_fouten[3][0].append(i)
            index_lijsten_voor_fouten[3][1].extend(bussen_bezetting_lijst[i])
            
    
    # Error 4 & 5: A bus does not have enough time to go from one location to the next, or it is given too much time
    # These errors occur if the amount of time a bus is given to travel between locations is less than the minimum neccesary time or higher than the maximum neccesary time
    
    dataframe_tijd = st.session_state['dataframe_afstanden']
    #dataframe_tijd = pd.read_excel("C:\\Users\\Siem Neyzen\\Downloads\\Connexxion data - 2022-2023.xlsx", "Afstand matrix")
    
    for index, row in dataframe.iterrows():
        if row['activiteit'] not in ['opladen','idle']:
            starttijd = int(row['starttijd'][:2])*60 + int(row['starttijd'][3:5])
            eindtijd = int(row['eindtijd'][:2])*60 + int(row['eindtijd'][3:5])
            # voor wanneer de klok van 23:.. naar 00:.. gaat:    
            if int(row['starttijd'][:2]) == 23 and int(row['eindtijd'][:2]) < 23:
                eindtijd = (24+int(row['eindtijd'][:2]))*60 + int(row['eindtijd'][3:5])
            
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
                
            geplande_tijd = eindtijd-starttijd
            if geplande_tijd < b['min reistijd in min'].iloc[0]:
                kolom2[4] += 1
                index_lijsten_voor_fouten[4].append(index)
            if geplande_tijd > b['max reistijd in min'].iloc[0]:
                kolom2[5] += 1
                index_lijsten_voor_fouten[5].append(index)
                
    
    
    # Error 6: A bus is below the desired minimum state of charge while still driving
    # This 
    StateOfHealth_capaciteit = 0.9
    if 'state of charge' not in list(dataframe.columns):
        dataframe['state of charge'] = 350*StateOfHealth_capaciteit
    dataframe['state of charge'] = dataframe['state of charge'].astype(float)
    busnummers = []
    
    # add State of Charge to dataframe
    for index, row in dataframe.iterrows():
        if row['activiteit'] not in ['opladen','idle']:
            # identficeren van busrit
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
                if row['state of charge'] == 350*StateOfHealth_capaciteit: #als de SoC lager dan 350 is, gaan we ervan uit dat het verbruik van de eerste rit al meegenomen is
                    dataframe.at[index, 'state of charge'] = 350*StateOfHealth_capaciteit - verbruik
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

    for index, row in dataframe.iterrows():
        if row['state of charge'] < (350*StateOfHealth_capaciteit)*0.1:
            kolom2[6] += 1
            index_lijsten_voor_fouten[6].append(index + 1)
        
    # Error 7: A bus charges for less then 15 minutes
    # This error obviously occurs if a charging period is less than 15 minutes
    
    for index, row in dataframe.iterrows():
        if row['activiteit'] == 'opladen':
            starttijd = int(row['starttijd'][:2])*60 + int(row['starttijd'][3:5])
            eindtijd = int(row['eindtijd'][:2])*60 + int(row['eindtijd'][3:5])
            # voor wanneer de klok van 23:.. naar 00:.. gaat:    
            if int(row['starttijd'][:2]) == 23 and int(row['eindtijd'][:2]) < 23:
                eindtijd = (24+int(row['eindtijd'][:2]))*60 + int(row['eindtijd'][3:5])
            if eindtijd - starttijd < 15:
                kolom2[7] += 1
                index_lijsten_voor_fouten[7].append(index + 1)
    
    return(kolom2, index_lijsten_voor_fouten)

#%%
# Function to make a table

def make_table(kolom2):
    st.write("""
         The table below containts the different kind of errors that can occur in the schedule.
         """)
    
    fouten_dictionary = {'Kind of error': kolom1, 'Number of errors': kolom2}
    fouten_dataframe = pd.DataFrame(data = fouten_dictionary)
      
    st.table(fouten_dataframe)

    if kolom2 == [0,0,0,0,0,0,0,0]:
        st.subheader("✅ The schedule is feasible and can be used! ✅")
    
    if kolom2[0] > 0:
        st.write("Error 0 (A bus has an incorrect starting- or final destination) occured at least once. "
                 "This means one or more busses aren't scheduled to start or finish in the garage, which is a problem. "
                 "This can be solved by adding an extra trip for that bus to go from/to the garage to its incorrect location. "
                 "The affected busses are the following:")
        for i in index_lijsten_voor_fouten[0]:
            st.write("- bus " + str(i))

    if kolom2[1] > 0:
        st.write("Error 1 (A bus departs from a wrong destination) occured at least once. "
                 "This means that a bus departed from a different destination compared to its previous final destination. "
                 "This can be solved by adding an extra trip for that bus to go from the previous final destination to the current starting point. "
                 "The buses and rows for which this error occurs are the following:")
        for i in range(len(index_lijsten_voor_fouten[1][0])):
            st.write("- bus " + str(index_lijsten_voor_fouten[1][0][i]))
            for j in index_lijsten_voor_fouten[1][1][i]:
                st.write("    • row " + str(j+2))
                         
    if kolom2[2] > 0:
        st.write("Error 2 (Number of times that a bus service is not covered by a bus) occured at least once. "
                 "This can be solved by making sure that a bus that isn't occupied at that time covers it, or by adding a new bus to cover the bus service. "
                 "The rows of the bus services that weren't covered are the following (these rows refer to the 'dienstregeling' file):")
        for i in range(len(index_lijsten_voor_fouten[2])):
            st.write("- row " + str(index_lijsten_voor_fouten[2][i] + 2))
        
    if kolom2[3] > 0:
        st.write("Error 3 (Number of times a bus service is covered by more than 1 bus) occured at least once. "
                 "This can be solved by changing the schedule of all but one busses to make sure that they get to the right destination without unnecessarily occupying a bus service. "
                 "The rows and buses for which this error occurs are the following (these rows refer to the 'dienstregeling' file):")
        for i in range(len(index_lijsten_voor_fouten[3][0])):
            st.write("- row" + str(index_lijsten_voor_fouten[3][0][i] + 1) + ' occupied by buses:')
            for j in range(len(index_lijsten_voor_fouten[3][1])):
                st.write("    • bus " + str(index_lijsten_voor_fouten[3][1][j]))
        
    if kolom2[4] > 0:
        st.write("Error 4 (A bus does not have enough time to go from one location to the next) occured at least once. "
                 "This means that a bus is given less than the minimum amount of time needed to travel between specific two locations. "
                 "If there is leeway, the solution is to add time to match the minimum amount of time necessary. "
                 "If there is no leeway, solving the problem will be complex and will require a thorough examination of the schedule. "
                 "The rows in which this error occurs are the following:")
        for i in range(len(index_lijsten_voor_fouten[4])):
            st.write("- row " + str(index_lijsten_voor_fouten[4][i]+1))

    if kolom2[5] > 0:
        st.write("Error 5 (A bus is given too much time to go from one location to the next) occured at least once. "
                 "This means that a bus is given more than the maximum amount of time needed to travel between specific two locations. "
                 "This is a problem because it influences calculations about the efficiency of the schedule and messes with the possible break time for a bus driver. "
                 "This can be solved by lowering the arival time to match the maximum amount of time needed. "
                 "The rows in which this error occurs are the following:")
        for i in range(len(index_lijsten_voor_fouten[5])):
            st.write("- row " + str(index_lijsten_voor_fouten[5][i]+1))
            
    if kolom2[6] > 0:
        st.write("Error 6 (A bus is below the desired minimum state of charge while still driving) occured at least once. "
                 "This means that a bus is driving while it should be charging, which is when its State of Charge is below 10% of the State of Health (wich is assumed to be 315 kWh, 90% capacity of 350 kWh). "
                 "This can be solved by having the bus go charge earlier, while making sure that another bus covers the bus services that the undercharged bus was meant to cover. "
                 "The rows in which this error occurs are the following:")
        for i in range(len(index_lijsten_voor_fouten[6])):
            st.write("- row " + str(index_lijsten_voor_fouten[6][i]+1))          
        
    if kolom2[7] > 0:
        st.write("Error 7 (A bus charges for less then 15 minutes) occured at least once. "
                 "This is a problem because it is determined that a bus should charge for at least 15 minutes. "
                 "This can be solved by increase the amount of time charging to at least 15 minutes. "
                 "this is no problem if there is leeway. If there isn't, then another bus needs to cover the bus services that the charging bus was meant to take. "
                 "The rows in which this error occurs are the following:")
        for i in range(len(index_lijsten_voor_fouten[7])):
            st.write("- row " + str(index_lijsten_voor_fouten[7][i]+1))



#%%
# Execute functions

if st.session_state['file_uploaded'] == True:
    dataframe = st.session_state['data']
    kolom_planning1, index_lijsten_voor_fouten = checking_errors(dataframe)
    if st.session_state['file2_uploaded'] == True:
        dataframe2 = st.session_state['data2']
        kolom_planning2, index_lijsten_voor_fouten2 = checking_errors(dataframe2)
        st.write("""
                 The table below compares the errors of the two different schedules. 
                 Below it are the individual tables and the explanation for each occured error.
                 """)
        fouten_vergelijken_dictionary = {'Kind of error': kolom1, 'Number of errors - Schedule 1': kolom_planning1, 'Number of errors - Schedule 2': kolom_planning2}
        fouten_vergelijken_dataframe = pd.DataFrame(data = fouten_vergelijken_dictionary)
      
        st.table(fouten_vergelijken_dataframe)
        
        st.header("\n")
        st.header("Schedule 1 errors:")
    
    make_table(kolom_planning1)
    if st.session_state['file2_uploaded'] == True:
        st.header("\n")
        st.header("Schedule 2 errors:")
        make_table(kolom_planning2)
    
# If a correct file hasn't been uploaded yet
else:
    st.write("A file has to be uploaded at the 'upload page' before its errors can be shown here.")