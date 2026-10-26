# DECISIONS.md

## 01. The Visit
*The technician has one hour at one station next week. Which station, what exactly do they do, and what do they check first? Why that station and not the second-best one?*

**Dispatch Station: S03 (Valley Library)**

* **What they check first (Minute 0–10):**  
  Open the logger enclosure and inspect the terminal block connections for the digital temperature sensor inside the passive radiation shield. Specifically check the 1-wire bus lines (VCC, DQ data, and GND) for loose screw terminals, wire strain fatigue, or corrosion. On Dallas DS18B20 1-wire digital sensors, an intermittent ground or data line disconnect produces characteristic open-circuit readings of `-40.0°C` and resets the scratchpad register to its power-on default of `+85.0°C`.
* **What they do in the remaining 50 minutes:**  
  1. Gently pull-test each wire on the terminal strip and re-strip/re-seat any frayed conductors.  
  2. Swap out the existing digital probe with the pre-tested spare DS18B20 temperature probe from the spares kit.  
  3. Inspect the passive radiation shield louvers and brush away any spider webs or debris that impede airflow.  
  4. Power-cycle the logger, observe real-time readings on the LCD screen, and verify live temperature against a handheld reference thermometer over 10 minutes before sealing the enclosure with fresh silicone grease.
* **Why S03 and not the second-best one?**  
  The plausible second-best stations are **S07** (to verify the replacement anemometer model), **S02** (to calibrate the replacement pressure board), or **S06** (to set the clock). However, S02, S06, and S07 are **100% deterministic and completely recoverable in software**:
  * S06 was a fixed -6-hour time zone shift after battery replacement; adding 6 hours recovers all data perfectly.
  * S07 was an anemometer unit scaling error (reporting m/s instead of km/h); multiplying by 3.6 restores the wind speed record.
  * S02 was a static +6.66 hPa uncalibrated board offset; subtracting 6.66 hPa aligns it with regional elevation physics.  
  
  **S03 is the only station with an active, recurrent, stochastic hardware failure.** It glitched to `-40.0°C` on March 5 and April 2, glitched to `+85.0°C` on March 12 and April 8, and suffered an 80-hour total freeze at `6.5°C` (March 18–21). April 8 is in the final week of data. This intermittent physical disconnect will continue to drop and corrupt ongoing spring data. Software cannot reconstruct missing temperatures during hardware latchups. Physical servicing at S03 is essential.

---

## 02. Your Least Certain Call
*Pick the decision in flags.csv you are least sure about. What is the evidence each way, and what single piece of information would settle it?*

**Decision: S04 Temperature (`temp_c`), from 2025-03-15 12:00 onwards — Action: `keep` (Issue: Daytime radiative heating from white fence)**

* **Evidence for flagging / correcting:**  
  On March 15, the garden committee repainted the fence and mounting post "nice and white". Immediately following this date, S04's daytime temperatures during high solar irradiance (`ghi_wm2 > 400 W/m²`) jumped by **+1.40°C** relative to neighboring stations (S02, S03, S05). Crucially, nighttime temperatures (`ghi_wm2 == 0`) showed **no change (+0.07°C)**. This daytime-only divergence is textbook evidence of increased surface albedo: reflected sunlight from the newly painted white post and fence entering the bottom of the passive radiation shield, artificially warming the sensor above true ambient air temperature.
* **Evidence against correcting / for keeping:**  
  The sensor itself is not broken; it is faithfully measuring the real thermodynamic microclimate of that garden post. Siting changes are a reality of community networks. Modifying this in post-processing by subtracting an artificial daytime temperature offset risks corrupting real meteorological variations (e.g. breezy days where ventilation neutralizes albedo heating).
* **Single piece of information that would settle it:**  
  A temporary side-by-side deployment of an **aspirated (fan-ventilated) reference temperature probe** placed 2 meters away from the white fence. Comparing aspirated ambient air temperature against S04's passive shield on calm, sunny afternoons would quantify the exact radiative heating bias and settle whether a mathematical correction is justified.

---

## 03. Where the AI Was Wrong
*Give one or two moments where an AI tool gave you something plausible but wrong (code, an explanation, a threshold). Quote it briefly and say how you noticed.*

* **Moment 1: Trusting the volunteer's lay diagnosis over atmospheric physics on S02.**  
  *What the AI said:* Prompted with the log note ("*Pressure reading looked 'a bit off' to the science teacher. Swapped pressure board with spare from cupboard*"), the AI stated:  
  > *"S02 pressure sensor was failing prior to March 21 because the teacher noticed it reading low; exclude pre-swap data and keep post-swap data."*  
  
  *How I noticed:* I evaluated the barometric formula using station elevations. S02 (North Mesa School) is at 1623 m, exactly 100 meters higher than S03 (Valley Library, 1523 m). The standard atmospheric pressure lapse rate is ~1.2 hPa per 10 meters, so S02 *must* read ~10 to 12 hPa lower than S03. Prior to March 21, S02 read exactly 10.0 hPa lower than S03—physically textbook perfect! The science teacher had compared station pressure to sea-level pressure and mistakenly assumed it was wrong. The uncalibrated spare board swapped in from the cupboard read +6.66 hPa too high. The AI uncritically adopted the human note and recommended discarding valid historical data while keeping the uncalibrated replacement.

