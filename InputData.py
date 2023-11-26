import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from energyConsumption import energyConsumption


# Interaktiver Benutzereingabe für das Datum
selected_date_str = input("Bitte geben Sie das Datum im Format TT.MM.JJJJ ein: ")
selected_date = datetime.strptime(selected_date_str, "%d.%m.%Y")

start_time = time.time()  # Startzeit des Programms

# Dateinamen
file_production = 'Realisierte_Erzeugung_202001010000_202212312359_Viertelstunde.csv'
file_consumption = 'Realisierter_Stromverbrauch_202001010000_202212312359_Viertelstunde.csv'

# Einlesen der Daten aus CSV-Dateien
production_df = pd.read_csv(file_production, delimiter=';')
consumption_df = pd.read_csv(file_consumption, delimiter=';')

# Spaltenbezeichnungen
DATE = 'Datum'
STARTTIME = 'Anfang'
BIOMAS = 'Biomasse [MWh] Originalauflösungen'
HYDROELECTRIC = 'Wasserkraft [MWh] Originalauflösungen'
WIND_OFFSHORE = 'Wind Offshore [MWh] Originalauflösungen'
WIND_ONSHORE = 'Wind Onshore [MWh] Originalauflösungen'
PHOTOVOLTAIC = 'Photovoltaik [MWh] Originalauflösungen'
OTHER_RENEWABLE = 'Sonstige Erneuerbare [MWh] Originalauflösungen'
CONSUMPTION = 'Gesamt (Netzlast) [MWh] Originalauflösungen'

# Umwandlung von Datumsspalten in DateTime-Objekte
production_df[DATE] = pd.to_datetime(production_df[DATE], format='%d.%m.%Y')
production_df[STARTTIME] = pd.to_datetime(production_df[STARTTIME], format='%H:%M')
consumption_df[DATE] = pd.to_datetime(consumption_df[DATE], format='%d.%m.%Y')
consumption_df[STARTTIME] = pd.to_datetime(consumption_df[STARTTIME], format='%H:%M')

# Bereinigung von Datenformaten der erneubaren Energien
columns_to_clean = [HYDROELECTRIC, BIOMAS, WIND_OFFSHORE, WIND_ONSHORE, PHOTOVOLTAIC, OTHER_RENEWABLE]
for column in columns_to_clean:
    production_df[column] = production_df[column].str.replace(".", "").str.replace(",", ".").replace('-', 0).astype(
        float)

# Bereinigung von Datenformaten des Gesamtenstromverbrauches
consumption_df[CONSUMPTION] = consumption_df[CONSUMPTION].str.replace(".", "").str.replace(",", ".").astype(float)

production_df['Total Production'] = production_df[columns_to_clean].sum(axis=1)
production_by_year = production_df.groupby(production_df[DATE].dt.year)['Total Production'].sum()
consumption_by_year = consumption_df.groupby(consumption_df[DATE].dt.year)[CONSUMPTION].sum()

production_by_type_and_year = production_df.groupby(production_df[DATE].dt.year)[columns_to_clean].sum()

pd.options.display.float_format = '{:.2f}'.format  # Set Pandas to display floating-point numbers with two decimal places

data_by_year = {}  # Aggregation der Daten nach Jahren und Speicherung in einem Dictionary

for year, data in production_df.groupby(production_df[DATE].dt.year):
    production_data = data[columns_to_clean].sum()
    consumption_data = consumption_df[consumption_df[DATE].dt.year == year][CONSUMPTION]
    total_consumption = consumption_data.sum()
    data_by_year[year] = {'Production': production_data.sum(), 'Consumption': total_consumption,
                          BIOMAS: production_data[BIOMAS], HYDROELECTRIC: production_data[HYDROELECTRIC],
                          WIND_OFFSHORE: production_data[WIND_OFFSHORE], WIND_ONSHORE: production_data[WIND_ONSHORE],
                          PHOTOVOLTAIC: production_data[PHOTOVOLTAIC],
                          OTHER_RENEWABLE: production_data[OTHER_RENEWABLE]}

