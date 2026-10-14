
import pandas as pd
import matplotlib.pyplot as plt

# Leser værdata fra CSV-filen
fil = r"C:\Users\frog_\OneDrive - Universitetet i Stavanger\Semester 1\Dat-120\Øving\sinnes_2014_2025_med_makstemperatur.csv"


data = pd.read_csv(
    fil,
    sep=";",
    decimal=",",
    na_values=["-"],
    encoding="utf-8-sig"
)

# Gjør datoene om til datoformat
data["Tid(norsk normaltid)"] = pd.to_datetime(
    data["Tid(norsk normaltid)"],
    format="%d.%m.%Y",
    errors="coerce"
)

# Fjerner rader uten gyldig dato og sorterer
data = data.dropna(subset=["Tid(norsk normaltid)"])
data = data.sort_values("Tid(norsk normaltid)").reset_index(drop=True)

# Lager en kolonne med årstall
data["År"] = data["Tid(norsk normaltid)"].dt.year

# Gjør værkolonnene numeriske
værkolonner = [
    "Maksimumstemperatur (døgn)",
    "Middeltemperatur (døgn)",
    "Nedbør (døgn)",
    "Høyeste middelvind (døgn)",
    "Snødybde"
]

for kolonne in værkolonner:
    data[kolonne] = pd.to_numeric(data[kolonne], errors="coerce")


# Legger til årstall
data["Tid(norsk normaltid)"] = pd.to_datetime(
    data["Tid(norsk normaltid)"],
    format="%d.%m.%Y",
    errors="coerce"
)
# Lager årskolonnen
data["År"] = data["Tid(norsk normaltid)"].dt.year
# Lar brukeren velge år
tilgjengelige_år = sorted(data["År"].unique())

while True:
    try:
        valgt_år = int(input("Skriv inn et årstall (2014–2025): "))
        if valgt_år in tilgjengelige_år:
            break
        print("Velg et år som finnes i datasettet.")
    except ValueError:
        print("Skriv inn et gyldig årstall.")

# Henter værdata for det valgte året
data_år = data[data["År"] == valgt_år].copy()

# e) Teller skidager fra november året før til mai i valgt år
start_skisesong = pd.Timestamp(valgt_år - 1, 11, 1)
slutt_skisesong = pd.Timestamp(valgt_år, 5, 31)

skisesong = data[

    (data["Tid(norsk normaltid)"] >= start_skisesong) &
    (data["Tid(norsk normaltid)"] <= slutt_skisesong)
]

skidager = (skisesong["Snødybde"] >= 20).sum()

print(f"\nSkidager i skisesongen {valgt_år}: {skidager}")

if start_skisesong < data["Tid(norsk normaltid)"].min():
    print("Merk: Deler av skisesongen mangler i datasettet.")

# f) Beregner total plantevekst
temperatur = data_år["Middeltemperatur (døgn)"]
plantevekst = (temperatur - 5).clip(lower=0)
total_vekst = plantevekst.sum()
print("Antall dager med registrert middeltemperatur:",
      temperatur.notna().sum())
print("Antall manglende middeltemperaturer:",
      temperatur.isna().sum())

print(f"Total plantevekst i {valgt_år}: {total_vekst:.1f}")
print("Første dato i valgt år:",
      data_år["Tid(norsk normaltid)"].min())
print("Siste dato i valgt år:",
      data_år["Tid(norsk normaltid)"].max())
print("Antall rader i valgt år:", len(data_år))

# g) Finner lengste sammenhengende periode uten nedbør
lengste_periode = 0
periode = 0
start_periode = None
beste_start = None
beste_slutt = None
forrige_dato = None

for _, rad in data_år.iterrows():
    dato = rad["Tid(norsk normaltid)"]
    nedbør = rad["Nedbør (døgn)"]

    # Manglende verdier skal ikke regnes som null nedbør
    if pd.isna(nedbør):
        periode = 0
        start_periode = None
        forrige_dato = dato
        continue

    # Perioden må bestå av sammenhengende kalenderdager
    if forrige_dato is not None and (dato - forrige_dato).days != 1:
        periode = 0
        start_periode = None

    if nedbør == 0:
        if periode == 0:
            start_periode = dato

        periode += 1

        if periode > lengste_periode:
            lengste_periode = periode
            beste_start = start_periode
            beste_slutt = dato
    else:
        periode = 0
        start_periode = None

    forrige_dato = dato

print(f"\nLengste periode uten nedbør i {valgt_år}: {lengste_periode} dager")

if beste_start is not None:
    print(f"Startdato: {beste_start:%d.%m.%Y}")
    print(f"Sluttdato: {beste_slutt:%d.%m.%Y}")
else:
    print("Fant ingen sammenhengende dager uten nedbør.")

# h) Teller sommerdager, høysommerdager og tropedager
maks_temp = data_år["Maksimumstemperatur (døgn)"]

sommerdager = (maks_temp > 20).sum()
høysommerdager = (maks_temp > 25).sum()
tropedager = (maks_temp > 30).sum()

print(f"\nSommerdager over 20 °C: {sommerdager}")
print(f"Høysommerdager over 25 °C: {høysommerdager}")
print(f"Tropedager over 30 °C: {tropedager}")


# d) Plotter de fire værmålingene for valgt år
fig, akser = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

målinger = [
    ("Snødybde", "Snødybde (cm)"),
    ("Nedbør (døgn)", "Nedbør (mm)"),
    ("Middeltemperatur (døgn)", "Temperatur (°C)"),
    ("Høyeste middelvind (døgn)", "Vind (m/s)")
]

for akse, (kolonne, etikett) in zip(akser, målinger):
    akse.plot(
        data_år["Tid(norsk normaltid)"],
        data_år[kolonne],
        linestyle="-",
        marker=None
        
        
    )
    akse.set_ylabel(etikett)
    akse.grid(True)

fig.suptitle(f"Værdata for Sinnes i {valgt_år}")
akser[3].set_xlabel("Dato")

plt.tight_layout()
plt.show()