* **Moment 2: Recommending deletion of S06's "backward time jump" records.**  
  *What the AI said:* When reviewing timestamp monotonicity in S06, the AI flagged row 3409 (`2025-03-24 16:00` jumping back to `10:10`) and proposed:  
  > *"Corrupted time index detected; delete all 2,639 subsequent rows from row 3409 onwards as invalid unsynchronized records."*  
  
  *How I noticed:* I cross-referenced the GPS NMEA sentences (`S06.nmea`). At the exact line where the logger recorded `10:10`, the `$GPRMC` sentence logged `16:10:00 UTC`. The volunteer noted swapping the battery around 10 am local time and seeing the "right time on the screen." The logger was simply running on Mountain Daylight Time (MDT = UTC - 6 hours)! Deleting those rows would have thrown away 2.5 weeks of pristine weather data. Adding 6 hours restored the entire record seamlessly.

---

## 04. Next Year
*The same checker has to run unattended on 500 stations, and nobody will read every flag. What do you change, what do you drop, and what would you refuse to automate?*

* **What to change:**  
  1. *Spatial Consensus Quality Control:* Implement automated spatial Kriging or Barnes objective analysis against the $k$-nearest neighbor stations (weighted by inverse distance and elevation lapse rate). If a station deviates beyond a $3.5\sigma$ spatial z-score persistently across 6 consecutive intervals, flag it automatically.  
  2. *Automated Edge Validation:* Ingest raw GPS NMEA sentences directly into the telemetry pipeline. If the time delta $|t_{\text{logger}} - t_{\text{GPS}}| > 60\text{ seconds}$, trigger an automated clock desynchronization alert immediately upon transmission.  
  3. *Triage Severity Levels:* Separate outputs into automated pipeline actions (e.g. deduplicating identical replayed blocks) versus human review tickets.
* **What to drop:**  
  1. *Subtle Siting / Microclimate Warnings:* Drop flagging subtle 0.5–1.0°C microclimate shifts like S04's repainted fence. In a 500-station network, microclimate variations are ubiquitous; flagging them creates debilitating alert fatigue.  
  2. *Single-interval spikes for human ticket queues:* Drop creating manual tickets for isolated 10-minute sensor glitches (`-40°C`, `+85°C`); handle them unattended with standard automated median despiking filters.
* **What to REFUSE to automate:**  
  1. *Uncalibrated Sensor Re-scaling / Offset Injections:* Refuse to let an algorithm automatically guess and inject scale factors (like the 3.6× anemometer multiplier or 6.66 hPa pressure offset) into the canonical archive without human verification of the hardware model and calibration sheet. Automated re-scaling across 500 stations without hardware provenance risks baking systematic bias into the regional climate record.  
  2. *Field Technician Dispatch:* Refuse to automate truck rolls. Field visits incur significant travel, volunteer time, and financial cost. Dispatch recommendations should be prioritized by algorithm, but a human coordinator must approve site visits.

---

## 05. By Hand
*Without code or AI, work out roughly at what UTC time the sun is highest at station S04 on 20 March 2025. Show your working in a few lines and say what it is useful for here.*

**Station S04 Coordinates:** Latitude $39.7540^\circ \text{ N}$, Longitude $105.1460^\circ \text{ W}$ ($-105.1460^\circ$).

1. **Solar Noon Definition:** The sun reaches its highest point at Local Solar Noon, which is exactly $12:00:00$ Local Solar Time (LST).
2. **Longitude to Time Conversion:** Earth rotates $360^\circ$ in 24 hours ($1440 \text{ minutes}$), corresponding to $15^\circ \text{ per hour}$ or $4 \text{ minutes per degree}$ ($1^\circ = 4\text{ min}$).
3. **Time Offset from Prime Meridian (0° Longitude, UTC):**  
   $$\text{Offset} = 105.1460^\circ \times 4 \text{ min/deg} = 420.584 \text{ minutes} = 7 \text{ hours, } 0 \text{ minutes, } 35 \text{ seconds}$$
4. **Mean Solar Noon in UTC:** Since S04 is West of Greenwich, solar noon occurs $7\text{h } 00\text{m } 35\text{s}$ *after* 12:00:00 UTC:  
   $$\text{Mean Solar Noon} = 12:00:00 + 07:00:35 = \mathbf{19:00:35 \text{ UTC}} \approx \mathbf{19:01 \text{ UTC}}$$
5. **Astronomical Equation of Time (EoT) Adjustment:** On the March 20 equinox, the Equation of Time due to Earth's orbital eccentricity and axial obliquity is approximately $-7.2 \text{ minutes}$ (solar noon lags mean noon by ~7 minutes):  
   $$\text{True Solar Noon} = 19:00:35 - (-00:07:12) = \mathbf{19:07:47 \text{ UTC}} \approx \mathbf{19:08 \text{ UTC}}$$

**What it is useful for here:**  
It provides an **independent, physical clock synchronization reference** using only the station's solar irradiance (`ghi_wm2`) data. On clear days, pyranometer irradiance physically peaks at true solar noon. By checking the timestamp when `ghi_wm2` reaches its diurnal maximum against this calculated time (~19:08 UTC), we can verify logger clock accuracy and immediately detect time zone configuration errors (such as S06 logging in local MDT, where solar radiation peaked at ~13:00 logger time instead of 19:00 UTC) without relying on network NTP or GPS fixes.
