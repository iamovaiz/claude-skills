# staged-release-supabase-vercel: ship through staging, then prove it's live

For apps with a staging and a production Supabase project and a Vercel deployment for each. The skill walks Claude through a release where nothing reaches production untested, and "done" means proof, not a green badge.

## The order that prevents most incidents

1. Feature branch from a fresh main
2. Migration on **staging** first, with a CHECK query that states the expected result
3. Merge into staging with a conflict guard (no committing conflict markers)
4. Test through the real UI, every role the change touches
5. PR with CI green
6. Production migration **before** the merge, so new code never reads a column that doesn't exist yet
7. Merge only after your yes
8. Prove the live domain serves the new version

## Step 8 is the one people skip

```bash
python3 served_version.py https://app.example.com --expect 2.4.1
```

```
FOUND  2.4.1 in /assets/index-Ab12.js
```

It fetches the page without cache and searches the JavaScript bundles for the version string. We added it after a production domain kept serving an old build through four releases while every new deployment showed READY. The cause was an earlier Instant Rollback, which stops Vercel from moving the domain automatically. The skill covers that fix and six other failures seen in real releases.

## Safety built in

Claude never runs production SQL, merges or force-pushes on its own, never asks for passwords, and labels every SQL block with the database it's for.

## Files

`SKILL.md` the procedure, `served_version.py` the live check (standard library). Exit codes: 0 found, 1 not found, 2 fetch error.
