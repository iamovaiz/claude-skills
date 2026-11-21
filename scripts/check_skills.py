#!/usr/bin/env python3
"""Repo checks run in CI: skill frontmatter, scripts compile, examples behave."""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []

for skill in sorted((ROOT / "skills").iterdir()):
    if not skill.is_dir():
        continue
    md = skill / "SKILL.md"
    if not md.exists():
        errors.append(f"{skill.name}: missing SKILL.md"); continue
    m = re.match(r"---\nname: (\S+)\ndescription: (.+?)\n---\n", md.read_text(encoding="utf-8"), re.S)
    if not m:
        errors.append(f"{skill.name}: bad frontmatter"); continue
    name, desc = m.groups()
    if name != skill.name:
        errors.append(f"{skill.name}: name '{name}' does not match folder")
    if len(desc) > 1024 or "<" in desc or ">" in desc:
        errors.append(f"{skill.name}: description too long or has angle brackets")
    if not (skill / "README.md").exists():
        errors.append(f"{skill.name}: missing README.md")
    for f in list(skill.rglob("*.md")):
        if "—" in f.read_text(encoding="utf-8"):
            errors.append(f"{f.relative_to(ROOT)}: contains an em dash")
    print(f"ok  {skill.name}")

def run(args, expect):
    r = subprocess.run([sys.executable, "-I", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != expect:
        errors.append(f"{' '.join(args)}: exit {r.returncode}, expected {expect}\n{r.stdout}{r.stderr}")

pc = "skills/post-check/"
run([pc + "postcheck.py", pc + "examples/bad-post.txt", "--offlimits", pc + "offlimits.example.txt"], 1)
run([pc + "postcheck.py", pc + "examples/good-post.txt", "--offlimits", pc + "offlimits.example.txt"], 0)
z = "skills/zkteco-attendance-import/"
run([z + "pair_shifts.py", z + "examples/first_last_sample.csv", "--start", "2026-01-26", "--end", "2026-02-25",
     "--rest", z + "examples/rest_days_sample.csv", "--out", "/tmp/zk_check"], 0)
grid = pathlib.Path("/tmp/zk_check/grid.csv").read_text().splitlines()
if not any(l.startswith("102,") and l.endswith(",30,1,0,0,0") for l in grid):
    errors.append("zkteco: night worker 102 should be P=30 R=1")
for f in ROOT.glob("skills/*/*.py"):
    run(["-m", "py_compile", str(f.relative_to(ROOT))], 0)

if errors:
    print("\n".join("FAIL " + e for e in errors)); sys.exit(1)
print("all checks passed")
