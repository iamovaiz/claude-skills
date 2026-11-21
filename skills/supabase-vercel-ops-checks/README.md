# supabase-vercel-ops-checks: the failures that look like success

A checklist skill for anyone running apps on Supabase and Vercel, especially one codebase with a separate database per client. Every item came from something that went wrong or nearly did.

## A few of the checks

- **New Supabase projects allow public sign-ups.** Turn it off before anyone finds your login page.
- **Free projects pause after about a week without activity**, and dashboard backups aren't on the free plan. Keep your own backup.
- **Adding a Vercel environment variable does nothing until you redeploy.**
- **An Instant Rollback pins your production domain.** New deploys show READY while the site serves the old build.
- **A migration that errors after `commit` still applied.** Check your migrations ledger before re-running anything.
- **Newer `pg_dump` output breaks the Management API** with a syntax error until you strip the `\restrict` lines.

Plus scoped access tokens with tracked expiry dates, one-database-per-client rules, and what a daily health check should alert on.

## Use it

Install it and Claude applies the checklist when you create a project, onboard a client, run remote migrations, or say "the deploy worked but the site didn't change".
