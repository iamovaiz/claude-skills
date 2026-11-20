---
name: staged-release-supabase-vercel
description: Ship a code or database change for a Supabase + Vercel app the safe way - feature branch, migration on staging first, staging merge with a conflict guard, PR with checks, production migration before merge, then proof that the live domain serves the new version. Use when releasing a change to an app hosted on Vercel with a Supabase database that has separate staging and production projects.
---

# staged-release-supabase-vercel

A release procedure for apps with a staging and a production Supabase project and a Vercel deployment for each. It was written for a solo builder directing Claude Code on a live business system, where the owner runs every SQL statement and approves every merge, and Claude prepares, tests and reports.

The rule behind every step: nothing reaches production that has not run on staging, and "done" means a query result or the live site's own files, not a green badge.

## Before the first release, write down the project facts

Put these in the repo's `CLAUDE.md` so every session reads them. Do not guess any of them.

- Repo, protected branches, how PRs are created and merged (squash or not).
- Staging: git branch, Vercel URL, Supabase project name and ref.
- Production: the branch or release process that deploys it, the domain, Supabase project name and ref.
- Where the version lives (for example `package.json` and a `version.ts`) and whether CI requires a CHANGELOG entry.
- Platform limits that break builds (for example Vercel's serverless function count on your plan).
- Which env vars exist for preview deployments. If previews have no database variables, a PR preview shows a blank page; test on the staging URL instead.

## Procedure

1. **Branch** from a fresh main: `git fetch origin main && git checkout -B feature/<name> origin/main`. Run `git status` first and never overwrite unrelated work.
2. **Build the change.** Keep business rules in plain modules with an offline test script, and add that script to CI.
3. **Migration**, if any: one timestamped file in `supabase/migrations/`, wrapped in `begin; ... commit;`, safe to run twice (`if not exists`), row-level security on for new tables, grants stated explicitly, a header with the rollback SQL, and a final `select` that states the expected result (the CHECK).
4. **Verify locally:** compile and type checks, unit tests, the project's own check scripts, `npm run build`. For database logic, run the real migration against a local Postgres before staging.
5. **Version and CHANGELOG,** commit, push.
6. **Staging migration.** Give the user the SQL labelled `Supabase SQL Editor · STAGING (<project name>)` and the expected CHECK result. Wait for the result. If they ran only part of the block, ask them to select all and run again.
7. **Merge into the staging branch:**
   - `git fetch origin +refs/heads/staging:refs/remotes/origin/staging` (a default clone may only fetch main).
   - `git checkout -B staging origin/staging && git merge --no-ff --no-commit feature/<name>`
   - Resolve each conflicted file in favour of the feature branch, then grep for conflict markers and confirm `git diff feature/<name> -- <source folders>` is empty before you commit. Never `git add -A` over unresolved conflicts.
   - Push and wait until the Vercel deployment for that commit is READY.
8. **Test on staging through the real UI,** every role the change touches, including what should be refused. The user does all logins. Tag any test data you ask them to insert (for example `source='release-test'`) and give them the cleanup SQL afterwards.
9. **Open the PR:** what changed, migration status (staging done, production not yet), what was verified and how, known limits, steps after merge. Wait for CI to pass; read failing job logs instead of guessing.
10. **Production migration,** if any, labelled `Supabase SQL Editor · PRODUCTION (<project name>)`, run before the merge so the new code never reads a column that does not exist yet. Wait for the CHECK result.
11. **Merge only after the user says yes in chat.** If main moved, rebase, take the next free version, re-run checks, and push with `--force-with-lease=<branch>:<old sha>` on your feature branch only.
12. **Prove it is live:** `python3 -I served_version.py https://<production domain> --expect <version>`. It fetches the page without cache and searches the JavaScript bundles for the version string.
13. **Close out:** report what is live, what was verified, and what is left (data fixes, test-data cleanup). The user deletes the remote branch.

## Validation

- CI green on the PR head commit.
- Staging tree identical to the feature branch after the merge.
- Production CHECK returned the expected row before the merge.
- `served_version.py` finds the new version on the production domain.

## Failure modes seen

- Staging merge committed with conflict markers: the build failed and never went live. Fix forward by checking out the feature branch's version of those files.
- The production domain kept serving an old build while new deployments showed READY. Cause: an earlier Instant Rollback in Vercel stops automatic domain assignment. Ask the user whether the rollback was on purpose; if not, promote the newest READY production deployment and run `served_version.py` again.
- A branch was moved but Vercel built nothing for that commit. Push an empty commit to trigger the build, then check the served version.
- CI lacks a library a new test needs. Install it in the workflow step.
- Staging without a `SITE_URL` variable makes links and QR codes in staging documents point to production.
- The Supabase SQL editor tab freezes. Open a new tab rather than retrying in the stuck one.
- Per-user settings stored as JSON: change one key with a jsonb merge on exact matches (preview with a select first), never overwrite the whole object.

## Safety limits

- Never type passwords or decrypt environment variables. The user logs in.
- Never run production SQL or merge without the user's explicit yes in chat.
- No force pushes to shared branches, no deleting branches, no resets of staging or main.
- Never edit production data without a backup table first.
