
"""Praxisproblem 1, Tontechnik 2: einfache Auswertung einer Raumimpulsantwort."""

from pathlib import Path
from math import gcd
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve, resample_poly

# 1. Eigene Gruppe und angenommene Hoerentfernung fuer die STI-Schaetzung
gruppe = 1  # HIER 1 bis 6 eintragen
abstand = 10.0  # Meter; angenommener Abstand Quelle-Hoerer

raeume = {
    1: ("RIR_A.wav", 1560),
    2: ("RIR_B.wav", 8000),
    3: ("RIR_F.wav", 18000),
    4: ("RIR_C.wav", 6000),
    5: ("RIR_E.wav", 1140),
    6: ("RIR_D.wav", 910),
}

# 2. RIR laden (WAV-Dateien vorher aus dem ZIP entpacken)
ordner = Path(__file__).resolve().parent
dateiname, volumen = raeume[gruppe]
treffer = list(ordner.rglob(dateiname))
if not treffer:
    raise FileNotFoundError(f"{dateiname} nicht gefunden. ZIP bitte entpacken.")

h, fs = sf.read(treffer[0])
if h.ndim == 2:
    h = h[:, 0]  # Nur einen Kanal der RIR verwenden

# Vorlauf entfernen: erster deutlicher Ausschlag bei 10 % des Spitzenwerts
start = np.where(np.abs(h) >= 0.1 * np.max(np.abs(h)))[0][0]
h = h[start:]
zeit = np.arange(len(h)) / fs

# 3. Schroeder-Integration: Schallenergie vom Ende her aufsummieren
energie = np.cumsum((h**2)[::-1])[::-1]
pegel = 10 * np.log10(np.maximum(energie / energie[0], 1e-12))

def nachhallzeit(oben, unten):
    bereich = (pegel <= oben) & (pegel >= unten)
    steigung, _ = np.polyfit(zeit[bereich], pegel[bereich], 1)
    return -60 / steigung  # Auf einen Abfall um 60 dB hochrechnen

t20 = nachhallzeit(-5, -25)
t30 = nachhallzeit(-5, -35)
t60 = t30  # T30 ist hier unsere T60-Schaetzung

# 4. C50 und C80: Energie vor und nach der jeweiligen Zeitgrenze

def klarheit(ms):
    grenze = round(ms / 1000 * fs)
    frueh = np.sum(h[:grenze] ** 2)
    spaet = np.sum(h[grenze:] ** 2)
    return 10 * np.log10(frueh / spaet)

c50 = klarheit(50)
c80 = klarheit(80)

# 5. STI nach der in der Aufgabenstellung genannten ALcons-Gleichung
# Hallradius angenaehert fuer eine ungerichtete Schallquelle und diffuses Hallfeld.
hallradius = 0.057 * np.sqrt(volumen / t60)
alcons = 0.625 * (abstand / hallradius)**2 * t60  # Prozentwert
sti_roh = 1 - 0.45 * np.log10(alcons)  # Farrell-Becker
sti = np.clip(sti_roh, 0, 1)

print(f"Gruppe {gruppe} | Raumvolumen: {volumen} m³")
print(f"T20: {t20:.2f} s | T30 / T60-Schaetzung: {t30:.2f} s")
print(f"C50: {c50:.2f} dB | C80: {c80:.2f} dB")
print(f"Hallradius: {hallradius:.2f} m")
print(f"Bei {abstand:g} m: ALcons = {alcons:.2f} %, STI ≈ {sti:.2f}")
if sti != sti_roh:
    print("Hinweis: STI-Rohwert ausserhalb 0 bis 1; Naeherung hier unzuverlaessig.")

# 6. Zwei einfache Diagramme speichern und anzeigen
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(zeit, h)
plt.xlabel("Zeit ab Impulsbeginn (s)")
plt.ylabel("Amplitude")
plt.title("Raumimpulsantwort")
plt.subplot(1, 2, 2)
plt.plot(zeit, pegel)
plt.ylim(-70, 0)
plt.xlabel("Zeit ab Impulsbeginn (s)")
plt.ylabel("Energiepegel (dB)")
plt.title("Schroeder-Abklingkurve")
plt.tight_layout()
plt.savefig(ordner / "auswertung.png", dpi=150)
plt.show()

# 7. Auralisation: trockene Dateien sprache.wav und musik.wav benoetigt
# "nah" = mehr Direktschall, "fern" = weniger Direktschall.
# Das simuliert nur einen Nahe-/Ferneindruck, keine exakte Entfernung in Metern.
for art in ("sprache", "musik"):
    datei = ordner / f"{art}.wav"
    if not datei.exists():
        print(f"{datei.name} fehlt: Auralisation dafuer uebersprungen.")
        continue

    trocken, audio_fs = sf.read(datei)
    if trocken.ndim == 2:
        trocken = trocken.mean(axis=1)  # Einfache Mono-Auswertung

    # Abtastraten muessen bei der Faltung gleich sein.
    faktor = gcd(fs, audio_fs)
    raum = resample_poly(h, audio_fs // faktor, fs // faktor)
    direktschall_ende = max(1, round(0.005 * audio_fs))

    for name, verstaerkung in (("nah", 2.0), ("fern", 0.5)):
        impuls = raum.copy()
        impuls[:direktschall_ende] *= verstaerkung
        ergebnis = fftconvolve(trocken, impuls)
        spitze = np.max(np.abs(ergebnis))
        if spitze > 0:
            ergebnis = 0.95 * ergebnis / spitze  # Uebersteuerung vermeiden
        sf.write(ordner / f"{art}_{name}.wav", ergebnis, audio_fs)
        print(f"Erzeugt: {art}_{name}.wav")
