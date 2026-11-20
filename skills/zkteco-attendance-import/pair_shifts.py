#!/usr/bin/env python3
"""Pair ZKTeco "First & Last" punches into shifts and build an attendance grid.

Usage:
  python3 -I pair_shifts.py EXPORT.csv|EXPORT.xlsx --start YYYY-MM-DD --end YYYY-MM-DD
                            [--rest REST.csv] [--out DIR]
                            [--min-hours 3] [--max-hours 17] [--target-hours 9]
                            [--day-ids 101,104] [--night-from 17]

EXPORT  ZKTeco First & Last report. Header row is found automatically (the row
        containing "Employee ID"). Needed columns: Employee ID, Date (dd-mm-yyyy),
        First Punch, Last Punch. Optional: First Name, Department.
REST    CSV with columns emp_id,rest_weekday (Mon..Sun). Optional.

Writes to DIR (default ./attendance_out):
  shifts.csv     one row per paired shift (credited to the start date)
  grid.csv       one row per employee, one column per day, codes + totals
  to_verify.csv  everything HR must decide: unpaired punches, unknown rest days,
                 rest sheets that look out of date, double shifts

Day codes: P present, R rest, A absent, ? unpaired punch (not counted),
R/A? no punch and no rest day on file (HR decides).
xlsx input needs openpyxl; csv needs nothing.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
CODES = ["P", "R", "A", "?", "R/A?"]
UNPAIRED = 8  # cost of leaving a mid-cycle punch unpaired, in hours of deviation


def read_rows(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        try:
            import openpyxl
        except ImportError:
            sys.exit("xlsx input needs openpyxl: pip install openpyxl (or export as csv)")
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        rows = [["" if v is None else v for v in r] for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
    for i, r in enumerate(rows):
        if any(str(c).strip().lower() == "employee id" for c in r):
            header = [str(c).strip().lower() for c in r]
            return header, rows[i + 1:]
    sys.exit("No header row with 'Employee ID' found")


def parse_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_time(v):
    if v in ("", None):
        return None
    if hasattr(v, "hour"):
        return v.hour * 60 + v.minute
    s = str(v).strip()
    if not s or s in ("-", "--"):
        return None
    parts = s.split(":")
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--rest")
    ap.add_argument("--out", default="attendance_out")
    ap.add_argument("--min-hours", type=float, default=3)
    ap.add_argument("--max-hours", type=float, default=17)
    ap.add_argument("--target-hours", type=float, default=9,
                    help="usual shift length; used to choose between possible pairings")
    ap.add_argument("--day-ids", default="",
                    help="comma-separated employee IDs known to work day shifts only")
    ap.add_argument("--night-from", type=int, default=17,
                    help="unpaired punch on the last day at or after this hour counts as a night shift")
    a = ap.parse_args()

    day_ids = {x.strip() for x in a.day_ids.split(",") if x.strip()}
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    days = [start + timedelta(d) for d in range((end - start).days + 1)]
    header, rows = read_rows(a.export)

    def col(*names):
        for n in names:
            if n in header:
                return header.index(n)
        return None

    c_id, c_date = col("employee id"), col("date")
    c_first, c_last = col("first punch"), col("last punch")
    c_name, c_dept = col("first name", "name"), col("department")
    if None in (c_id, c_date, c_first, c_last):
        sys.exit(f"Missing columns. Found: {header}")

    punches = defaultdict(list)
    info = {}
    seen_days = defaultdict(set)
    for r in rows:
        if len(r) <= max(c_id, c_date, c_first, c_last) or str(r[c_id]).strip() == "":
            continue
        emp = str(r[c_id]).strip()
        d = parse_date(r[c_date])
        if d is None:
            continue
        if d in seen_days[emp]:
            print(f"warning: duplicate row for {emp} on {d} (overlapping exports?)", file=sys.stderr)
        seen_days[emp].add(d)
        info.setdefault(emp, (str(r[c_name]).strip() if c_name is not None else "",
                              str(r[c_dept]).strip() if c_dept is not None else ""))
        for t in (parse_time(r[c_first]), parse_time(r[c_last])):
            if t is not None:
                punches[emp].append(datetime(d.year, d.month, d.day) + timedelta(minutes=t))

    rest = {}
    if a.rest:
        with open(a.rest, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                wd = r["rest_weekday"].strip()[:3].title()
                if wd not in WEEKDAYS:
                    sys.exit(f"bad rest_weekday {r['rest_weekday']!r} for {r['emp_id']}")
                rest[r["emp_id"].strip()] = WEEKDAYS.index(wd)

    os.makedirs(a.out, exist_ok=True)
    shifts_out, verify, grid = [], [], []
    lo, hi = timedelta(hours=a.min_hours), timedelta(hours=a.max_hours)

    for emp in sorted(info, key=lambda e: (len(e), e)):
        ps = sorted(set(punches[emp]))
        deduped = []
        for p in ps:  # same punch twice within 5 minutes = one punch
            if deduped and p - deduped[-1] < timedelta(minutes=5):
                continue
            deduped.append(p)
        credited = defaultdict(int)
        unpaired = defaultdict(list)

        # Choose the pairing with the lowest total cost, not the first pair that fits.
        # A greedy pass pairs a night worker's 05:00 punch with the same day's 20:00
        # punch (15 h) and gets every shift wrong. Costs: a pair costs how far its
        # length is from --target-hours; a punch left unpaired mid-cycle costs
        # UNPAIRED; a punch explained by a cycle-edge rule costs nothing.
        def edge(p):
            if emp in day_ids:
                return None
            if p.date() == start and p.hour < 12:
                return "first"
            if p.date() == end and p.hour >= a.night_from:
                return "last"
            return None

        n = len(deduped)
        best = [0.0] * (n + 2)
        choice = [None] * (n + 1)
        for i in range(n - 1, -1, -1):
            best[i] = (0 if edge(deduped[i]) else UNPAIRED) + best[i + 1]
            choice[i] = "single"
            if i + 1 < n:
                gap = deduped[i + 1] - deduped[i]
                if lo <= gap <= hi:
                    c = abs(gap.total_seconds() / 3600 - a.target_hours) + best[i + 2]
                    if c < best[i]:
                        best[i], choice[i] = c, "pair"
        i = 0
        while i < n:
            p = deduped[i]
            if choice[i] == "pair":
                q = deduped[i + 1]
                credited[p.date()] += 1
                shifts_out.append([emp, p.isoformat(sep=" ", timespec="minutes"),
                                   q.isoformat(sep=" ", timespec="minutes"),
                                   round((q - p).total_seconds() / 3600, 2), p.date().isoformat()])
                i += 2
                continue
            d = p.date()
            if edge(p) == "first":
                # ends the previous cycle's night shift: not counted, but shown to HR
                verify.append([emp, d.isoformat(), "morning-only punch on first day: treated as end of last cycle's night shift, not counted", p.strftime("%H:%M")])
            elif edge(p) == "last":
                credited[d] += 1  # night shift that ends in the next cycle
                shifts_out.append([emp, p.isoformat(sep=" ", timespec="minutes"), "next cycle", "", d.isoformat()])
            else:
                unpaired[d].append(p.strftime("%H:%M"))
            i += 1

        # First & Last data cannot tell a 08:00-20:00 day worker from a 20:00-08:00
        # night worker. If most shifts are overnight but same-day spans fit the
        # target just as well, say so instead of guessing silently.
        mine = [r for r in shifts_out if r[0] == emp and r[3] != ""]
        overnight = [r for r in mine if r[1][:10] != r[2][:10]]
        if mine and len(overnight) * 2 > len(mine):
            by_day = defaultdict(list)
            for p in deduped:
                by_day[p.date()].append(p)
            night_dev = sum(abs(r[3] - a.target_hours) for r in overnight) / len(overnight)
            fits = 0
            for ps_ in by_day.values():
                span = ps_[-1] - ps_[0]
                if lo <= span <= hi and abs(span.total_seconds() / 3600 - a.target_hours) <= night_dev + 1:
                    fits += 1
            if fits * 5 >= len(by_day) * 4:
                verify.append([emp, "", "paired as night shifts, but the same punches also fit day shifts: confirm the shift with HR (use --day-ids to force day shifts)", ""])

        codes, rest_punch, rest_total = [], 0, 0
        for d in days:
            is_rest = emp in rest and d.weekday() == rest[emp]
            rest_total += is_rest
            if credited[d]:
                codes.append("P")
                rest_punch += is_rest
                if credited[d] > 1:
                    verify.append([emp, d.isoformat(), "two shifts credited to one day", ""])
            elif unpaired[d]:
                codes.append("?")
                verify.append([emp, d.isoformat(), "unpaired punch", " ".join(unpaired[d])])
            elif emp not in rest:
                codes.append("R/A?")
            else:
                codes.append("R" if is_rest else "A")
        if emp not in rest:
            verify.append([emp, "", "no rest day on file: no-punch days marked R/A?", ""])
        elif rest_total and rest_punch * 2 >= rest_total:
            verify.append([emp, "", f"punched on {rest_punch} of {rest_total} listed rest days: rest sheet may be out of date", ""])
        name, dept = info[emp]
        grid.append([emp, name, dept] + codes + [codes.count(c) for c in CODES])

    with open(os.path.join(a.out, "shifts.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["emp_id", "start", "end", "hours", "credited_date"])
        w.writerows(shifts_out)
    with open(os.path.join(a.out, "grid.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["emp_id", "name", "department"] + [d.isoformat() for d in days] + CODES)
        w.writerows(grid)
    with open(os.path.join(a.out, "to_verify.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["emp_id", "date", "issue", "punches"])
        w.writerows(verify)

    print(f"cycle {start} to {end}: {len(days)} days, {len(grid)} employees, "
          f"{len(shifts_out)} shifts, {len(verify)} items to verify")
    for row in grid:
        print(f"  {row[0]:>6}  " + "  ".join(f"{c}={n}" for c, n in zip(CODES, row[-len(CODES):])))
    print(f"written to {a.out}/")


if __name__ == "__main__":
    main()
