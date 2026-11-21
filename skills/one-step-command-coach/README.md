# one-step-command-coach: for people who run the commands an AI gives them

You don't write the code. You paste what Claude gives you into a terminal, into Claude Code, into a database editor. It works, until a command goes into the wrong window, or two commands arrive at once and the second one runs before the first one has finished, or Claude says "done" and it wasn't.

This skill makes Claude coach you one step at a time:

- **One step per message,** then it waits for your output.
- **Every block is labelled** with where it goes: `→ TERMINAL`, `→ CLAUDE CODE`, `→ SQL EDITOR · STAGING (shop-staging)`.
- **It says what the step does** and what you should see, before you run it.
- **"Done" means proof:** a `grep`, a `select`, the live site. Not "Success. No rows returned", and not Claude's own summary.
- **Decisions come first,** as numbered options, before any code that depends on them.
- **New problems get queued,** so the current step finishes.
- **Anything destructive** gets a backup step and waits for your yes.

## What it looks like

```
Step 2 of 5: add the column on staging.

This adds an empty discount_code column to orders on the staging database only.

→ SQL EDITOR · STAGING (shop-staging)
alter table orders add column if not exists discount_code text;
```

See `examples/session.md` for a full short session.

## Why

These rules come from running a live HR and payroll system and several client stores this way. The failures it prevents are real: a migration run on the wrong database, half an SQL block run and reported as success, a deploy that broke because the code went out before the column it reads.

## Files

`SKILL.md` the rules for Claude, `examples/session.md` an invented example session.
