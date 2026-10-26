Samir Boraste
[Your Email Address]
[Your 3-Minute Video Link - Unlisted YouTube / Google Drive]
Run: python checker.py "<path_to_data_pack>"

# Ridgeline Weather Network - Quality Control & Network Health Analysis

Automated quality control checker, network health audit, and operational decision report for the Ridgeline Schools Weather Network (8 stations across 6 weeks).

---

## 1. Quick Start

### Prerequisites
* Python 3.8+
* Dependencies: `pandas`, `numpy`, `reportlab` (for PDF report generation)

Install dependencies:
```bash
pip install pandas numpy reportlab
```

### Running the Checker
Run the checker with a single command passing the path to the data pack folder as an argument:
```bash
python checker.py "ridgeline_data_pack (2)"
```
This reads `stations.csv`, `data/*.csv`, and `gps/*.nmea`, executes all quality control routines, and writes `flags.csv` into the directory from which the command is executed.

To re-generate the PDF version of the coordinator health briefing:
```bash
python generate_pdf.py
```
*(An interactive HTML version formatted for A4 printing is also provided in `report.html`.)*

---

## 2. What Each Check Does

The automated checker (`checker.py`) runs 9 modular, physically and statistically grounded verification routines:

1. **GPS Metadata & Coordinate Typo Verification (`metadata`):**
   * Parses standard NMEA 0183 `$GPRMC` sentences from `gps/Sxx.nmea`.
   * Calculates the median fix coordinates and compares them against `lat` and `lon` in `stations.csv`.
   * Flags discrepancies exceeding 0.05° (~5 km). *Detects S05 install sheet latitude typo (39.5700° vs 39.7540° N).*
2. **GPS Clock Drift & Local Time Discontinuity (`all`):**
   * Compares the logger timestamp prefix against the UTC timestamp in `$GPRMC` sentences.
   * Scans for backwards time steps or persistent multi-hour offsets. *Detects S06 clock reset to local Mountain Daylight Time (MDT = UTC-6) following a battery swap on March 24.*
3. **Identical Replay & Duplicate Block Detection (`all`):**
   * Identifies identical rows (duplicate timestamp and all sensor readings) appended out of chronological order. *Detects S08 144-record duplicate dump for April 5.*
4. **Telemetry Outage & Transmission Gap Detection (`all`):**
   * Scans chronological timestamps for intervals exceeding 15 minutes. *Detects S08 35.8-hour telemetry gap (March 16–18) caused by cellular SIM data plan exhaustion.*
5. **Digital Sensor Spikes & Bus Errors (`temp_c`):**
   * Screens for hardware error codes on digital 1-wire sensors: `-40.0°C` (bus open-circuit / disconnect) and `+85.0°C` (Dallas DS18B20 power-on reset scratchpad default). *Detects S03 intermittent spikes on March 5, March 12, April 2, and April 8.*
6. **Sensor Frozen / Flatline Detection (`temp_c`, `pressure_hpa`, `wind_kmh`):**
   * Analyzes consecutive runs of identical floating-point values exceeding 3 hours while surrounding environmental channels vary. *Detects S03 80.2-hour temperature freeze at 6.5°C (March 18–21).*
7. **Physical Limit & Waterlogged Saturation Screening (`rh_pct`):**
   * Detects physically impossible readings (`rh_pct > 100%`) and extended periods pegged at saturation during daytime solar irradiance (`ghi_wm2 > 200 W/m²`). *Detects S05 84-hour waterlogged capacitive sensor saturation (March 7–11).*
8. **Precipitation Funnel Blockage & Cleaning Artifacts (`rain_mm`):**
   * Identifies unphysical rainfall surges (>5 mm in 10 minutes while regional network is dry). *Detects S04 artificial 33.4 mm dump on April 2 resulting from trapped water clearing during funnel maintenance, and flags the preceding suppressed accumulation period.*
9. **Spatial Consensus Step Detection (`pressure_hpa` & `wind_kmh`):**
   * Uses pairwise differential consensus voting: computes $\Delta_{i,j}(t) = X_i(t) - X_j(t)$ across all station pairs $(i, j)$.
   * Prevents false positives caused by regional weather fronts or missing station data.
   * *Detects S02 +6.66 hPa uncalibrated pressure board offset (swapped March 21 at 11 am local).*
   * *Detects S07 anemometer scaling drop of ~3.6× (replacement anemometer outputting in m/s rather than km/h).*
10. **Radiative Siting & Microclimate Reflection (`temp_c`):**
    * Compares daytime temperature differentials against nighttime differentials before and after site modifications. *Evaluates S04 +1.4°C daytime warming caused by white fence repainting.*

---

## 3. What We Did Not Get To

Given the scope of the 48-hour assignment, several advanced extensions were prioritized for future unattended deployment:
1. **Dynamic Diurnal Envelope Fitting for Pyranometer Drift:**  
   Implementing a clear-sky solar model (e.g., Bird or Haurwitz clear-sky envelope) to detect subtle pyranometer soiling, sensor tilt, or leveling errors on non-cloudy days.
2. **Wind Direction Circular Statistics & Vector Variance:**  
   Circular dispersion analysis ($\theta \in [0, 360)$) to identify partial mechanical binding or potentiometer dead-band flatlining on wind vanes during low-speed transitions.
3. **Automated Battery Voltage State-of-Health Modeling:**  
   Correlating battery swap dates and diurnal solar charging curves with internal logger voltage telemetries to preemptively predict battery exhaustion prior to station shutdown.

---

## 4. Repository Structure

* `checker.py`: The single-command automated quality control program.
* `flags.csv`: Output table of all real issues, exact timestamps, actions, and evidence.
* `DECISIONS.md`: In-depth engineering justifications, technician mission plan, edge case evaluation, AI critique, 500-station scalability, and hand solar noon calculation.
* `report.html`: Two-page coordinator health briefing, formatted for A4 printing.
* `report.pdf`: Publication-quality vector PDF of the two-page briefing.
* `generate_pdf.py`: Python script used to compile `report.pdf` using `reportlab`.
* `ai_logs/`: Complete exports and transcripts of AI collaboration sessions and prompt iterations.
* `VIDEO_RECORDING_SCRIPT.md`: Step-by-step guide for the candidate's 3-minute video recording.
