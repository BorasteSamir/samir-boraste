# 3-Minute Screen Recording Guide & Speaking Script

**Assignment Requirement:**
> *"A 3-minute screen recording with your voice (an unlisted YouTube or Drive link in the README; phone or free screen recorder is fine). Open the data and show us the evidence for the flag you are proudest of and for the one you are least sure of. No slides, no editing needed."*

Use OBS, Loom, Windows Game Bar (`Win + G`), or any free screen recorder.

---

## Preparation (Before Pressing Record)
Open the following on your screen:
1. Terminal / VS Code / File Explorer showing `flags.csv` and `checker.py`.
2. A spreadsheet or code viewer with:
   - `ridgeline_data_pack (2)/data/S06.csv` and `ridgeline_data_pack (2)/gps/S06.nmea` (for the flag you are **proudest of**).
   - `ridgeline_data_pack (2)/data/S04.csv` (for the flag you are **least sure of**).
3. Have `report.pdf` open in a PDF viewer.

---

## Script Breakdown (Exact Timing: 3 Minutes Total)

### 0:00 – 0:35 | Introduction & Overview
* **What to show on screen:** Terminal running `python checker.py "ridgeline_data_pack (2)"`, then show the resulting `flags.csv`.
* **What to say:**  
  *"Hello, I'm [Your Name]. Today I'm walking through my quality control analysis for the Ridgeline Schools Weather Network assignment.  
  Our automated checker, `checker.py`, runs with a single command against the data pack directory and outputs `flags.csv` containing 16 vetted issues.  
  Rather than using hardcoded rules, our checker implements physical bounds, GPS time-sync parsing, and robust pairwise consensus voting across the network to isolate real anomalies without false alarms."*

---

### 0:35 – 1:45 | The Flag I Am Proudest Of: S06 Clock Shift (MDT vs UTC)
* **What to show on screen:**  
  1. Open `data/S06.csv` around row 3408–3410. Highlight timestamp `2025-03-24 16:00` followed by `2025-03-24 10:10`.  
  2. Open `gps/S06.nmea` around the same date and show `$GPRMC,161000.00,A,...`.  
  3. Show the corresponding row in `flags.csv`: `S06 | all | correct | add 6 hours`.
* **What to say:**  
  *"The flag I am proudest of is Station S06's clock shift.  
  If you only look at the timestamps naively—like an AI tool initially suggested to me—you see row 3408 at 16:00 followed by row 3409 jumping backwards to 10:10. A standard script would discard those 2,600 subsequent rows as corrupted time index.  
  However, looking at the volunteer notebook, the volunteer swapped the battery on March 24 and noted 'the clock showed the right time on the screen so I left it.'  
  When you open `gps/S06.nmea` at the exact same moment, the GPS sentence reports 16:10 UTC!  
  10:10 was simply 10:10 AM local Mountain Daylight Time (UTC-6). The logger clock was never broken; it was rebooted into local time.  
  Because our checker cross-references the raw NMEA sentences with the logger clock, it recognizes this deterministic 6-hour shift. Adding 6 hours to all timestamps from row 3409 onwards recovers 100% of the data with zero loss."*

---

### 1:45 – 2:40 | The Flag I Am Least Sure Of: S04 Fence Albedo Heating
* **What to show on screen:**  
  1. Open `data/S04.csv` and show March 15 data.  
  2. Show the `flags.csv` row: `S04 | temp_c | keep | daytime radiative heating from white fence`.  
  3. Briefly show the `DECISIONS.md` Section 02.
* **What to say:**  
  *"The call I am least sure about is our decision on Station S04's temperature after March 15.  
  The volunteer log states that the garden committee repainted the fence and the mounting post 'nice and white.'  
  When we analyze the data before and after March 15, we discovered a fascinating split:  
  At night, S04's temperature difference relative to neighboring stations is completely unchanged (+0.07°C). But during sunny daytime hours when solar radiation exceeds 400 W/m², S04 jumps by +1.40°C warmer than its neighbors!  
  This daytime-only warming is classic albedo reflection—sunlight bouncing off the newly white post into the passive radiation shield.  
  The reason I am least sure about this call is the dilemma of microclimate versus error: the sensor isn't broken; it is faithfully recording the real air temperature in that specific garden pocket. If we try to mathematically subtract an offset, we might introduce artificial errors on cloudy or windy days.  
  We decided to mark it as `action: keep` with a siting caution. The one piece of information that would settle this would be temporarily deploying an aspirated, fan-ventilated reference probe 2 meters away from the fence to measure true unperturbed ambient air."*

---

### 2:40 – 3:00 | Conclusion & Technician Dispatch
* **What to show on screen:**  
  Open `report.pdf` (Page 2) showing the Volunteer Technician Work Order for **Station S03 (Valley Library)**.
* **What to say:**  
  *"Finally, for the coordinator's Monday decisions: our 2-page report recommends publishing 88.4% of the data directly, applying our software fixes for S02, S06, and S07, and sending our one technician next week to Station S03 (Valley Library). S03 has an active, recurring 1-wire digital probe disconnect that software cannot fix and needs immediate physical servicing.  
  Thank you for reviewing my work!"*
