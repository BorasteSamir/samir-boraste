# AI Prompt & Session Log 02: Consensus Algorithms, Checker Development, and Decisions

**Date:** 2026-10-26  
**Tool:** Gemini / Claude Assistant  
**Topic:** Quality Control Checker Implementation, Consensus Step Detection, and Report Design

---

### Prompt 4 (User)
> We need to implement `checker.py` so it can run with:
> `python checker.py <pack_directory>`
> and write `flags.csv` into the current working directory.
> How should we detect the S02 pressure jump and S07 anemometer change without hardcoding?

### Response 4 (AI)
We can use network median comparison. For each station, compute the difference against the median of all stations:
`diff = station_pressure - median(other_pressures)`
Then compute rolling mean before and after.

### Critique / Human Debugging:
When testing this initial code, we got false positive flags on S01, S04, S05, and S06!
Why?
Because when S02 jumped by +6.66 hPa, taking the median of all stations caused the median itself to shift! Furthermore, S08 had a missing data gap from March 16–18. When S08 (the highest pressure station) re-entered on March 18 at 01:40, the network median dropped abruptly, creating a false step change flag on March 18!

**Solution: Pairwise Consensus Voting**
Instead of comparing against a single network median, we compare target station $i$ against all other stations $j$ individually:
$\Delta_{i,j}(t) = P_i(t) - P_j(t)$
For S02, *every single pairwise difference* jumps by +6.66 hPa at 2025-03-21 17:20:
- S02 - S01: +6.6 hPa
- S02 - S03: +6.5 hPa
- S02 - S04: +6.6 hPa
- S02 - S05: +6.7 hPa
- S02 - S06: +6.5 hPa
- S02 - S07: +6.5 hPa
- S02 - S08: +6.6 hPa
The median of pairwise jumps for S02 is +6.66 hPa!
For any other station (e.g. S04), 6 out of 7 pairwise differences have 0.0 jump, and only S04 - S02 jumps by -6.6 hPa. Thus, the median jump for S04 is 0.0 hPa!
This eliminated 100% of false positives across the entire network.

The exact same pairwise consensus voting applies to the anemometer scale factor on S07, isolating S07 with a 3.6x drop while all other stations have median ratio changes of ~1.0.

---

### Prompt 5 (User)
> What about S03? What is happening with S03 temperature?

### Response 5 (AI)
Looking at S03:
1. Spikes:
   - Row 662 (2025-03-05 14:20): -40.0°C
   - Row 1606 (2025-03-12 03:40): +85.0°C
   - Row 4741 (2025-04-02 22:10): -40.0°C
   - Row 5531 (2025-04-08 09:50): +85.0°C
2. Flatline:
   - From 2025-03-18 06:00 to 2025-03-21 14:00 (481 consecutive 10-minute intervals = 80.2 hours), S03 temperature was frozen at exactly 6.5°C while other channels (humidity, wind, pressure, solar) varied normally.
3. Analysis:
   - `-40.0°C` is the standard open-circuit / 1-wire disconnect code for digital probes.
   - `+85.0°C` is the well-known Dallas DS18B20 digital temperature sensor power-on reset default scratchpad register value.
   - This indicates an intermittent physical connection (loose screw terminal or cracked solder joint) on the 1-wire digital bus at S03.
   - Because S03 has an active, recurrent physical fault (spiking as late as April 8), S03 is the #1 priority for the technician visit next week!

---

### Prompt 6 (User)
> Let's answer Question 05 of DECISIONS.md: By hand, work out roughly at what UTC time the sun is highest at station S04 on 20 March 2025.

### Response 6 (AI)
1. S04 coordinates from `stations.csv`: Lat 39.7540° N, Lon -105.1460° W.
2. Local Solar Noon is 12:00:00 Local Solar Time (LST).
3. Longitude to time conversion:
   - 360° = 24 hours = 1440 minutes -> 15° per hour -> 4 minutes per degree.
   - S04 longitude = 105.1460° W.
   - Offset from Prime Meridian = 105.1460 * 4 min = 420.584 minutes = 7h 0m 35s.
4. Mean solar noon in UTC:
   - 12:00:00 + 7h 00m 35s = 19:00:35 UTC (approx 19:01 UTC).
5. Equation of Time (EoT) on March 20:
   - EoT is approx -7.2 minutes.
   - True solar noon = 19:00:35 - (-7.2 min) = 19:07:47 UTC (approx 19:08 UTC).
6. Usefulness:
   - It provides an independent astrophysical clock reference directly from pyranometer data (`ghi_wm2`).
   - Peak irradiance occurs at solar noon; checking peak GHI allows instant detection of clock skew or time zone errors (such as S06 logging in local MDT, peaking at 13:00 logger time instead of 19:00 UTC).
