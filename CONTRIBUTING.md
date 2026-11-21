# Contributing

Thanks for helping. A few rules keep this collection useful.

## What belongs here

A skill earns a place when it fixes a problem that actually happened: a broken release, a wrong payroll figure, a post that had to be deleted. Describe that problem in your pull request. Ideas without an incident behind them are welcome as issues, not as skills.

## Skill layout

```
skills/<skill-name>/
  SKILL.md      instructions for Claude, with name and description frontmatter
  README.md     for people: what it does, an example, how to use it
  *.py          optional scripts, Python standard library where possible
  examples/     invented sample data the scripts can run on
```

- `name` in the frontmatter matches the folder name.
- The description says what the skill does and when to use it, in under 1,024 characters.
- Scripts take inputs as arguments, need no network unless that is the point, and exit non-zero on failure.

## Data

Every example must be invented. No real employee names or IDs, client names, emails, API keys, passwords, Supabase refs or domains you don't own. Pull requests with real data are closed, not edited.

## Safety

A skill must never let Claude publish, merge, deploy, delete, spend money or run production SQL without the user's explicit yes in chat, and must never ask the user to paste secrets into the conversation.

## Before you open a pull request

```bash
python scripts/check_skills.py
```

## Writing style

Plain words, short sentences, no em dashes. Say the specific thing. Write it the way you'd explain it to a colleague.

By contributing you agree your work is licensed under the Apache License 2.0.