for year, data in data_by_year.items():  # Ausgabe der aggregierten Daten pro Jahr
    print(f"Year: {year}")
    print(f"Total Renewable Energy Production: {data['Production']} MWh")
    print(f"Total Consumption: {data['Consumption']} MWh")
    print(f"Biomasse: {data[BIOMAS]} MWh")
    print(f"Wasserkraft: {data[HYDROELECTRIC]} MWh")
    print(f"Wind Offshore: {data[WIND_OFFSHORE]} MWh")
    print(f"Wind Onshore: {data[WIND_ONSHORE]} MWh")
    print(f"Photovoltaik: {data[PHOTOVOLTAIC]} MWh")
    print(f"Sonstige Erneuerbare: {data[OTHER_RENEWABLE]} MWh")
    print()

total_renewable_production = production_df[columns_to_clean].sum(axis=1)
total_consumption = consumption_df[CONSUMPTION]

# Filtern der Daten für das ausgewählte Datum
selected_production = production_df[production_df[DATE] == selected_date]
selected_consumption = consumption_df[consumption_df[DATE] == selected_date]

end_time = time.time()  # The time at the end of the program is stored
duration = end_time - start_time  # Duration of the program is calculated
print("Duration of the program: ", round(duration, 2))

# Berechnung der prozentualen Anteile der erneuerbaren Energieerzeugung am Gesamtverbrauch
percent_renewable = total_renewable_production / total_consumption * 100

counts, intervals = np.histogram(percent_renewable, bins=np.arange(0, 111, 1))  # Use NumPy to calculate the histogram of the percentage distribution

x = intervals[:-1]  # Define the x-axis values as the bin edges
labels = [f'{i}%' for i in range(0, 111, 1)]  # Create labels for x-axis ticks (von 0 bis 111 in Einzelnschritten)

fig = go.Figure(data=[go.Bar(x=x, y=counts)])  # Create a bar chart using Plotly

fig.update_layout(
    xaxis=dict(tickmode='array', tickvals=list(range(0, 111, 5)), ticktext=labels[::5]))  # X-axis label settings

# Title and axis labels settings
fig.update_layout(title='Anzahl der Viertelstunden in Jahren 2020-2022 mit 0-110 % EE-Anteilen',
                  xaxis_title='Prozentsatz erneuerbarer Energie',
                  yaxis_title='Anzahl der Viertelstunden')

fig.show()

# Plotting with Plotly
# Create a new Plotly subplot figure
fig = make_subplots()

# Add the energy consumption trace
fig.add_trace(
    go.Scatter(
        x=selected_consumption[STARTTIME].dt.strftime('%H:%M'),
        y=selected_consumption[CONSUMPTION],
        mode='lines',
        name='Total Consumption',
        fill='tozeroy'
    )
)

# Add the renewable energy production trace
fig.add_trace(
    go.Scatter(
        x=selected_production[STARTTIME].dt.strftime('%H:%M'),
        y=selected_production['Total Production'],
        mode='lines',
        name='Total Renewable Production',
        fill='tozeroy'
    )
)

fig.update_layout(
    title=f'Energy Production and Consumption on {selected_date}',
    xaxis=dict(title='Time (hours)'),
    yaxis=dict(title='Energy (MWh)'),
    showlegend=True
)

# Show the plot using st.plotly_chart
fig.show()
# st.plotly_chart(fig)

#---------------------------------------------------------------------------------------------------------------------
# code to make 2030 prediction
# 2030 prediction



# Abfrage datum
while True:
    selected_date_str = input("Bitte geben Sie ein Datum IM JAHR 2030 im Format TT.MM.JJJJ ein: ")
    selected_date = datetime.strptime(selected_date_str, "%d.%m.%Y")

    if selected_date.year == 2030:
        break
    else:
        print("Bitte geben Sie ein Datum aus dem Jahr 2030 an.")

# Define a dataframe of the production of 2022
production_2022df = production_df[production_df[DATE].dt.year == 2022]
prognoseErzeugung2030df = production_2022df.copy()
prognoseErzeugung2030df['Datum'] = prognoseErzeugung2030df['Datum'].map(lambda x: x.replace(year=2030))

