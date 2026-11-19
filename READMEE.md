# Tontechnik 2 (TON2) – Prüfungsleistung (WiSe 2026/27)

* **Hochschule:** HAW Hamburg (Department Medientechnik – DMI-MT)
* **Dozentin:** Prof. Dr.-Ing. Eva Wilk
* **Abgabefrist:** 15.02.2027 (via Moodle)

---

## 📋 Allgemeine Informationen

Die Prüfungsleistung im Modul **Tontechnik 2** besteht aus einer Fallstudie mit drei aufeinander aufbauenden **Praxisproblemen** aus dem Bereich Tonstudio-Umgebung und Audiomischung. 

* **Bearbeitungszeitraum:** Ab dem 13.10.2026 bis zum 15.02.2027
* **Gruppenarbeit vs. Einzelleistung:** Die Besprechung und Erarbeitung findet in Gruppen von 4 Personen statt. **Fertigstellung, Validierung, Abgabe und Dokumentation erfolgen jedoch als Einzelleistung.** Der Eigenanteil muss im Code sowie in der Dokumentation klar erkennbar und ausgewiesen sein.
* **Bewertung:** Pro Praxisproblem können maximal 25 Punkte erreicht werden (insgesamt **75 Punkte**). Zusätzlich sind bis zu **8 Zusatzpunkte** möglich.

---

## 🛠️ Übersicht der Praxisprobleme

Für jedes Praxisproblem ist eine Dokumentation von **verbindlich 1,5 Seiten (DIN A4, Schriftgröße 11)** anzufertigen. *(Wesentliche Abweichungen führen zu Punktabzug).*

### 1. Praxisproblem 1: Raumakustik & Impulsantwort
* **Ausgabe:** 13.11.2026 | **Bearbeitung bis:** 26.11.2026
* **Aufgabe:** Analyse gemessener und berechneter Raumeigenschaften zur Bewertung der Eignung für verschiedene Nutzungsszenarien. Ermittlung der Parameter und eines Höreindrucks aus einer vorgegebenen Raum-Impulsantwort mittels eigenem Python-Code.
* **Dokumentation:** 1,5 Seiten (DIN A4, 11 pt)

### 2. Praxisproblem 2: Audio-Effekte & Systemtheorie
* **Ausgabe:** 27.11.2026 | **Bearbeitung bis:** 10.12.2026
* **Aufgabe:** Systemtheoretische und auditive Analyse von Audio-Effekten, um Zusammenhänge zwischen Parametern, Analyse-Ergebnissen und Höreindruck herzustellen. Eigene Modellierung der Effekte und Analyseverfahren in Python gemäß Vorgaben.
* **Dokumentation:** 1,5 Seiten (DIN A4, 11 pt)

### 3. Praxisproblem 3: Mixing & Test-Umgebung
* **Ausgabe:** 11.12.2026
* **Aufgabe:** Überprüfung theoretischer Zusammenhänge zum Mixing anhand einer eigenen Mischung und des Höreindrucks (Bestimmung des Geltungsbereichs). Erstellung einer entsprechenden Test- und Mess-Umgebung in Python.
* **Dokumentation:** 1,5 Seiten (DIN A4, 11 pt)

---

## ⭐ Optionale Zusatzaufgaben (max. 8 Zusatzpunkte)

1. **Dante Certification Level 2 (4 Punkte)**
   * Erfolgreiches Ablegen der *Dante Zertifizierung Level 2 – fortgeschrittene Dante Konzepte*.
   * **Abgabe:** Zertifikat sowie eine 0,5 bis 1-seitige Zusammenfassung und Reflexion der fachlichen Inhalte im Kontext des Studiums.

2. **AI Music Generator (4 Punkte)**
   * Erstellung eines Songs aus einem gewählten Jahrzehnt (**1920–1930**, **1950–1960** oder **1960–1970**; Region: USA, Deutschland oder England) mithilfe eines KI-Musikgenerators (z. B. Suno, Udio, Media.io).
   * Iterative Optimierung der Prompts, um Genre und Stil möglichst authentisch zu treffen.
   * **Abgabe:** Original-Referenzsong, KI-Generierung, verwendete Prompts sowie ein 0,5 bis 1-seitiger Vergleich (Instrumentierung, Mischung, Stereobild, Text etc.) und Dokumentation des Vorgehens.

---

## 📦 Abgabemodalitäten & Verzeichnisstruktur

Die Abgabe erfolgt als **einzelnes ZIP-Archiv** über Moodle (maximale Dateigröße: **100 MB**).

### Namenskonvention (Verbindlich!)
Das ZIP-Archiv muss exakt folgendermaßen benannt werden *(Abweichungen führen zu Punktabzug)*:
```text
<Gruppen-Buchstabe>_<Matrikel-Nr.>_Prfg_TON2_WiSe26.zip
```
*(Hinweis: Alle enthaltenen Code-Dateien und PDFs müssen ebenfalls eindeutig dir zugeordnet werden können und Name/Matrikelnummer sowie Aufgabennummer enthalten.)*

### Empfohlene Projektstruktur (für das ZIP-Archiv / Repository)
```text
<Gruppen-Buchstabe>_<Matrikel-Nr.>_Prfg_TON2_WiSe26/
├── Dokumentation_TON2_<Matrikel-Nr.>.pdf   # Alle Dokumentationen (PP1-3 + ggf. Zusatzaufgaben) in EINEM PDF
├── Praxisproblem_1/
│   ├── pp1_analyse_<Matrikel-Nr.>.py        # Lauffähiger, kommentierter Python-Code
│   └── audio/                              # Verwendete Test-Signale & Impulsantworten (.wav)
├── Praxisproblem_2/
│   ├── pp2_effekte_<Matrikel-Nr.>.py        # Lauffähiger, kommentierter Python-Code
│   └── audio/                              # Test-Signale & gerenderte Effekte (.wav)
├── Praxisproblem_3/
│   ├── pp3_mixing_<Matrikel-Nr.>.py         # Test- und Mess-Umgebung in Python
│   └── audio/                              # Test-Signale & eigene Mischung (.wav)
└── Zusatzaufgaben/                         # Optional
    ├── Dante_Zertifikat_Level2_<Matrikel-Nr.>.pdf
    └── AI_Music/
        ├── original_referenz.wav
        ├── ai_generierung.wav
        └── prompts.txt
```

---

## ✅ Checkliste vor der Abgabe

- [ ] Eigenanteil im Python-Code und in der Dokumentation klar gekennzeichnet?
- [ ] Alle Python-Skripte sind lauffähig und ausreichend kommentiert?
- [ ] Alle verwendeten Test-Signale und relevanten Audiodateien liegen im `.wav`-Format bei?
- [ ] Alle schriftlichen Ausarbeitungen sind in **einem einzigen PDF** zusammengefasst?
- [ ] Seitenvorgaben eingehalten (je 1,5 Seiten A4, Schriftgröße 11 pro Praxisproblem)?
- [ ] Jede Aufgabe im PDF mit Name/Matrikelnummer und Aufgabennummer beschriftet?
- [ ] Dateinamen-Schema `<Gruppen-Buchstabe>_<Matrikel-Nr.>_Prfg_TON2_WiSe26.zip` exakt eingehalten?
- [ ] Dateigröße der ZIP-Datei unter 100 MB?
