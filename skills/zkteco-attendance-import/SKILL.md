---
name: zkteco-attendance-import
description: Turn ZKTeco fingerprint-machine exports (First & Last report) into a monthly attendance sheet - pair punches into day and night shifts, apply rest days, list what HR must verify, and optionally load the result into a database with backups. Use when the user shares ZKTeco or biometric attendance exports and asks to compile, check or import attendance.
---

# zkteco-attendance-import

ZKTeco machines export a "First & Last" report: one row per person per day with the first and last punch. That shape breaks on night shifts. A worker who clocks in at 20:00 and out at 05:00 shows up as two half-days, and a naive "punched today = present" rule counts them wrong. This skill pairs punches into real shifts, credits each shift to the day it started, and puts every unclear case in a list for HR instead of guessing.

## Working rules

- Ask before any choice that changes pay: the cycle dates, the shift-length window, how unpaired punches count. Flag problems before building anything.
- Never invent attendance. A day with one punch is `?` for HR, not P.
- If you load data into a database, the user runs every write. You prepare SQL and read the results.
- Example and test data must be invented. Never put real employee names, IDs or punch times in a repo, a test or a demo.

## Inputs

1. The First & Last export(s) for the whole pay cycle, as csv or xlsx. Columns: Employee ID, First Name, Department, Date (dd-mm-yyyy), First Punch, Last Punch. The header row is found automatically. If the cycle is split across exports, merge them; the script warns about duplicate days.
2. Rest-day sheets per department, if they exist (one fixed weekday per person).
3. The employee master list (ID on the machine, employee code, name, father's name, department, status, exit date), read-only.
4. Cycle start and end dates (for example 26th to 25th).

## Method

1. **Profile the export.** Date range, number of IDs, rows with a single punch (Total Time 00:00), IDs on the machine that are not in the employee master and the reverse.
2. **Rest sheets to `rest.csv`** (`emp_id,rest_weekday`). Sheets often have names but no codes. Match names within the same department: full token match first, then a spelling-tolerant match (compare the consonants). Mark first-name-only matches "verify". Resolve ambiguous names by elimination, otherwise list them for HR. Re-check unmatched names against the employee master, because old machine IDs are often merged into new codes. Never assume Sunday is the rest day for production or security staff.
3. **Pair shifts:**

   ```
   python3 -I pair_shifts.py export.csv --start 2026-01-26 --end 2026-02-25 --rest rest.csv --out out/
   ```

   The script picks the pairing with the lowest total cost across the cycle, not the first pair that fits. A pair must be 3 to 17 hours long (`--min-hours`, `--max-hours`) and costs its distance from the usual shift length (`--target-hours`, default 9). This matters: a first-fit pass pairs a night worker's 05:00 punch with the same day's 20:00 punch and gets every shift wrong.

   Cycle-edge rules: a morning-only punch on the first day ends last cycle's night shift (not counted, listed for HR). A punch at or after 17:00 on the last day starts a night shift that ends next cycle (counted P).

4. **Read `to_verify.csv` with the user.** It lists unpaired punches, people with no rest day on file, rest sheets that look out of date (punched on half or more of their listed rest days; rest days often rotate, so a sheet is a snapshot), double shifts, and people whose punches fit day shifts as well as night shifts. First & Last data cannot tell a 08:00-20:00 day worker from a 20:00-08:00 night worker. Ask HR, then re-run with `--day-ids` for confirmed day workers.
5. **Build the workbook** with openpyxl, Arial: the grid from `grid.csv` with COUNTIF totals, a To verify tab, a Rest-sheet matching tab, and a Method tab that states the rules used. In COUNTIF, `?` is a wildcard: count it with `"~?"` and `"R/A~?"`. Recalculate and check each row's totals against the script's counts before sending.
6. **HR documents** as separate PDFs (A4, dark lines that print on black-and-white printers, signature lines, created date and time on each page): the rest-day request with weekly columns, the name-matching list, the discrepancy list. One task per file.

Day codes: `P` present, `R` rest, `A` absent, `?` unpaired punch, `R/A?` no punch and no rest day on file.

## Optional: load into a database

Only if the user has an HR system with an attendance table. Adapt table and column names to theirs; these are placeholders.

1. Map machine IDs to employees, and check that no machine ID maps to more than one employee before going further.
2. Stage the shifts: `create table att_stage_YYYYMM (machine_id text, d date, first_punch time, last_punch time, hours numeric);` with row-level security on. Show the staged count.
3. Read-only preview: unmatched IDs, people who left before the date (status or exit date), days that already have an entry, rows that will be inserted. If the numbers differ from what you expected, list the people before inserting.
4. Back up the cycle (`create table attendance_bak_YYYYMM as select ...`), then insert `Present` rows with a `not exists` guard. Never overwrite rows HR entered by hand, such as leave.
5. Count by status and the backup row count in one final query. "Success. No rows returned" is not proof.
6. Same pattern for rest days. Drop staging tables only after HR's decisions are loaded.

Label every SQL block with the database it is for (PRODUCTION or STAGING plus the project name), and run it on staging or a local copy first.

## Failure modes seen

- Re-running a step that creates a backup table fails with "relation already exists" (42P07). Check what exists with a read-only query before retrying.
- New employee codes that were never enrolled on older machines show no punches at all; check enrollment before marking them absent.
- Files attached in one chat do not carry over to another. Ask for them again.
- Pairing gives fewer present days than an "any punch that day" rule. If HR enters override days by hand, they must use the same counting.

## Files

- `pair_shifts.py`: the pairing script. Standard library only; xlsx input needs openpyxl.
- `examples/first_last_sample.csv`, `examples/rest_days_sample.csv`: invented data with a day worker, a night worker, a missed punch-out, an out-of-date rest sheet and a person with no rest day on file.

## Outputs

`shifts.csv`, `grid.csv`, `to_verify.csv`, then the workbook, the HR PDFs and, if used, numbered SQL files with the verified counts.