# Define a dataframe of the consumption of 2022
consumption_2022df = consumption_df[consumption_df[DATE].dt.year == 2022]
prognoseVerbrauch2030df = consumption_2022df.copy()
prognoseVerbrauch2030df['Datum'] = prognoseVerbrauch2030df['Datum'].map(lambda x: x.replace(year=2030))

# CHANGE LATER Define the factors Verbrauch 2022 to 2030 von Bjarne Noah
# Verbrauch2022_2030_factor = 1.157  # assuming consumption will increase by 10% from 2022 compared to 2030


def scale_2030_factorsConsumption(df, Verbrauch2022_2030_factor):
    df_copy = df.copy()
    df_copy[CONSUMPTION] *= Verbrauch2022_2030_factor
    return df_copy


'''
#LATER put in Verbrauch 2030 fron noah&bjarne
prognoseVerbrauch2030df = energyConsumption(consumption_df)
'''
# Define the factors
# müssen noch angepasst werden
windonshore_2030_factor = 2.03563  # assuming Wind Onshore will increase by 203% from 2022 compared to 2030
windoffshore_2030_factor = 3.76979  # assuming Wind Offshore will 376% increase
pv_2030_factor = 3.5593  # assuming PV will increase by 350%


def scale_2030_factors(df, windonshore_factor, windoffshore_factor, pv_factor):
    df_copy = df.copy()
    df_copy[WIND_ONSHORE] *= windonshore_factor
    df_copy[WIND_OFFSHORE] *= windoffshore_factor
    df_copy[PHOTOVOLTAIC] *= pv_factor
    df_copy['Total Production'] = df_copy[columns_to_clean].sum(axis=1)
    return df_copy


# Scale the data by the factors
scaled_production_df = scale_2030_factors(prognoseErzeugung2030df, windonshore_2030_factor, windoffshore_2030_factor,
                                          pv_2030_factor)

# Filter the data for the selected date
scaled_selected_production_df = scaled_production_df[scaled_production_df[DATE] == selected_date]

verbrauch2030df = energyConsumption(consumption_df)
# scaled_consumption_df = scale_2030_factorsConsumption(prognoseVerbrauch2030df, Verbrauch2022_2030_factor)

# Filter the data for the selected date
# scaled_selected_consumption_df = scaled_consumption_df[scaled_consumption_df[DATE] == selected_date]

### subplot only consumption 2030
''''
fig = make_subplots()

fig.add_trace(
    go.Scatter(
        x=selected_consumption_df[STARTTIME].dt.strftime('%H:%M'), 
        y=selected_consumption_df[CONSUMPTION],
        mode='lines',
        name='Total Consumption',
        fill='tozeroy'
    )
)
fig.update_layout(
    title=f'Energy Production and Consumption on {selected_date}',
    xaxis=dict(title='Time (hours)'),
    yaxis=dict(title='Energy (MWh)'),
    showlegend=True
)
fig.show()
'''

'''
# Plot the data with Matplotlib
# Plotting
plt.figure(figsize=(12, 6))
plt.plot(scaled_selected_production_df[STARTTIME], scaled_selected_production_df['Total Production'], label='Total Renewable Production')
plt.plot(selected_consumption_df[STARTTIME], selected_consumption_df[CONSUMPTION], label='Total Consumption')

plt.title(f'Renewable Energy Production and Total Consumption on {selected_date_str}')
plt.xlabel('Time (hours)')
plt.ylabel('Energy (MWh)')
plt.legend()
plt.grid(True)

# Format x-axis ticks and labels
unique_hours = sorted(scaled_selected_production_df[STARTTIME].dt.hour.unique())
plt.xticks(scaled_selected_production_df[STARTTIME], selected_production[STARTTIME].dt.strftime('%H:%M'), rotation=45)
plt.gca().set_xticks(scaled_selected_production_df[STARTTIME][::4])
plt.gca().set_xticklabels(scaled_selected_production_df[STARTTIME].dt.strftime('%H')[::4])
plt.show()
'''

## Plotly daily production and consumption 2030

selected_consumption2030df = verbrauch2030df[verbrauch2030df[DATE] == selected_date]
scaled_selected_production_df = scaled_selected_production_df[scaled_selected_production_df[DATE] == selected_date]

