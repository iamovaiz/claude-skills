# zkteco-attendance-import: monthly attendance from ZKTeco exports, night shifts included

ZKTeco fingerprint machines export a "First & Last" report: one row per person per day. A night-shift worker who clocks in at 20:00 and out at 05:00 shows up as two half-days, and the usual "punched today means present" rule gets their month wrong.

This skill pairs punches into real shifts, credits each shift to the day it started, applies rest days, and lists every unclear case for HR instead of guessing.

## What you get

```bash
python3 pair_shifts.py examples/first_last_sample.csv \
  --start 2026-01-26 --end 2026-02-25 --rest examples/rest_days_sample.csv
```

```
cycle 2026-01-26 to 2026-02-25: 31 days, 4 employees, 109 shifts, 4 items to verify
     101  P=26  R=4  A=1  ?=0  R/A?=0
     102  P=30  R=1  A=0  ?=0  R/A?=0
     103  P=26  R=4  A=0  ?=1  R/A?=0
     104  P=27  R=0  A=0  ?=0  R/A?=4
```

- `shifts.csv` every paired shift with its hours
- `grid.csv` one row per employee, one column per day: `P` present, `R` rest, `A` absent, `?` unpaired punch, `R/A?` no rest day on file
- `to_verify.csv` what HR must decide: missed punch-outs, rest sheets that look out of date, people whose punches fit day and night shifts equally

## How the pairing works

A shift must be 3 to 17 hours. When several pairings are possible, the script picks the one closest to the usual shift length across the whole month, not the first pair that fits. A first-fit rule pairs a night worker's 05:00 punch with the same day's 20:00 punch and gets every shift wrong; this one doesn't.

First & Last data can't tell a 08:00-20:00 day worker from a 20:00-08:00 night worker. When that happens the script says so, and `--day-ids` lets HR confirm who works days.

## Beyond the script

`SKILL.md` also guides Claude through matching handwritten rest-day sheets to employees, building the Excel workbook (with the COUNTIF wildcard trap for `?`), the HR verification PDFs, and an optional, backed-up database import.

## Files

`pair_shifts.py` (standard library; `.xlsx` input needs openpyxl), `examples/` invented data with a day worker, a night worker, a missed punch-out and an out-of-date rest sheet.
