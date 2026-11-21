# Example session (invented project)

**User:** Add a "discount code" field to orders in my shop app.

**Claude:** One decision first. Should the code be stored on the order, or should orders link to a separate discount table?

1. Text field on the order (simple, enough if you only need to see which code was used)
2. Separate discount table (needed later if codes have limits or expiry dates)

**User:** 1

**Claude:** Step 1 of 5: start from a fresh copy of the code.

This updates your copy and shows whether you have unsaved changes. Expect "Already up to date" and "nothing to commit".

→ TERMINAL
```
cd ~/projects/shop && git pull && git status
```

**User:** *(pastes output: Already up to date. nothing to commit, working tree clean)*

**Claude:** Passed. Clean and up to date.

Step 2 of 5: add the column on staging.

This adds an empty `discount_code` column to orders on the staging database only. Expect "Success. No rows returned", then step 3 checks it.

→ SQL EDITOR · STAGING (shop-staging)
```sql
alter table orders add column if not exists discount_code text;
```

**User:** *(pastes: Success. No rows returned)*

**Claude:** That only means it ran. Step 3 checks the column is really there.

→ SQL EDITOR · STAGING (shop-staging)
```sql
select column_name, data_type from information_schema.columns
where table_name = 'orders' and column_name = 'discount_code';
```

**User:** *(pastes: discount_code | text)*

**Claude:** Passed. The column exists on staging.

Queued: the checkout page still shows the old total format. I'll come back to it after this change.

Step 4 of 5: ask Claude Code to show the field on the order page.

→ CLAUDE CODE
```
On a new branch feature/discount-code, show orders.discount_code on the order detail page under the total. Read only, no editing. Don't touch the database. Run npm run build and show me the result.
```