fig = make_subplots()

# Add the energy consumption trace
fig.add_trace(
    go.Scatter(
        x=selected_consumption2030df[STARTTIME].dt.strftime('%H:%M'),
        y=selected_consumption2030df['Verbrauch [MWh]'],
        mode='lines',
        name='Total Consumption',
        fill='tozeroy'
    )
)

# Add the renewable energy production trace
fig.add_trace(
    go.Scatter(
        x=scaled_selected_production_df[STARTTIME].dt.strftime('%H:%M'),
        y=scaled_selected_production_df['Total Production'],
        mode='lines',
        name='Total Renewable Production',
        fill='tozeroy'
    )
)

fig.update_layout(
    title=f'Energy Production and Consumption on {selected_date}',
    xaxis=dict(title='Time (hours)'),
    yaxis=dict(title='Energy (MWh)'),
    showlegend=True
)

fig.show()

# code to do 2030 quarter hours
total_scaled_renewable_production = scaled_production_df[columns_to_clean].sum(axis=1)
total_consumption = verbrauch2030df['Verbrauch [MWh]']

# Berechnung der prozentualen Anteile der erneuerbaren Energieerzeugung am Gesamtverbrauch
percent_renewable = total_scaled_renewable_production / total_consumption * 100

counts, intervals = np.histogram(percent_renewable, bins=np.arange(0, 330, 1))  # Use NumPy to calculate the histogram of the percentage distribution

x = intervals[:-1]  # Define the x-axis values as the bin edges
labels = [f'{i}%' for i in range(0, 330, 1)]  # Create labels for x-axis ticks (von 0 bis 111 in Einzelnschritten)

fig = go.Figure(data=[go.Bar(x=x, y=counts)])  # Create a bar chart using Plotly
fig.update_layout(
    xaxis=dict(tickmode='array', tickvals=list(range(0, 330, 5)), ticktext=labels[::5]))  # X-axis label settings

# Title and axis labels settings
fig.update_layout(title='Anzahl der Viertelstunden im Jahren 2030 mit 0-330 % EE-Anteil',
                  xaxis_title='Prozentsatz erneuerbarer Energie',
                  yaxis_title='Anzahl der Viertelstunden')

fig.show()

# how many quarter hours are in scaled_production_df
print("soviele VS sind in scaled_production_df:")
print(len(scaled_selected_production_df))
print("Viertelstunden aus 2030 expected 35040 hier: ")




# Berechnen Sie den prozentualen Anteil der erneuerbaren Energieerzeugung am Verbrauch
prozentualerAnteil = total_scaled_renewable_production / verbrauch2030df['Verbrauch [MWh]'] * 100
print(percent_renewable)

# Initialisieren Sie eine Liste für die Datensätze
data = []

# Iterieren Sie über die Prozentsätze von 0 bis 100
for i in range(301):
    # Zählen Sie die Viertelstunden über oder gleich dem Prozentsatz
    anzahlViertelstundenProzent = len(percent_renewable[percent_renewable >= i])

    # Fügen Sie einen Datensatz zum Speichern in die Liste hinzu
    data.append({'Prozentsatz': i, 'Anzahl_Viertelstunden': anzahlViertelstundenProzent})

# Erstellen Sie ein DataFrame aus der Liste
result_df = pd.DataFrame(data)

# Drucken Sie das erstellte DataFrame
print(result_df)

fig = go.Figure()

# Fügen Sie einen Balken für die Anzahl der Viertelstunden für jeden Prozentsatz hinzu
fig.add_trace(go.Bar(x=result_df['Prozentsatz'], y=result_df['Anzahl_Viertelstunden']))

# Aktualisieren Sie das Layout für Titel und Achsenbeschriftungen
fig.update_layout(
    title='Anzahl der Viertelstunden mit erneuerbarer Energieerzeugung über oder gleich dem Verbrauch',
    xaxis=dict(title='Prozentsatz erneuerbarer Energie'),
    yaxis=dict(title='Anzahl der Viertelstunden')
)

# Zeigen Sie den Plot an
fig.show()
