"""Praxisproblem 1, Gruppe 4 – Kurzfassung auf Basis von main (f4lk99).py.

Grundlagen: README.md, RIR_C.wav und gruppe4_diagramme.png im Projekt.
Die vier WAVs in 'Ergänzendes Material' sind zusätzliche Impulsantworten;
das Raumvolumen von 6000 m³ gilt hier nur für RIR_C.
Abhängigkeiten: numpy, matplotlib, scipy (nur scipy.io.wavfile), sounddevice.
Optional sprache.wav und musik.wav neben dieses Skript legen.
Erzeugte Signale werden nach dem Speichern automatisch abgespielt.
Die Nah-/Fernvarianten und der STI sind Näherungen wie im Ausgangscode.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.io import wavfile

ORDNER = Path(__file__).resolve().parent


def lesen(pfad, erster_kanal=False):
    """PCM/Float-WAV als Float-Monosignal lesen; RIR nutzt Kanal 1."""
    fs, x = wavfile.read(pfad)
    typ = x.dtype
    x = x.astype(np.float64)
    if typ == np.uint8:
        x = (x - 128) / 128
    elif np.issubdtype(typ, np.signedinteger):
        x /= float(-np.iinfo(typ).min)
    if x.ndim == 2:
        x = x[:, 0] if erster_kanal else x.mean(axis=1)
    if not x.size or not np.all(np.isfinite(x)):
        raise ValueError(f"Leere oder ungültige Audiodaten: {pfad}")
    return fs, x


def speichern(pfad, fs, x):
    """Auf 95 % Spitzenpegel normieren und als 16-Bit-PCM speichern."""
    peak = np.max(np.abs(x))
    x = x * (0.95 / peak) if peak else x
    wavfile.write(pfad, fs, np.rint(x * 32767).astype(np.int16))
    print(f"Gespeichert: {pfad.name}")
    sd.play(x, fs)
    sd.wait()  # Jede Variante vollständig abspielen, bevor die nächste startet.


def abtastrate(x, alt, neu):
    """Fourier-Resampling mit NumPy; hohe Frequenzen beim Kürzen entfernen.

    Wie bei Fourier-Resampling üblich wird das Signal periodisch fortgesetzt.
    Das unterscheidet sich vom Polyphasenfilter im Ausgangscode.
    """
    if alt == neu:
        return x.copy()
    n = max(1, round(len(x) * neu / alt))
    gemeinsam = min(len(x), n)
    spektrum = np.zeros(n // 2 + 1, dtype=complex)
    spektrum[:gemeinsam // 2 + 1] = np.fft.rfft(x)[:gemeinsam // 2 + 1]
    if gemeinsam % 2 == 0:
        spektrum[gemeinsam // 2] *= 2 if n < len(x) else 0.5
    return np.fft.irfft(spektrum, n=n) * n / len(x)


def main():
    fs, h = lesen(ORDNER / "RIR_C.wav", erster_kanal=True)
    h -= h.mean()
    if not np.any(h):
        raise ValueError("Die Impulsantwort enthält kein auswertbares Signal.")
    h = h[np.flatnonzero(np.abs(h) >= 0.05 * np.max(np.abs(h)))[0]:]
    zeit = np.arange(len(h)) / fs

    # Schroeder-Integration mit Rauschkorrektur, wie im Original über 1,5 s.
    kurz = h[:int(1.5 * fs)]
    t = np.arange(len(kurz)) / fs
    rauschen = np.mean(h[-max(1, int(0.5 * fs)):] ** 2)
    energie = np.cumsum(kurz[::-1] ** 2)[::-1]
    energie -= rauschen * np.arange(len(kurz), 0, -1)
    if energie[0] <= 0:
        raise ValueError("Keine nutzbare Abklingenergie nach Rauschkorrektur.")
    pegel = 10 * np.log10(np.maximum(energie, 1e-15) / energie[0])
    fits = []
    for unten in (-25, -35):
        bereich = (pegel <= -5) & (pegel >= unten)
        if bereich.sum() < 2:
            raise ValueError(f"Zu wenige Messwerte zwischen -5 und {unten} dB.")
        m, b = np.polyfit(t[bereich], pegel[bereich], 1)
        if m >= 0:
            raise ValueError("Die Energieabklingkurve fällt nicht ab.")
        fits.append((-60 / m, m, b))
    t20, t30 = fits[0][0], fits[1][0]
    radius = 0.057 * np.sqrt(6000 / t30)
    print(f"Gruppe 4 – RIR_C.wav | 6000 m³ | {fs} Hz | {len(h)/fs:.2f} s")
    print(f"T20: {t20:.2f} s\nT30 / T60-Schätzung: {t30:.2f} s")
    for ms in (50, 80):
        grenze = int(ms * fs / 1000)
        frueh, spaet = np.sum(h[:grenze] ** 2), np.sum(h[grenze:] ** 2)
        c = 10 * np.log10(frueh / spaet) if frueh > 0 and spaet > 0 else np.nan
        print(f"C{ms}: {c:.2f} dB")
    print(f"Hallradius: {radius:.2f} m")
    for abstand in (5, 12):
        alcons = 0.625 * (abstand / radius) ** 2 * t30
        sti = 1 - 0.45 * np.log10(alcons)
        print(f"{abstand} m: ALcons {alcons:.2f} %, STI {sti:.2f} (Näherung)")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(zeit, h)
    ax[0].set(title="Raumimpulsantwort RIR_C", xlabel="Zeit (s)", ylabel="Amplitude")
    ax[1].plot(t, pegel, label="Schroeder-Kurve")
    ax[1].plot(t, fits[1][1] * t + fits[1][2], "--", label="T30-Gerade")
    ax[1].set(title="Energieabklingkurve", xlabel="Zeit (s)", ylabel="Pegel (dB)", ylim=(-60, 0))
    ax[1].legend()
    for a in ax:
        a.grid(True)
    fig.tight_layout()
    fig.savefig(ORDNER / "pp1_diagramme.png", dpi=150)

    # Auralisation: erste 5 ms verändern, anschließend linear per FFT falten.
    for name in ("RIR_GlassCupC"):
        datei = ORDNER / "Ergänzendes Material" / f"{name}.wav"
        if not datei.exists():
            print(f"{datei.name} fehlt – Auralisation übersprungen.")
            continue
        audio_fs, trocken = lesen(datei)
        h_audio = abtastrate(h, fs, audio_fs)
        laenge = len(trocken) + len(h_audio) - 1
        nfft = 1 << (laenge - 1).bit_length()
        trocken_fft = np.fft.rfft(trocken, nfft)
        for variante, faktor in (("nah", 1.8), ("fern", 0.5)):
            h_var = h_audio.copy()
            h_var[:int(0.005 * audio_fs)] *= faktor
            nass = np.fft.irfft(trocken_fft * np.fft.rfft(h_var, nfft), nfft)[:laenge]
            speichern(ORDNER / f"{name}_{variante}.wav", audio_fs, nass)
    plt.show()


if __name__ == "__main__":
    main()
