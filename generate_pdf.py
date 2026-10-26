import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable

def build_pdf():
    pdf_filename = "report.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        spaceAfter=6
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#64748b'),
        alignment=2 # Right aligned
    )
    
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=6,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    card_title_green = ParagraphStyle(
        'CardTG',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#166534')
    )

    card_title_blue = ParagraphStyle(
        'CardTB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1e40af')
    )
    
    table_cell = ParagraphStyle(
        'TCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )

    table_cell_bold = ParagraphStyle(
        'TCellB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0f172a')
    )
    
    badge_green = ParagraphStyle(
        'BGreen',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#15803d')
    )
    badge_amber = ParagraphStyle(
        'BAmber',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#b45309')
    )
    badge_red = ParagraphStyle(
        'BRed',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#b91c1c')
    )

    story = []

    # ------------------ PAGE 1 ------------------
    # Header row: Title left, Meta right
    header_data = [
        [
            Paragraph("<b>Ridgeline Weather Network Health Briefing</b>", title_style),
            Paragraph("<b>Coordinator Action Brief</b><br/>6-Week Audit: Mar 01 – Apr 11, 2025<br/>Prepared for Monday Meeting", meta_style)
        ],
        [
            Paragraph("Spring Climate Summary Decisions & Volunteer Technician Dispatch Plan", subtitle_style),
            Paragraph("", meta_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[370, 153])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=6, spaceBefore=2))

    # Executive Summary Cards
    c1 = [
        Paragraph("<b>✔ Decision 1: Spring Climate Summary</b>", card_title_green),
        Spacer(1, 2),
        Paragraph("<b>88.4% of network data is publication-grade.</b> Saddle Ridge (S01) is 100% sound. Three stations (S02, S06, S07) are fully rescued via mathematical formulas. Corrupted windows at S03 (frozen temp), S04 (clogged rain), and S05 (waterlogged humidity) are isolated and excluded.", body_style)
    ]
    c2 = [
        Paragraph("<b>➔ Decision 2: Technician Dispatch</b>", card_title_blue),
        Spacer(1, 2),
        Paragraph("<b>Dispatch technician to S03 (Valley Library).</b> S03 has an active, recurrent temperature sensor disconnect (-40°C/+85°C spikes and 80-hour freeze). All other station errors are solved in software; S03 cannot and requires physical servicing.", body_style)
    ]
    
    t_cards = Table([[c1, c2]], colWidths=[256, 256])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (0,0), 0.8, colors.HexColor('#86efac')),
        ('BOX', (1,0), (1,0), 0.8, colors.HexColor('#93c5fd')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 6))

    # Section 1 Table
    story.append(Paragraph("<b>Station-by-Station Quality Assessment & Inclusion Rules</b>", sec_title))
    
    table_data = [
        [
            Paragraph("<b>Station</b>", table_cell_bold),
            Paragraph("<b>Elevation / Role</b>", table_cell_bold),
            Paragraph("<b>Summary Status</b>", table_cell_bold),
            Paragraph("<b>What Happened</b>", table_cell_bold),
            Paragraph("<b>Action for Spring Climate Summary</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>S01</b> Saddle Ridge", table_cell),
            Paragraph("2913 m • Alpine Hut", table_cell),
            Paragraph("INCLUDE (100%)", badge_green),
            Paragraph("Extreme cold (-18.7°C) and low pressure (~709 hPa) look unusual but match alpine physics.", table_cell),
            Paragraph("<b>Include all data without changes.</b> Confirmed genuine alpine climate record.", table_cell)
        ],
        [
            Paragraph("<b>S02</b> North Mesa", table_cell),
            Paragraph("1623 m • School", table_cell),
            Paragraph("CORRECT PRESS.", badge_amber),
            Paragraph("Swapped uncalibrated pressure board Mar 21 at 11am local (+6.66 hPa jump).", table_cell),
            Paragraph("<b>Subtract 6.66 hPa</b> from pressure after Mar 21 17:20 UTC. Other channels 100% good.", table_cell)
        ],
        [
            Paragraph("<b>S03</b> Valley Library", table_cell),
            Paragraph("1523 m • Valley Ref.", table_cell),
            Paragraph("TRIM TEMP", badge_red),
            Paragraph("Digital probe glitched (-40°C, +85°C) and froze at 6.5°C for 80 hrs (Mar 18–21).", table_cell),
            Paragraph("<b>Exclude Mar 18 06:00 – Mar 21 14:00 temp</b> and 4 glitch spikes. Rest 100% good.", table_cell)
        ],
        [
            Paragraph("<b>S04</b> Community Gdn", table_cell),
            Paragraph("1763 m • Foothills", table_cell),
            Paragraph("EXCLUDE RAIN", badge_red),
            Paragraph("Funnel clogged with leaves/nest until cleaned Apr 2 (33.4 mm surge). Fence repainted.", table_cell),
            Paragraph("<b>Exclude rainfall prior to Apr 2 16:30.</b> Note subtle daytime fence heating.", table_cell)
        ],
        [
            Paragraph("<b>S05</b> Eastside Rec", table_cell),
            Paragraph("1644 m • Plains Edge", table_cell),
            Paragraph("TRIM RH + META", badge_amber),
            Paragraph("Install sheet had lat typo (39.57 vs 39.754). Humidity saturated >100% after Mar 7 storm.", table_cell),
            Paragraph("<b>Exclude RH from Mar 7 12:00 to Mar 11 00:00.</b> Update latitude to 39.7540° N.", table_cell)
        ],
        [
            Paragraph("<b>S06</b> Fire Station", table_cell),
            Paragraph("1891 m • South Hills", table_cell),
            Paragraph("SHIFT TIMESTAMPS", badge_amber),
            Paragraph("Rebooted to Mountain Time (UTC-6) after battery swap Mar 24; clock ran 6h behind.", table_cell),
            Paragraph("<b>Add 6 hours to timestamps</b> from Mar 24 10:10 onwards. Recovers 100% of data.", table_cell)
        ],
        [
            Paragraph("<b>S07</b> Riverbend Farm", table_cell),
            Paragraph("1525 m • North Valley", table_cell),
            Paragraph("SCALE WIND ×3.6", badge_amber),
            Paragraph("Replacement anemometer fitted Mar 26 outputs pulses in m/s rather than km/h (dropped 3.6×).", table_cell),
            Paragraph("<b>Multiply wind speed by 3.6</b> from Mar 26 15:30 onwards. Completely restores record.", table_cell)
        ],
        [
            Paragraph("<b>S08</b> Plains Grange", table_cell),
            Paragraph("1437 m • East Plains", table_cell),
            Paragraph("DROP DUPLICATE", badge_amber),
            Paragraph("35.8-hr modem blackout Mar 16–18 (SIM expired). Apr 05 data re-appended twice at end.", table_cell),
            Paragraph("<b>Drop trailing duplicate block.</b> Mark Mar 16–18 missing. Remainder is 100% sound.", table_cell)
        ],
    ]
    
    t_status = Table(table_data, colWidths=[65, 75, 75, 145, 163])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')])
    ]))
    story.append(t_status)
    story.append(Spacer(1, 6))

    # Summary Callout Table
    excl_text = Paragraph("<b>Permanently Exclude from Climate Means:</b><br/>"
                          "• S03 Temperature: 80-hour frozen flatline (Mar 18 06:00 – Mar 21 14:00) &amp; 4 spikes<br/>"
                          "• S04 Precipitation: Entire rain record prior to Apr 02 16:30 (clogged funnel + surge)<br/>"
                          "• S05 Humidity: Saturated period (Mar 07 12:00 – Mar 11 00:00, values 100–105%)<br/>"
                          "• S08 Telemetry: Missing SIM blackout gap (Mar 16 13:50 – Mar 18 01:40) &amp; duplicate day", table_cell)
    recov_text = Paragraph("<b>Recovered in Full via Script Formulas:</b><br/>"
                           "• S06 Clocks: Timestamps shifted +6 hours &rarr; 100% complete time-series restored<br/>"
                           "• S07 Wind: Multiplied by 3.6 (m/s &rarr; km/h conversion) &rarr; matches regional baseline<br/>"
                           "• S02 Pressure: Subtracted 6.66 hPa &rarr; barometric elevation curve seamlessly aligned<br/>"
                           "• S05 Coordinates: Corrected install sheet latitude typo to 39.7540° N", table_cell)
    
    t_sum = Table([[excl_text, recov_text]], colWidths=[256, 256])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_sum)

    # Footer Page 1
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=4, spaceBefore=4))
    story.append(Table([[
        Paragraph("Ridgeline Schools Weather Network • Spring Climate Briefing", meta_style),
        Paragraph("Page 1 of 2", meta_style)
    ]], colWidths=[400, 123]))

    # ------------------ PAGE 2 ------------------
    story.append(PageBreak())

    # Header Page 2
    header_data2 = [
        [
            Paragraph("<b>Volunteer Technician Work Order & Dispatch Plan</b>", title_style),
            Paragraph("<b>Mission Plan: Station S03</b><br/>Location: Valley Library<br/>Estimated Time: 45–60 Minutes", meta_style)
        ],
        [
            Paragraph("Where to send our one technician next week • 1-Hour Step-by-Step Task List", subtitle_style),
            Paragraph("", meta_style)
        ]
    ]
    t_header2 = Table(header_data2, colWidths=[370, 153])
    t_header2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header2)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=8, spaceBefore=2))

    # Dispatch Work Order Container
    disp_left = [
        Paragraph("<b>Why S03 and NOT the Second-Best Choice?</b>", ParagraphStyle('H4', parent=table_cell_bold, textColor=colors.HexColor('#1e3a8a'), spaceAfter=3)),
        Paragraph("Every other station's anomaly is <b>mathematically deterministic and already resolved</b>: "
                  "S06 was a fixed clock shift (+6h), S07 was a known unit scale (3.6×), S02 was a static board offset (-6.66 hPa), "
                  "and S04/S08 issues are already past.<br/><br/>"
                  "<b>S03 is the only station with an ACTIVE, RECURRING HARDWARE FAILURE.</b> "
                  "Its digital temperature probe suffered -40°C open-circuit disconnections and +85°C reset defaults on Mar 05, Mar 12, Apr 02, and Apr 08, "
                  "plus an 80-hour total freeze. Software cannot invent missing weather data. If not physically repaired, S03 will continue losing spring data.", body_style),
        Spacer(1, 6),
        Table([[
            Paragraph("<b>What to Check FIRST (Minute 0–10):</b><br/>"
                      "Inspect screw terminals inside the logger enclosure and radiation shield strain relief. "
                      "A loose screw or corroded ground on a 1-wire digital bus produces intermittent disconnects (-40°C) and reset register states (+85°C).", table_cell)
        ]], colWidths=[240], style=[
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e0f2fe')),
            ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor('#7dd3fc')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ])
    ]

    disp_right = [
        Paragraph("<b>1-Hour Field Protocol for the Volunteer</b>", ParagraphStyle('H4', parent=table_cell_bold, textColor=colors.HexColor('#1e3a8a'), spaceAfter=3)),
        Paragraph("<b>1. Min 00–10 (Terminal Inspection):</b> Open enclosure, inspect probe wiring to terminal block. Check for loose strands, moisture ingress, or oxidized contacts. Gently tug each wire.<br/>"
                  "<b>2. Min 10–25 (Sensor Replacement):</b> Swap the Dallas DS18B20 temperature probe with the pre-tested spare from the kit. Tighten screw terminals firmly.<br/>"
                  "<b>3. Min 25–35 (Radiation Shield Check):</b> Check louvers of radiation shield for spider webs or debris that trap heat/moisture against probe. Clean with brush.<br/>"
                  "<b>4. Min 35–50 (Real-Time Diagnostic):</b> Power on logger display. Confirm live temperature updates every 10s and tracks ambient (compare with handheld reference).<br/>"
                  "<b>5. Min 50–60 (Close &amp; Sign-off):</b> Reseal weatherproof grommet with silicone grease, verify logger status LED blinks green, log replacement in notebook.", table_cell),
        Spacer(1, 4),
        Paragraph("<b>Equipment to bring:</b> Small flathead screwdriver, spare DS18B20 probe, handheld reference thermometer, lint-free cloth, desiccant pouch.", table_cell)
    ]

    t_disp = Table([[disp_left, disp_right]], colWidths=[252, 260])
    t_disp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#2563eb')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_disp)
    story.append(Spacer(1, 10))

    # Secondary Backlog Table
    story.append(Paragraph("<b>Secondary Backlog & Remote Resolutions (No Field Visit Required)</b>", sec_title))
    
    backlog_data = [
        [
            Paragraph("<b>Station</b>", table_cell_bold),
            Paragraph("<b>Reported Issue</b>", table_cell_bold),
            Paragraph("<b>Why Remote Fix is Better than a Field Visit</b>", table_cell_bold),
            Paragraph("<b>Action Taken in Data Pipeline</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>S06</b> Fire Station", table_cell),
            Paragraph("Clock 6h behind UTC", table_cell),
            Paragraph("The data is completely sound; a site visit would only take 5 mins to press buttons, but our script resolves all historical data cleanly.", table_cell),
            Paragraph("Next routine battery change will re-sync clock; data corrected via automated +6 hr pipeline rule.", table_cell)
        ],
        [
            Paragraph("<b>S07</b> Riverbend Farm", table_cell),
            Paragraph("Anemometer reads low", table_cell),
            Paragraph("New anemometer is mechanically sound and spinning freely; the only issue is the logger interpreting m/s pulses as km/h.", table_cell),
            Paragraph("Scaled by factor of 3.6 in data ingestion. Next site visit can update logger firmware pulse constant.", table_cell)
        ],
        [
            Paragraph("<b>S02</b> North Mesa", table_cell),
            Paragraph("Pressure +6.66 hPa high", table_cell),
            Paragraph("Uncalibrated spare board has a steady, pure linear offset. A site visit without a high-precision lab calibrator cannot fix it on-site.", table_cell),
            Paragraph("Subtracted static 6.66 hPa offset in software. When calibration kit is available later this summer, calibrate properly.", table_cell)
        ],
        [
            Paragraph("<b>S04</b> Community Gdn", table_cell),
            Paragraph("Rain blockage &amp; painted post", table_cell),
            Paragraph("Funnel was already cleared by volunteer on Apr 2. Post repaint is permanent; daytime solar reflection is noted in metadata.", table_cell),
            Paragraph("Excluded invalid historical rain; current rain gauge is working. Siting note added to annual report.", table_cell)
        ],
    ]
    
    t_backlog = Table(backlog_data, colWidths=[70, 95, 175, 183])
    t_backlog.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')])
    ]))
    story.append(t_backlog)
    story.append(Spacer(1, 8))

    # Guidance Callout Box
    g_text = Paragraph("<b>Guidance for the Coordinator at Monday's Meeting:</b><br/>"
                       "You can confidently reassure the school committee that our network data is sound and defensible. "
                       "By applying these precise mathematical adjustments, we preserve over 95% of the spring weather history without sweeping flawed data under the rug. "
                       "Sending our volunteer to S03 protects our upcoming summer dataset before severe heatwaves begin.", body_style)
    t_g = Table([[g_text]], colWidths=[523])
    t_g.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#16a34a')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_g)

    # Footer Page 2
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=4, spaceBefore=4))
    story.append(Table([[
        Paragraph("Ridgeline Schools Weather Network • Spring Climate Briefing", meta_style),
        Paragraph("Page 2 of 2", meta_style)
    ]], colWidths=[400, 123]))

    doc.build(story)
    print("Successfully built report.pdf")

if __name__ == '__main__':
    build_pdf()
