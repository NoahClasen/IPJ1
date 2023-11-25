# -----------------------------------------
# name: energyConsumption
# date: 17.11.2023
# laste change: 17.11.2023
# author: Noah Clasen
# use: calculate forecast till 2023
# test Bjarne
# -----------------------------------------

# import
import pandas as pd


# Funktion
def energyConsumption(consumption_df):
    wärmepumpeHochrechnung2030 = wärmepumpe()
    eMobilitätHochrechnung2030 = eMobilität()

    print('\n', 'wärmepumpeHochrechnung2030', f"{wärmepumpeHochrechnung2030:,.0f}".replace(",", "."))
    print('\n', 'eMobilitätHochrechnung2030', f"{eMobilitätHochrechnung2030:,.0f}".replace(",", "."))

    verbrauch2022df = consumption_df[consumption_df['Datum'].dt.year == 2022]
    prognose2030df = verbrauch2022df.copy()
    faktor = faktorRechnung(verbrauch2022df, wärmepumpeHochrechnung2030, eMobilitätHochrechnung2030)
    print(faktor)
    # Change the year in 'Datum' column to 2030
    prognose2030df['Datum'] = prognose2030df['Datum'].map(lambda x: x.replace(year=2030))

    prognose2030df['Verbrauch [MWh]'] = prognose2030df['Gesamt (Netzlast) [MWh] Originalauflösungen'] * faktor

    combined_df = pd.concat([verbrauch2022df[['Anfang', 'Gesamt (Netzlast) [MWh] Originalauflösungen']], prognose2030df[['Verbrauch [MWh]']]], axis=1)
    print(combined_df[['Gesamt (Netzlast) [MWh] Originalauflösungen', 'Verbrauch [MWh]']])

    return prognose2030df


def wärmepumpe():
    wärmepumpeAnzahl2030 = 500000 * (2030 - 2023)  # 500k pro Jahr bis 2023

    heizstunden = 2000
    nennleistung = 15  # 15kW
    luftWasserVerhältnis = 206 / 236
    erdwärmeVerhältnis = 30 / 236
    luftWasserJAZ = 3.1
    erdwärmeJAZ = 4.1

    # Berechnung der einzelnen Pumpe
    luftWasserVerbrauch = wärmepumpeVerbrauchImJahr(heizstunden, nennleistung, luftWasserJAZ)  # in kW/h
    erdwärmeVerbrauch = wärmepumpeVerbrauchImJahr(heizstunden, nennleistung, erdwärmeJAZ)  # in kW/h

    luftWasserVerhältnisAnzahl = verhältnisAnzahl(wärmepumpeAnzahl2030, luftWasserVerhältnis)
    erdwärmeVerhältnisAnzahl = verhältnisAnzahl(wärmepumpeAnzahl2030, erdwärmeVerhältnis)

    return luftWasserVerbrauch * luftWasserVerhältnisAnzahl + erdwärmeVerbrauch * erdwärmeVerhältnisAnzahl  # kWh


# berechnung des Verbrauchs einer Wärmepumpe im Jahr
def wärmepumpeVerbrauchImJahr(heizstunden, nennleistung, jaz):
    # (Heizstunden * Nennleistung) / JAZ = Stromverbrauch pro Jahr
    return (heizstunden * nennleistung) / jaz


def verhältnisAnzahl(wärmepumpeAnzahl2030, verhältnis):
    return wärmepumpeAnzahl2030 * verhältnis


def eMobilität():
    eMobilität2030 = 15000000  # 15mio bis 20230
    eMobilitätBisher = 1307901  # 1.3 mio
    verbrauchPro100km = 21  # 21kWh
    kilometerProJahr = 15000  # 15.000km

    eMobilitätVerbrauch = (verbrauchPro100km / 100) * kilometerProJahr  # kWh

    return (eMobilität2030 - eMobilitätBisher) * eMobilitätVerbrauch


def faktorRechnung(verbrauch2022df, wärmepumpeHochrechnung2030, eMobilitätHochrechnung2030):
    gesamtVerbrauch2022 = otherFactors() + verbrauch2022df[
        'Gesamt (Netzlast) [MWh] Originalauflösungen'].sum() * 1000  # mal1000 weil MWh -> kWh
    print('\n', 'gesamtVerbrauch2022', f"{gesamtVerbrauch2022:,.0f}".replace(",", "."))
    return (gesamtVerbrauch2022 + wärmepumpeHochrechnung2030 + eMobilitätHochrechnung2030) / gesamtVerbrauch2022


def prognoseRechnung(verbrauch2022df, faktor):
    verbrauch2030df = verbrauch2022df['Verbrauch [kWh]'] * faktor
    return verbrauch2030df


def otherFactors():
    # positive Faktoren
    railway = 5000  # kWh
    batterieProdAndServerRooms = 13000  # kwh
    powerNetLoss = 1000

    # negative Faktoren
    efficiency = 51000
    other = 6000

    return railway + batterieProdAndServerRooms + powerNetLoss - efficiency - other
