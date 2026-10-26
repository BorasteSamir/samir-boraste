# AI Prompt & Session Log 01: Initial Data Audit and Anomaly Exploration

**Date:** 2026-10-26  
**Tool:** Gemini / Claude Assistant  
**Topic:** Initial inspection of Ridgeline 6-week weather network dataset

---

### Prompt 1 (User)
> I have a dataset from 8 weather stations (S01 to S08) with 10-minute intervals over 6 weeks, companion GPS NMEA files, and a volunteer maintenance notebook. We need to build an automated checker that outputs `flags.csv`, write a 2-page coordinator health report, and answer the decisions document. Can you inspect the dataset structure and find any obvious issues?

### Response 1 (AI)
Let's examine the structure of the data files and stations metadata.
The files contain:
- `stations.csv`: 8 stations with lat, lon, elevation, install dates.
- `data/Sxx.csv`: 10-minute interval sensor logs (temp_c, rh_pct, pressure_hpa, wind_kmh, wind_dir_deg, rain_mm, ghi_wm2).
- `gps/Sxx.nmea`: hourly NMEA sentences ($GPRMC, $GPGGA).
- `maintenance_log.md`: volunteer maintenance notes.

Initial file inspection:
- Expected records: 42 days * 24 hours * 6 = 6,048 records per station.
- S01 to S05, S07 have 6,048 rows.
- S06 has 6,048 rows but ends at 2025-04-11 17:50 (6 hours early).
- S08 has 5,978 rows (missing 70 rows).

Looking at the maintenance notes:
1. S01: Snow cleared from solar panel on Mar 2; snowed in on Mar 31.
2. S02: Volunteer swapped pressure board on Mar 21 with uncalibrated board from cupboard.
3. S03: Routine checks on Mar 6 and Apr 9.
4. S04: Fence repainted white on Mar 15; rain gauge funnel cleared of leaves/nest on Apr 2.
5. S05: Kids asked why humidity was 100 all week when sunny (Mar 10).
6. S06: Battery swapped on Mar 24, logger clock showed time on screen.
7. S07: Anemometer cups replaced on Mar 26 with different brand.
8. S08: SIM expired on Mar 17; duplicate day on website on Apr 5.

---

### Prompt 2 (User)
> Look at S02 pressure and S06 clock. What do you think happened?

### Response 2 (AI) [DEAD END / PLAUSIBLE BUT FLAWED RESPONSE]
> On S02, the teacher noted pressure was "a bit off" before March 21. Looking at the data, S02 pressure was ~831 hPa while other stations like S03 were ~841 hPa. Therefore, S02 pressure sensor was failing prior to March 21 because it was under-reading by 10 hPa. Swapping the board brought it back closer to normal. You should exclude S02 pressure data before March 21.
>
> On S06, the timestamp column has a negative time jump from 16:00 back to 10:10 on March 24. This looks like logger memory corruption after the battery rebooted. You should discard all records from row 3409 onwards as invalid desynchronized data.

### Critique / Human Engineer Correction:
Wait, that is completely wrong on both counts!
1. For S02: S02 is at elevation 1623 m, North Mesa School. S03 is at 1523 m in the valley. That's a 100 m elevation difference! In standard atmospheric lapse rate, 100 m elevation corresponds to ~10 to 12 hPa lower pressure! S02 reading -10 hPa lower than S03 was PHYSICALLY CORRECT. The teacher compared North Mesa pressure to the valley or sea level and mistakenly thought it was too low. When the volunteer swapped the board with an uncalibrated board from the cupboard, S02 jumped by +6.66 hPa! The replacement board is the one that's uncalibrated and reading too high!
2. For S06: Row 3409 jumped from 16:00 to 10:10. 16:00 UTC is exactly 10:00 AM Mountain Daylight Time (MDT = UTC-6)! Looking at `S06.nmea`, the GPS sentence at row 3409 explicitly logs `16:10:00 UTC`. The logger clock simply defaulted to local MDT time instead of UTC! The data is not corrupt at all; adding 6 hours restores 100% of the subsequent 2,639 records!

---

### Prompt 3 (User)
> Let's check S07 wind and S05 humidity. What is the mathematical relationship?

### Response 3 (AI)
Let's analyze S07 wind speed before and after March 26 15:30:
- Before March 26: S07 wind ratio to S08 was ~1.09.
- After March 26: S07 wind ratio to S08 was ~0.286.
- The ratio change is 1.09 / 0.286 = 3.81 (or ~3.6 across all regional stations).
- Since $1\text{ m/s} = 3.6\text{ km/h}$, the replacement anemometer from the spares box outputs pulses calibrated for meters per second, while the logger assumes kilometers per hour!
- Correction: Multiply wind speed by 3.6 from 2025-03-26 15:30 onwards.

For S05 humidity:
- Maintenance log: Kids asked why humidity says 100 all week when it's sunny on March 10.
- Examining S05 data: Following a rain/snow event on March 7 at 01:00–05:00, S05 relative humidity spiked to 100% and stayed saturated between 100% and 105% continuously from March 7 12:00 to March 11 00:00 (84.2 hours).
- During this time, daytime solar irradiance (GHI) reached > 750 W/m² and temperatures rose to 11°C, while neighboring stations read 25–35% RH.
- The capacitive sensor element was waterlogged. On March 11 at 00:10 it dried out and dropped to 7%.
- Action: Exclude S05 RH from 2025-03-07 12:00 to 2025-03-11 00:00.

Also, checking `stations.csv`:
- S05 metadata says latitude 39.5700° N.
- But `S05.nmea` GPS fixes consistently report latitude 39.7540° N (39° 45.24' N).
- Notice digits 57 and 75 were transposed on the install sheet!
- Action: Correct metadata latitude to 39.7540° N.
