# I AM OVAIZ skills

Claude skills taken from real business systems: an HR and payroll system for a factory, client e-commerce stores, and the release work behind them. Each one exists because something went wrong without it.

Built for people who run their business systems by directing Claude Code rather than writing every line themselves.

## Skills

| Skill | What it does | Scripts |
|---|---|---|
| [post-check](skills/post-check) | Checks a LinkedIn or X post before you publish it: em dashes, invisible characters, stray `,.`, placeholders, AI-sounding words, claims you ruled out | `postcheck.py` |
| [zkteco-attendance-import](skills/zkteco-attendance-import) | Turns ZKTeco fingerprint-machine exports into a monthly attendance sheet, pairing night shifts correctly and listing what HR must check | `pair_shifts.py` |
| [staged-release-supabase-vercel](skills/staged-release-supabase-vercel) | Ships a change through staging to production on Supabase and Vercel, and proves the live site serves it | `served_version.py` |
| [supabase-vercel-ops-checks](skills/supabase-vercel-ops-checks) | Setup and health checklist for Supabase and Vercel apps, including the failures that look like success | none |
| [project-board-sync](skills/project-board-sync) | Reads the project board before work and suggests step closures, with evidence, after it | template |

All scripts use the Python standard library only (`pair_shifts.py` needs `openpyxl` for xlsx input). None of them call a network service except `served_version.py`, which fetches the URL you give it.

## Install

**Claude Code:** copy a skill folder into `~/.claude/skills/` (all projects) or `.claude/skills/` in one repo.

```
git clone https://github.com/iamovaiz/skills.git
cp -r skills/skills/post-check ~/.claude/skills/
```

**Claude apps:** zip one skill folder and upload it under Settings, Capabilities, Skills.

## Try one in a minute

```
cd skills/post-check
python3 postcheck.py examples/bad-post.txt
python3 postcheck.py examples/good-post.txt
```

## Contributing

Issues and pull requests are welcome. Test data must be invented: no real names, employee IDs, client names or project refs.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). You can use, change and redistribute these skills, including commercially. Keep the LICENSE and NOTICE files with any copy.

The license covers the code and text in this repo. It does not give permission to use the "I AM OVAIZ" name, the OV logo or other I AM OVAIZ branding, except to say where the skills came from.

Made by [I AM OVAIZ](https://iamovaiz.com). We build business systems for factories, retailers and e-commerce operators.
