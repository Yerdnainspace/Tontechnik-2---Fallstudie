"""Praxisproblem 1, Gruppe 4 – Analyse eines Raumes (6000m³) anhand einer Impulsantwort

Gruppenmitglieder: Jonah Fetahovic, Maximilian Falk Pitulle, Mario Contrino, Andrey Schaefer

Die vier WAVs in 'Ergänzendes Material' sind zusätzliche Impulsantworten
Abhängigkeiten: numpy, matplotlib, scipy
Erzeugte Signale werden nach dem Speichern automatisch abgespielt.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import fftconvolve, resample


# 1. Einstellungen und Dateipfade

projekt_ordner = Path(__file__).resolve().parent
rir_datei = projekt_ordner / "RIR_C.wav"
audio_ordner = projekt_ordner / "Ergänzendes Material"

raumvolumen = 6000                      # m³, gilt für RIR_C
hoerabstaende = [5, 10,15]                 # m, nur für die STI-Näherung
analyse_dauer = 1.5                       # s, Ausschnitt für die Nachhallauswertung
audio_abspielen = True


# Eine Hilfsfunktion für WAV-Dateien
def wav_lesen(datei):
    # Ganzzahlen vor dem Rechnen in Gleitkommazahlen umwandeln.
    abtastrate, signal = wavfile.read(datei)
    datentyp = signal.dtype
    signal = signal.astype(float)

    if datentyp == np.uint8:
        signal = (signal - 128) / 128
    elif np.issubdtype(datentyp, np.signedinteger):
        signal = signal / float(-np.iinfo(datentyp).min)

    if signal.size == 0 or not np.all(np.isfinite(signal)):
        raise ValueError(f"Leere oder ungültige WAV-Datei: {datei.name}")
    return abtastrate, signal


# 2. Raumimpulsantwort laden und ihren Beginn bestimmen

abtastrate, impulsantwort = wav_lesen(rir_datei)

if impulsantwort.ndim == 2:
    impulsantwort = impulsantwort[:, 0]  # Bei der RIR nur Kanal 1 verwenden.

impulsantwort = impulsantwort - np.mean(impulsantwort)
spitzenwert = np.max(np.abs(impulsantwort))
if spitzenwert == 0:
    raise ValueError("Die Raumimpulsantwort enthält kein Signal.")

# Erste Überschreitung von 5 % des Spitzenwerts als Ankunft schätzen.
startschwelle = 0.05 * spitzenwert
startposition = np.flatnonzero(np.abs(impulsantwort) >= startschwelle)[0]
impulsantwort = impulsantwort[startposition:]
zeit_rir = np.arange(len(impulsantwort)) / abtastrate


# 3. Schroeder-Kurve: verbleibende Energie rückwärts aufsummieren

analyse_signal = impulsantwort[:round(analyse_dauer * abtastrate)]
zeit_analyse = np.arange(len(analyse_signal)) / abtastrate

# Annahme: Die letzten 0,5 s der vollständigen RIR enthalten überwiegend Rauschen.
anzahl_rauschwerte = max(1, round(0.5 * abtastrate))
rauschleistung = np.mean(impulsantwort[-anzahl_rauschwerte:] ** 2)

energie = np.cumsum((analyse_signal ** 2)[::-1])[::-1]
verbleibende_werte = np.arange(len(analyse_signal), 0, -1)
energie = energie - rauschleistung * verbleibende_werte

if energie[0] <= 0:
    raise ValueError("Die Rauschkorrektur lässt keine positive Gesamtenergie übrig.")

# Anfang auf 0 dB beziehen; den Logarithmus von null/negativen Werten vermeiden.
energie_db = 10 * np.log10(np.maximum(energie, 1e-15) / energie[0])


# 4. T10, T20 und T30: Geraden an verschiedene Abklingbereiche anpassen
# Jede Zeit wird auf einen Energieabfall von 60 dB extrapoliert.

bereich_t10 = (energie_db <= -5) & (energie_db >= -15)
bereich_t20 = (energie_db <= -5) & (energie_db >= -25)
bereich_t30 = (energie_db <= -5) & (energie_db >= -35)

for bereich in [bereich_t10, bereich_t20, bereich_t30]:
    if np.count_nonzero(bereich) < 2:
        raise ValueError("Zu wenige Werte für die Nachhallauswertung.")

steigung_t10, offset_t10 = np.polyfit(zeit_analyse[bereich_t10], energie_db[bereich_t10], 1)
steigung_t20, offset_t20 = np.polyfit(zeit_analyse[bereich_t20], energie_db[bereich_t20], 1)
steigung_t30, offset_t30 = np.polyfit(zeit_analyse[bereich_t30], energie_db[bereich_t30], 1)

if steigung_t10 >= 0 or steigung_t20 >= 0 or steigung_t30 >= 0:
    raise ValueError("Die Energieabklingkurve fällt nicht in allen Bereichen ab.")

t10 = -60 / steigung_t10
t20 = -60 / steigung_t20
t30 = -60 / steigung_t30

# Wie gut folgt die Abklingkurve im jeweiligen Bereich einer Geraden?
r_t10 = np.corrcoef(zeit_analyse[bereich_t10], energie_db[bereich_t10])[0, 1]
r_t20 = np.corrcoef(zeit_analyse[bereich_t20], energie_db[bereich_t20])[0, 1]
r_t30 = np.corrcoef(zeit_analyse[bereich_t30], energie_db[bereich_t30])[0, 1]

# Hallradius bestimmen mit Raumvolumen und optimaler Nachhallzeit
hallradius = 0.057 * np.sqrt(raumvolumen / t20)

# 5. C50 und C80: Energie vor und nach 50 bzw. 80 ms vergleichen
# Wie in der hochgeladenen Fassung: vollständige RIR, ohne Rauschkorrektur.

grenze_50ms = round(0.050 * abtastrate)
grenze_80ms = round(0.080 * abtastrate)

energie_bis_50ms = np.sum(impulsantwort[:grenze_50ms] ** 2)
energie_nach_50ms = np.sum(impulsantwort[grenze_50ms:] ** 2)
energie_bis_80ms = np.sum(impulsantwort[:grenze_80ms] ** 2)
energie_nach_80ms = np.sum(impulsantwort[grenze_80ms:] ** 2)

if min(energie_bis_50ms, energie_nach_50ms, energie_bis_80ms, energie_nach_80ms) <= 0:
    raise ValueError("Für C50/C80 müssen frühe und späte Energie positiv sein.")

c50 = 10 * np.log10(energie_bis_50ms / energie_nach_50ms)
c80 = 10 * np.log10(energie_bis_80ms / energie_nach_80ms)

# 6. Ergebnisse und STI-Näherung aus den Formeln des Aufgabenblatts

print(f"Gruppe 4 – RIR_C – Raumvolumen: {raumvolumen} m³")
print(f"T10: {t10:.4f} s | r = {r_t10:.4f}")
print(f"T20: {t20:.4f} s | r = {r_t20:.4f}")
print(f"T30: {t30:.4f} s | r = {r_t30:.4f}")
print(f"C50: {c50:.2f} dB")
print(f"C80: {c80:.2f} dB")
print(f"Hallradius: {hallradius:.4f} m")

for abstand in hoerabstaende:
    artikulationsverlust = 0.652 * (abstand / hallradius) ** 2 * t20
    sti = 1 - 0.45 * np.log10(artikulationsverlust)
    print(f"STI-Näherung bei {abstand} m: {sti:.2f}")

# Die STI-Formel ist eine Modellschätzung, keine vollständige STI-Messung.
# Rohwerte außerhalb 0...1 sind keine gültigen STI-Werte.


# 7. Raumimpulsantwort und Abklingkurve darstellen

abbildung, (diagramm_rir, diagramm_nachhall) = plt.subplots(1, 2, figsize=(12, 5))

diagramm_rir.plot(zeit_rir, impulsantwort)
diagramm_rir.set_title("Raumimpulsantwort RIR_C")
diagramm_rir.set_xlabel("Zeit / s")
diagramm_rir.set_ylabel("Amplitude")
diagramm_rir.grid(True)

diagramm_nachhall.plot(zeit_analyse, energie_db, color="black", label="Schroeder-Kurve")
diagramm_nachhall.plot(zeit_analyse[bereich_t10], steigung_t10 * zeit_analyse[bereich_t10] + offset_t10,
                       label=f"T10: {t10:.2f} s")
diagramm_nachhall.plot(zeit_analyse[bereich_t20], steigung_t20 * zeit_analyse[bereich_t20] + offset_t20,
                       label=f"T20: {t20:.2f} s")
diagramm_nachhall.plot(zeit_analyse[bereich_t30], steigung_t30 * zeit_analyse[bereich_t30] + offset_t30,
                       label=f"T30: {t30:.2f} s")
diagramm_nachhall.set_title("Schroeder-Plot")
diagramm_nachhall.set_xlabel("Zeit / s")
diagramm_nachhall.set_ylabel("Energiepegel / dB")
diagramm_nachhall.set_ylim(-120, 0)
diagramm_nachhall.legend()
diagramm_nachhall.grid(True)

abbildung.tight_layout()
abbildung.savefig(projekt_ordner / "pp1_diagramme.png", dpi=150)
plt.show()  # Diagrammfenster schließen, um mit den Hörbeispielen fortzufahren.


# 8. Optional: trockene Sprache und Musik mit dem Raumhall versehen
# Beide WAV-Dateien werden im Unterordner "Ergänzendes Material" gesucht.
# Die dort vorhandenen anderen RIRs ersetzen keine Sprach-/Musikaufnahme.

for dateiname in ["RIR_Dustbin1C.wav"]:
    audio_datei = audio_ordner / dateiname
    if not audio_datei.exists():
        print(f"{dateiname} fehlt – zugehörige Hörbeispiele übersprungen.")
        continue

    audio_abtastrate, trockenes_signal = wav_lesen(audio_datei)
    if trockenes_signal.ndim == 2:
        trockenes_signal = np.mean(trockenes_signal, axis=1)

    if not np.any(trockenes_signal):
        raise ValueError(f"{dateiname} enthält kein Signal.")

    # Die RIR bei Bedarf mit dem Fourier-Verfahren von SciPy umrechnen.
    # Das Verfahren nimmt eine periodische Fortsetzung an; Randartefakte sind möglich.
    raumfilter = impulsantwort.copy()
    if audio_abtastrate != abtastrate:
        neue_laenge = max(1, round(len(raumfilter) * audio_abtastrate / abtastrate))
        raumfilter = resample(raumfilter, neue_laenge)

    hoerbeispiele = []

    # Nur den Anfang verändern: vereinfachter Nah-/Ferneindruck, keine Meter-Simulation.
    for variante, anfangsfaktor in [("nah", 1.8), ("fern", 0.5)]:
        veraenderter_filter = raumfilter.copy()
        erste_5ms = round(0.005 * audio_abtastrate)
        veraenderter_filter[:erste_5ms] *= anfangsfaktor

        # SciPy übernimmt FFT, Spektrenmultiplikation und Rücktransformation.
        # "full" erhält das vollständige Ergebnis einschließlich Nachhallende.
        gefaltetes_signal = fftconvolve(trockenes_signal, veraenderter_filter, mode="full")
        hoerbeispiele.append((variante, gefaltetes_signal))

    # Gemeinsame Skalierung pro Aufnahme erhält Pegelunterschiede zwischen nah/fern.
    gemeinsamer_spitzenwert = max(np.max(np.abs(signal)) for variante, signal in hoerbeispiele)
    if gemeinsamer_spitzenwert == 0:
        raise ValueError("Die Faltung liefert kein Signal.")
    speicherfaktor = 0.95 / gemeinsamer_spitzenwert

    for variante, signal in hoerbeispiele:
        ausgabesignal = signal * speicherfaktor
        ausgabedatei = projekt_ordner / f"{audio_datei.stem}_{variante}.wav"
        pcm_signal = np.rint(ausgabesignal * 32767).astype(np.int16)
        wavfile.write(ausgabedatei, audio_abtastrate, pcm_signal)
        print(f"Gespeichert: {ausgabedatei.name}")

        if audio_abspielen:
            import sounddevice as sd
            sd.play(ausgabesignal, audio_abtastrate)
            sd.wait()
