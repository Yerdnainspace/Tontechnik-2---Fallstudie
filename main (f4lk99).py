# Tontechnik 2 - Praxisproblem 1 - Gruppe 4
# Raumimpulsantwort RIR_C, Raumvolumen 6000 m^3

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.signal import fftconvolve, resample_poly
from math import gcd
from pathlib import Path


# 1. Raumimpulsantwort laden

ordner = Path(__file__).resolve().parent
datei = ordner / "Raumimpulsantworten" / "RIR_C.wav"

volumen = 6000
h, fs = sf.read(datei)

if h.ndim == 2:
    h = h[:, 0]  # Bei Stereo nur ersten Kanal verwenden

h = h - np.mean(h)

# Beginn der Impulsantwort bestimmen
start = np.where(np.abs(h) >= 0.05 * np.max(np.abs(h)))[0][0]
h = h[start:]

zeit = np.arange(len(h)) / fs

print("Gruppe 4 - RIR_C.wav")
print("Raumvolumen:", volumen, "m^3")
print("Abtastrate:", fs, "Hz")
print("Signallaenge:", round(len(h) / fs, 2), "s")


# 2. Nachhallzeit mit Schroeder-Integration

# Wir betrachten die ersten 1,5 Sekunden nach dem Impuls.
auswertezeit = 1.5
anzahl = int(auswertezeit * fs)

h_kurz = h[:anzahl]
t_kurz = np.arange(len(h_kurz)) / fs

# Rauschleistung am Ende der Aufnahme abschaetzen
rauschen = np.mean(h[-int(0.5 * fs):] ** 2)

# Energie von hinten aufsummieren
energie = np.cumsum((h_kurz ** 2)[::-1])[::-1]

# Geschaetzten Rauschanteil abziehen
energie = energie - rauschen * np.arange(len(h_kurz), 0, -1)
energie = np.maximum(energie, 1e-15)

# Energie in Dezibel umrechnen
pegel = 10 * np.log10(energie / energie[0])


def nachhallzeit(oben, unten):
    bereich = (pegel <= oben) & (pegel >= unten)

    steigung, achsenabschnitt = np.polyfit(
        t_kurz[bereich], pegel[bereich], 1
    )

    t60 = -60 / steigung

    return t60, steigung, achsenabschnitt


t20, _, _ = nachhallzeit(-5, -25)
t30, m30, b30 = nachhallzeit(-5, -35)

# T30 als Schaetzung fuer T60
t60 = t30


# 3. C50 und C80 berechnen

def klarheit(grenze_ms):
    grenze = int(grenze_ms / 1000 * fs)

    energie_frueh = np.sum(h[:grenze] ** 2)
    energie_spaet = np.sum(h[grenze:] ** 2)

    c = 10 * np.log10(energie_frueh / energie_spaet)

    return c


c50 = klarheit(50)
c80 = klarheit(80)


# 4. Sprachverstaendlichkeit (STI)

# Hallradius mit Raumvolumen und Nachhallzeit abschaetzen
hallradius = 0.057 * np.sqrt(volumen / t60)

print("\n--- Ergebnisse ---")
print(f"T20: {t20:.2f} s")
print(f"T30 / T60: {t30:.2f} s")
print(f"C50: {c50:.2f} dB")
print(f"C80: {c80:.2f} dB")
print(f"Hallradius: {hallradius:.2f} m")

# STI fuer zwei angenommene Entfernungen
for abstand in [5, 12]:

    alcons = 0.625 * (abstand / hallradius) ** 2 * t60

    sti = 1 - 0.45 * np.log10(alcons)

    print(f"\nAbstand: {abstand} m")
    print(f"ALcons: {alcons:.2f} %")
    print(f"STI: {sti:.2f} (Naeherung)")


# 5. Diagramme darstellen

plt.figure(figsize=(11, 4))

# Raumimpulsantwort
plt.subplot(1, 2, 1)
plt.plot(zeit, h)
plt.title("Raumimpulsantwort RIR_C")
plt.xlabel("Zeit (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# Energieabklingkurve
plt.subplot(1, 2, 2)
plt.plot(t_kurz, pegel, label="Schroeder-Kurve")
plt.plot(t_kurz, m30 * t_kurz + b30, "--", label="T30-Gerade")

plt.title("Energieabklingkurve")
plt.xlabel("Zeit (s)")
plt.ylabel("Pegel (dB)")
plt.ylim(-60, 0)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig(ordner / "gruppe4_diagramme.png")
plt.show()


# 6. Auralisation durch Faltung

# Trockene Sprache und Musik werden im Hauptordner erwartet.
# Falls die Dateien fehlen, wird dieser Teil uebersprungen.

for name in ["sprache", "musik"]:

    audio_datei = ordner / (name + ".wav")

    if not audio_datei.exists():
        print(f"\n{name}.wav nicht gefunden.")
        continue

    trocken, audio_fs = sf.read(audio_datei)

    if trocken.ndim == 2:
        trocken = np.mean(trocken, axis=1)

    # Raumimpulsantwort auf Abtastrate der Aufnahme bringen
    faktor = gcd(fs, audio_fs)
    h_audio = resample_poly(
        h, audio_fs // faktor, fs // faktor
    )

    # Zwei verschiedene Naehe-/Ferneindruecke
    for variante, verstaerkung in [("nah", 1.8), ("fern", 0.5)]:

        h_var = h_audio.copy()

        # Fruehen Schallanteil veraendern
        direkt = int(0.005 * audio_fs)
        h_var[:direkt] *= verstaerkung

        # Faltung
        ergebnis = fftconvolve(trocken, h_var)

        # Pegel normalisieren
        maximal = np.max(np.abs(ergebnis))

        if maximal > 0:
            ergebnis = 0.95 * ergebnis / maximal

        # Neue WAV-Datei speichern
        ausgabe = ordner / (name + "_" + variante + ".wav")

        sf.write(ausgabe, ergebnis, audio_fs)

        print("Gespeichert:", ausgabe.name)
