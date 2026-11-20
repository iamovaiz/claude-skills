---
name: supabase-vercel-ops-checks
description: Setup and health checklist for apps on Supabase and Vercel - lock down a new Supabase project, scope and track access tokens, run migrations remotely without double-applying them, and catch the silent failures (paused free projects, missing redeploys, domains pinned to old builds). Use when creating a new Supabase project, onboarding a client installation, running migrations through the Management API, or when a deploy looks fine but the site is not.
---

# supabase-vercel-ops-checks

Checks learned from running one codebase for several clients, each with its own Supabase database and Vercel app. Every item here came from something that went wrong or nearly did.

## New Supabase project

1. **Turn off public sign-ups** (Authentication, Sign In / Providers, "Allow new users to sign up"). New projects allow it. Left on, anyone can create an account in a business system meant for invited staff only. Create users yourself in the dashboard with auto-confirm.
2. **Label the project before any SQL.** State the project name and ref above every SQL block you give the user. Running a migration on the wrong project is the most common near miss when staging and production sit side by side.
3. **Free plan limits.** Free projects pause after about 7 days without activity, and the dashboard backups are not available on the free plan. Keep your own scheduled backup and treat a paused project as one health problem, not several.
4. **Region.** Choose it on purpose (close to the users), because moving later means a new project.

## Access tokens for automation

- Create a token per project, scoped to what the automation needs (for example database read-write, backups read, API keys read), with an expiry such as 90 days.
- Record each token's expiry date where your health check can see it, and warn before it runs out.
- The user pastes token values into the host's secret store. Never ask for a secret in chat and never print one. Check names and lengths only.
- A scoped token may not be allowed to read project status. A "database possibly not accessible" message can mean a paused project, not a broken token.

## Vercel

- **Adding or changing an environment variable does nothing until you redeploy.** If a connection fails right after a variable was added, redeploy first.
- **Preview deployments get only the variables you set for previews.** A preview with no database URL shows a blank page.
- **An Instant Rollback pins the production domain** to the rolled-back build. Later deployments show READY but the domain keeps serving the old one. Promote the newest READY production deployment, then check what the domain serves (the `served_version.py` script in the staged-release-supabase-vercel skill does this).
- Keep a small GitHub Actions budget if CI runs there: at $0 the jobs stop and the error can read "repository not found".

## Running migrations remotely

When migrations run through the Supabase Management API (one file per call):

- An error before a file's `commit` rolls it back. An error after the commit (for example a failing CHECK select at the end) keeps the change but still returns an error. A timeout may have committed.
- So after any failure, read your migrations ledger (for example a `schema_migrations` table) and find out which case it was. Never re-run blindly.
- Schema dumps from newer `pg_dump` versions contain `\restrict` / `\unrestrict` lines and `SET transaction_timeout`, which the API rejects with a syntax error (42601). Strip them before sending.

## One database per client

- Never put one client's data in another client's database, not even test rows.
- Test clients get invented names, emails and IDs only.
- Deleting a test project or app needs the user's confirmation, every time.
- Paid plan changes need the user's yes.

## Health check, per installation

A daily check should report, and alert on:

- App reachable and serving the expected version.
- Migrations up to date with the code.
- Last backup within your limit (for example 26 hours for platform backups, 8 days for your own weekly backup).
- Token expiry more than 14 days away.
- Database size under the plan limit.
- Sign-ups still off.

New scheduled jobs report nothing until their first run, so allow a grace period after a release before alerting on them.
