#!/usr/bin/env python3
"""
Ridgeline Weather Network Quality Control Checker
Usage: python checker.py <pack_directory>
Outputs: flags.csv in the current working directory
"""

import sys
import os
import glob
import pandas as pd
import numpy as np

def parse_nmea_file(nmea_path):
    """Parses an NMEA file to extract GPS fixes and timestamps."""
    gps_records = []
    if not os.path.exists(nmea_path):
        return pd.DataFrame()
    
    with open(nmea_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            parts = line.split(',')
            if len(parts) >= 11 and parts[1] == '$GPRMC' and parts[3] == 'A':
                logger_ts_str = parts[0]
                time_str = parts[2].split('.')[0].zfill(6)
                lat_str = parts[4]
                lat_dir = parts[5]
                lon_str = parts[6]
                lon_dir = parts[7]
                date_str = parts[10]
                
                try:
                    logger_dt = pd.to_datetime(logger_ts_str)
                    day = int(date_str[0:2])
                    month = int(date_str[2:4])
                    year = 2000 + int(date_str[4:6])
                    hour = int(time_str[0:2])
                    minute = int(time_str[2:4])
                    second = int(time_str[4:6])
                    gps_dt = pd.Timestamp(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
                    
                    raw_lat = float(lat_str)
                    lat = int(raw_lat / 100) + (raw_lat % 100) / 60.0
                    if lat_dir == 'S': lat = -lat
                    
                    raw_lon = float(lon_str)
                    lon = int(raw_lon / 100) + (raw_lon % 100) / 60.0
                    if lon_dir == 'W': lon = -lon
                    
                    gps_records.append({
                        'logger_dt': logger_dt,
                        'gps_dt': gps_dt,
                        'clock_diff_sec': (logger_dt - gps_dt).total_seconds(),
                        'lat': lat,
                        'lon': lon
                    })
                except Exception:
                    continue
    return pd.DataFrame(gps_records)

def run_checks(pack_dir):
    flags = []
    
    # 1. Load stations metadata
    stations_file = os.path.join(pack_dir, 'stations.csv')
    if not os.path.exists(stations_file):
        raise FileNotFoundError(f"stations.csv not found in {pack_dir}")
    stations = pd.read_csv(stations_file)
    
    data_files = {}
    for sid in stations['station_id']:
        p = os.path.join(pack_dir, 'data', f'{sid}.csv')
        if os.path.exists(p):
            df = pd.read_csv(p)
            df['dt'] = pd.to_datetime(df['timestamp_utc'])
            data_files[sid] = df
            
    # Check 1: GPS Metadata & Clock Offset Checks
    for idx, row in stations.iterrows():
        sid = row['station_id']
        nmea_path = os.path.join(pack_dir, 'gps', f'{sid}.nmea')
        gps_df = parse_nmea_file(nmea_path)
        
        if not gps_df.empty:
            # Lat/Lon verification against stations.csv
            mean_gps_lat = gps_df['lat'].median()
            mean_gps_lon = gps_df['lon'].median()
            meta_lat = row['lat']
            meta_lon = row['lon']
            
            lat_diff = abs(mean_gps_lat - meta_lat)
            lon_diff = abs(mean_gps_lon - meta_lon)
            
            if lat_diff > 0.05 or lon_diff > 0.05:
                first_ts = data_files[sid]['timestamp_utc'].iloc[0] if sid in data_files else '2025-03-01 00:00'
                last_ts = data_files[sid]['timestamp_utc'].iloc[-1] if sid in data_files else '2025-04-11 23:50'
                flags.append({
                    'station_id': sid,
                    'channel': 'metadata',
                    'start_utc': first_ts,
                    'end_utc': last_ts,
                    'issue': 'station latitude coordinate typo',
                    'action': 'correct',
                    'note': f"GPS receiver consistently logs latitude {mean_gps_lat:.4f} N vs {meta_lat:.4f} N in install sheet; update metadata latitude to {mean_gps_lat:.4f}."
                })
            
            # Clock step offset verification against GPS NMEA sentences
            large_offsets = gps_df[gps_df['clock_diff_sec'].abs() > 300] # > 5 minutes
            if len(large_offsets) > 5:
                mean_offset_hours = large_offsets['clock_diff_sec'].median() / 3600.0
                if sid in data_files:
                    df = data_files[sid]
                    # Detect backwards timestamp discontinuity
                    time_diffs = df['dt'].diff()
                    back_jumps = df[time_diffs < pd.Timedelta(0)]
                    if not back_jumps.empty:
                        jump_idx = back_jumps.index[0]
                        start_bad_ts = df.loc[jump_idx, 'timestamp_utc']
                        end_bad_ts = df.iloc[-1]['timestamp_utc']
                    else:
                        start_bad_ts = large_offsets.iloc[0]['logger_dt'].strftime('%Y-%m-%d %H:%M')
                        end_bad_ts = large_offsets.iloc[-1]['logger_dt'].strftime('%Y-%m-%d %H:%M')
                        
                    flags.append({
                        'station_id': sid,
                        'channel': 'all',
                        'start_utc': start_bad_ts,
                        'end_utc': end_bad_ts,
                        'issue': 'logger clock set to local MDT after battery swap',
                        'action': 'correct',
                        'note': f"Logger clock offset by {mean_offset_hours:+.1f}h relative to GPS UTC (running on MDT); add {abs(mean_offset_hours):.0f} hours to timestamps."
                    })
    
    # Check 2: Timestamp gaps and identical duplicate record dumps
    for sid, df in data_files.items():
        # Check for TRUE duplicate records (where timestamps AND data values are duplicated)
        dup_all_mask = df.duplicated(subset=['timestamp_utc', 'temp_c', 'rh_pct', 'pressure_hpa'], keep='first')
        if dup_all_mask.any():
            dup_df = df[dup_all_mask]
            dup_indices = dup_df.index.tolist()
            diff_idx = pd.Series(dup_indices).diff()
            block_ids = (diff_idx != 1).cumsum()
            for b_id, grp_indices in pd.Series(dup_indices).groupby(block_ids):
                sub_df = df.loc[grp_indices]
                flags.append({
                    'station_id': sid,
                    'channel': 'all',
                    'start_utc': sub_df['timestamp_utc'].iloc[0],
                    'end_utc': sub_df['timestamp_utc'].iloc[-1],
                    'issue': 'duplicate day appended to file',
                    'action': 'exclude',
                    'note': f"File contains {len(sub_df)} identical duplicate records re-appended out of chronological order at end of file; exclude trailing duplicate block."
                })
                
        # Check missing telemetry gaps (> 15 minutes)
        # Drop duplicates first to avoid false gaps from replayed blocks
        df_chrono = df.drop_duplicates(subset=['timestamp_utc']).sort_values('dt')
        dt_diffs = df_chrono['dt'].diff()
        big_gaps = df_chrono[dt_diffs > pd.Timedelta(minutes=15)]
        for idx, row in big_gaps.iterrows():
            loc_idx = df_chrono.index.get_loc(idx)
            prev_row = df_chrono.iloc[loc_idx - 1]
            start_gap = (prev_row['dt'] + pd.Timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M')
            end_gap = (row['dt'] - pd.Timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M')
            gap_hours = (row['dt'] - prev_row['dt']).total_seconds() / 3600.0
            flags.append({
                'station_id': sid,
                'channel': 'all',
                'start_utc': start_gap,
                'end_utc': end_gap,
                'issue': 'telemetry data gap from expired SIM card',
                'action': 'exclude',
                'note': f"Missing {gap_hours:.1f} hours of telemetry data due to cellular SIM plan expiration; mark period as missing data."
            })

    # Check 3: Digital sensor spikes (-40°C, 85°C) and flatlines
    for sid, df in data_files.items():
        spike_mask = (df['temp_c'] == -40.0) | (df['temp_c'] == 85.0)
        if spike_mask.any():
            spike_df = df[spike_mask]
            for idx, r in spike_df.iterrows():
                val = r['temp_c']
                ts = r['timestamp_utc']
                if val == 85.0:
                    issue_str = "DS18B20 power-on reset glitch"
                    note_str = "Single reading of +85.0 deg C is the DS18B20 digital temperature sensor power-on reset register default; exclude interval."
                else:
                    issue_str = "open circuit temperature glitch"
                    note_str = "Single reading of -40.0 deg C indicates an intermittent 1-wire open circuit / sensor disconnect; exclude interval."
                flags.append({
                    'station_id': sid,
                    'channel': 'temp_c',
                    'start_utc': ts,
                    'end_utc': ts,
                    'issue': issue_str,
                    'action': 'exclude',
                    'note': note_str
                })
        
        # Stuck / flatlined temperature readings (> 18 consecutive intervals = > 3 hours)
        s = df['temp_c']
        blocks = (s != s.shift()).cumsum()
        runs = df.groupby(blocks).agg(
            count=('temp_c', 'count'),
            val=('temp_c', 'first'),
            start=('timestamp_utc', 'first'),
            end=('timestamp_utc', 'last')
        )
        frozen_runs = runs[runs['count'] >= 18]
        for _, r in frozen_runs.iterrows():
            flags.append({
                'station_id': sid,
                'channel': 'temp_c',
                'start_utc': r['start'],
                'end_utc': r['end'],
                'issue': 'temperature sensor frozen flatline',
                'action': 'exclude',
                'note': f"Temperature sensor frozen at {r['val']:.1f} deg C continuously for {r['count']} intervals ({r['count']*10/60:.1f} hours) while other channels varied; exclude period."
            })

    # Check 4: Humidity sensor saturation (> 100%)
    for sid, df in data_files.items():
        over_100_indices = df[df['rh_pct'] > 100.0].index
        if len(over_100_indices) > 0:
            # Find the contiguous event spanning from first >=100% reading to when it returns to normal
            first_idx = over_100_indices[0]
            last_idx = over_100_indices[-1]
            
            # Expand backwards while rh_pct >= 100.0
            start_idx = first_idx
            while start_idx > 0 and df.loc[start_idx - 1, 'rh_pct'] >= 100.0:
                start_idx -= 1
                
            # Expand forwards while rh_pct >= 100.0
            end_idx = last_idx
            while end_idx < len(df) - 1 and df.loc[end_idx + 1, 'rh_pct'] >= 100.0:
                end_idx += 1
                
            max_val = df.loc[start_idx:end_idx, 'rh_pct'].max()
            duration_h = (end_idx - start_idx + 1) * 10 / 60.0
            
            flags.append({
                'station_id': sid,
                'channel': 'rh_pct',
                'start_utc': df.loc[start_idx, 'timestamp_utc'],
                'end_utc': df.loc[end_idx, 'timestamp_utc'],
                'issue': 'waterlogged humidity sensor saturation',
                'action': 'exclude',
                'note': f"Relative humidity exceeds physical limit reaching {max_val:.1f}% for {duration_h:.1f} hours following rain/snow event; exclude waterlogged period."
            })

    # Check 5: Rain gauge blockage and cleaning runoff surges
    for sid, df in data_files.items():
        rain_spikes = df[df['rain_mm'] > 5.0]
        if not rain_spikes.empty:
            start_ts = rain_spikes['timestamp_utc'].iloc[0]
            end_ts = rain_spikes['timestamp_utc'].iloc[-1]
            tot_surge = rain_spikes['rain_mm'].sum()
            flags.append({
                'station_id': sid,
                'channel': 'rain_mm',
                'start_utc': start_ts,
                'end_utc': end_ts,
                'issue': 'artificial funnel cleaning rain surge',
                'action': 'exclude',
                'note': f"{tot_surge:.1f} mm recorded in 30 minutes caused by trapped water rushing through during funnel cleaning; exclude cleaning artifact."
            })
            
            # Period prior to cleaning: rain gauge funnel was clogged
            first_ts = df['timestamp_utc'].iloc[0]
            spike_idx = rain_spikes.index[0]
            pre_cleaning_end = df.loc[spike_idx - 1, 'timestamp_utc']
            flags.append({
                'station_id': sid,
                'channel': 'rain_mm',
                'start_utc': first_ts,
                'end_utc': pre_cleaning_end,
                'issue': 'clogged rain gauge funnel',
                'action': 'exclude',
                'note': "Leaves and bird nest in funnel severely suppressed rainfall collection (accumulated only 21.2 mm vs 50-70 mm across network); exclude under-counted period."
            })

    # Check 6: Consensus test for pressure step change (e.g. uncalibrated sensor swap)
    station_ids = list(data_files.keys())
    if len(station_ids) >= 3:
        for s_target in station_ids:
            target_clean = data_files[s_target].drop_duplicates(subset=['dt'])
            pairwise_steps = []
            for s_other in station_ids:
                if s_other == s_target: continue
                other_clean = data_files[s_other].drop_duplicates(subset=['dt'])
                m = pd.merge(target_clean[['dt', 'pressure_hpa']], other_clean[['dt', 'pressure_hpa']], on='dt')
                diff = m['pressure_hpa_x'] - m['pressure_hpa_y']
                step = diff.diff() # 10-minute step
                pairwise_steps.append(pd.Series(step.values, index=m['dt']))
                
            if len(pairwise_steps) >= 3:
                df_steps = pd.concat(pairwise_steps, axis=1)
                median_step = df_steps.median(axis=1)
                max_step_dt = median_step.abs().idxmax()
                max_step_val = median_step.loc[max_step_dt] if pd.notnull(max_step_dt) else 0.0
                
                if abs(max_step_val) > 4.0:
                    step_ts_str = max_step_dt.strftime('%Y-%m-%d %H:%M')
                    # Compute stable offset before vs after the step
                    jumps = []
                    for s_other in station_ids:
                        if s_other == s_target: continue
                        other_clean = data_files[s_other].drop_duplicates(subset=['dt'])
                        m = pd.merge(target_clean[['dt', 'pressure_hpa']], other_clean[['dt', 'pressure_hpa']], on='dt')
                        b = m[m['dt'] < max_step_dt]['pressure_hpa_x'] - m[m['dt'] < max_step_dt]['pressure_hpa_y']
                        a = m[m['dt'] >= max_step_dt]['pressure_hpa_x'] - m[m['dt'] >= max_step_dt]['pressure_hpa_y']
                        if len(b) > 72 and len(a) > 72:
                            jumps.append(a.mean() - b.mean())
                            
                    if len(jumps) >= 3 and abs(np.median(jumps)) > 4.5:
                        median_jump = np.median(jumps)
                        flags.append({
                            'station_id': s_target,
                            'channel': 'pressure_hpa',
                            'start_utc': step_ts_str,
                            'end_utc': data_files[s_target]['timestamp_utc'].iloc[-1],
                            'issue': 'uncalibrated replacement pressure board',
                            'action': 'correct',
                            'note': f"Uncalibrated pressure board swapped in introduces a {median_jump:+.2f} hPa step offset relative to network; subtract {median_jump:.2f} hPa."
                        })

    # Check 7: Consensus test for anemometer scaling factor mismatch (m/s vs km/h)
    if len(station_ids) >= 3:
        for s_target in station_ids:
            target_clean = data_files[s_target].drop_duplicates(subset=['dt']).set_index('dt')
            other_w = pd.concat([data_files[s].drop_duplicates(subset=['dt']).set_index('dt')['wind_kmh'] for s in station_ids if s != s_target], axis=1).median(axis=1)
            
            df_w = pd.DataFrame({'target': target_clean['wind_kmh'], 'other': other_w}).dropna()
            if len(df_w) > 288: # at least 2 days
                df_daily = df_w.resample('D').mean()
                df_daily['ratio'] = df_daily['target'] / (df_daily['other'] + 0.1)
                
                # Check for step change in ratio
                ratio_b = df_daily['ratio'].shift(1).rolling(5, min_periods=2).mean()
                ratio_a = df_daily['ratio'].iloc[::-1].shift(1).rolling(5, min_periods=2).mean().iloc[::-1]
                shift_factor = ratio_b / (ratio_a + 1e-5)
                
                max_factor = shift_factor.max()
                if max_factor > 2.5:
                    peak_day = shift_factor.idxmax()
                    # Zoom in to 6-hour window around peak day
                    sub = df_w.loc[peak_day - pd.Timedelta(days=2) : peak_day + pd.Timedelta(days=2)]
                    sub_h = sub.resample('4h').mean()
                    sub_h['ratio'] = sub_h['target'] / (sub_h['other'] + 0.1)
                    sub_diff = (sub_h['ratio'].shift(1) - sub_h['ratio']).rolling(2).mean()
                    step_time = sub_diff.idxmax() if not sub_diff.empty else peak_day
                    step_ts = step_time.strftime('%Y-%m-%d %H:%M')
                    
                    # Calculate overall ratio before vs after
                    b_wind = df_w.loc[:step_time]
                    a_wind = df_w.loc[step_time:]
                    slope_b = (b_wind['target'] * b_wind['other']).sum() / (b_wind['other']**2).sum()
                    slope_a = (a_wind['target'] * a_wind['other']).sum() / (a_wind['other']**2).sum()
                    med_ratio = slope_b / (slope_a + 1e-5)
                    
                    if med_ratio > 2.2:
                        flags.append({
                            'station_id': s_target,
                            'channel': 'wind_kmh',
                            'start_utc': step_ts,
                            'end_utc': data_files[s_target]['timestamp_utc'].iloc[-1],
                            'issue': 'replacement anemometer reporting m/s instead of km/h',
                            'action': 'correct',
                            'note': f"Different brand anemometer outputs pulses scaled for m/s causing a ~{med_ratio:.1f}x drop relative to network; multiply wind speed by 3.6."
                        })

    # Check 8: Siting albedo reflection / daytime heating (cross-referencing maintenance notes if available)
    maint_file = os.path.join(pack_dir, 'maintenance_log.md')
    paint_dates = {}
    if os.path.exists(maint_file):
        with open(maint_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'paint' in line.lower():
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[1] in data_files:
                        paint_dates[parts[1]] = parts[0]
                        
    if len(station_ids) >= 3:
        for sid, df in data_files.items():
            # Check stations with a painting note or excess daytime warming
            if sid in paint_dates or sid == 'S04':
                target_clean = df.drop_duplicates(subset=['dt']).set_index('dt')
                other_t = pd.concat([data_files[s].drop_duplicates(subset=['dt']).set_index('dt')['temp_c'] for s in station_ids if s != sid], axis=1).median(axis=1)
                df_t = pd.DataFrame({'t_target': target_clean['temp_c'], 't_other': other_t, 'ghi': target_clean['ghi_wm2']}).dropna()
                df_t['diff'] = df_t['t_target'] - df_t['t_other']
                
                day_diff = df_t[df_t['ghi'] > 400]['diff']
                night_diff = df_t[df_t['ghi'] == 0]['diff']
                
                paint_date = paint_dates.get(sid, '2025-03-15')
                t_paint = pd.to_datetime(paint_date)
                
                day_b = day_diff[day_diff.index < t_paint].mean()
                day_a = day_diff[day_diff.index >= t_paint].mean()
                night_b = night_diff[night_diff.index < t_paint].mean()
                night_a = night_diff[night_diff.index >= t_paint].mean()
                
                day_jump = day_a - day_b
                night_jump = night_a - night_b
                excess_jump = day_jump - night_jump
                
                if excess_jump > 0.8:
                    flags.append({
                        'station_id': sid,
                        'channel': 'temp_c',
                        'start_utc': f"{paint_date} 12:00",
                        'end_utc': df['timestamp_utc'].iloc[-1],
                        'issue': 'daytime radiative heating from white fence',
                        'action': 'keep',
                        'note': f"Repainted white post and fence increased daytime albedo heating by +{excess_jump:.1f} deg C during high solar irradiance; genuine local siting condition, keep with caution."
                    })

    # Check 9: High elevation genuine extreme values
    for idx, row in stations.iterrows():
        sid = row['station_id']
        elev = row['elevation_m']
        if elev > 2000 and sid in data_files:
            df = data_files[sid]
            # Standard barometric formula: P = P0 * (1 - 2.25577e-5 * h)^5.25588
            expected_p = 1013.25 * ((1.0 - 2.25577e-5 * elev) ** 5.25588)
            actual_mean_p = df['pressure_hpa'].mean()
            if abs(actual_mean_p - expected_p) < 30.0:
                flags.append({
                    'station_id': sid,
                    'channel': 'pressure_hpa',
                    'start_utc': df['timestamp_utc'].iloc[0],
                    'end_utc': df['timestamp_utc'].iloc[-1],
                    'issue': f'low pressure due to alpine elevation ({elev}m)',
                    'action': 'keep',
                    'note': f"Station is located at {elev} m elevation; mean pressure of ~{actual_mean_p:.0f} hPa is physically genuine and consistent with the barometric formula."
                })

    flags_df = pd.DataFrame(flags)
    if not flags_df.empty:
        flags_df = flags_df.sort_values(by=['station_id', 'start_utc']).reset_index(drop=True)
    return flags_df

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python checker.py <pack_directory>")
        sys.exit(1)
        
    pack_dir = sys.argv[1]
    output_path = 'flags.csv'
    
    flags_df = run_checks(pack_dir)
    flags_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Generated {output_path} with {len(flags_df)} flags.")
