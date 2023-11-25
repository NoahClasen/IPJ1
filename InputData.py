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

counts, intervals = np.histogram(percent_renewable, bins=np.arange(0, 111,
                                                                   1))  # Use NumPy to calculate the histogram of the percentage distribution

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

# code to make 2030 prediction
# 2030 prediction


prognoseVerbrauch2030df = energyConsumption(consumption_df)

# Annahme: 'Anfang' ist eine Spalte im DataFrame prognoseVerbrauch2030df
prognoseVerbrauch2030df['Anfang'] = pd.to_datetime(prognoseVerbrauch2030df['Anfang'], format='%H:%M')

# Benutzereingabe für das Datum
selected_date_str = input("Bitte geben Sie das Datum im Format TT.MM.JJJJ ein: ")
selected_date = pd.to_datetime(selected_date_str, format='%d.%m.%Y')

# Plotly-Figur als erstellen Scatter-Diagramm erstellen
fig = go.Figure(
    go.Scatter(
        x=prognoseVerbrauch2030df['Anfang'],
        y=prognoseVerbrauch2030df['Gesamt (Netzlast) [kWh] Originalauflösungen'],
        mode='lines',
        name=f'Total Energy Consumption on {selected_date_str}',  # Änderung hier, um den Datumsstring einzufügen
        fill='tozeroy'
    )
)

# Layout aktualisieren
fig.update_layout(
    title=f'Energy Consumption 2030 on {selected_date_str}',
    xaxis=dict(title='Time (hours)'),
    yaxis=dict(title='Energy (MWh)'),
    showlegend=True
)

# Diagramm anzeigen
fig.show()
