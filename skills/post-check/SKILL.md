---
name: post-check
description: Check a social post, comment, reply, DM or caption before it is published - invisible characters, em dashes, stray punctuation, placeholders, banned AI-sounding words, off-limits claims and platform limits. Use when the user asks to check, proof or approve a LinkedIn or X post, or before showing any drafted post as ready.
---

# post-check

A local rule check for text someone is about to paste into LinkedIn, X or another feed. It catches the mechanical mistakes that make a post look machine-written or get its author in trouble: an em dash left in, a `,.` left behind after an edit, a `{{CTA}}` placeholder, a revenue claim the author already ruled out, a client name they have no permission to publish.

It is a rule check, not an AI detector. Passing it does not mean a post cannot be flagged as AI. Never tell the user a post is undetectable.

## Setup (once per user)

1. Copy `offlimits.example.txt` to `~/.config/post-check/offlimits.txt` (applies everywhere) or `./offlimits.txt` (this folder only).
2. Ask the user for the claims they have ruled out (numbers they cannot prove) and the names they must not publish (clients, employers, people). Write one rule per line: `regex | label`. Never fill this file with guesses.
3. Optional: `banned.txt` in the same places adds words to the built-in banned list, one per line.

## Procedure

1. Save the exact text the user will paste to `post.txt`, hashtags included. Leave out your own notes.
2. Run `python3 -I postcheck.py post.txt --platform linkedin` (or `x`, or `generic`). The script is in this skill's folder. It needs no packages and no network.
3. Fix every FAIL by rewriting the sentence, not by swapping one symbol for another. Never fix an off-limits claim by inventing a different number: remove the claim, or ask the user for the real figure.
4. For each WARN, fix it or tell the user in one line why it can stay.
5. Run again until RESULT is READY, or only WARNs with a stated reason remain.
6. Show the final text in a copy-ready block with the check result under it. Never show the text without the check, or the result without the text.
7. Never post, schedule or publish anything yourself. The user posts it.

## What it checks

FAIL, must be fixed:
- Invisible characters: zero-width, non-breaking and thin spaces, soft hyphen, BOM.
- Em dashes, en dashes, curly quotes, the single ellipsis character.
- Stray punctuation: `,.`, `,,`, a space before punctuation, a line that starts with a comma, `!!`, `..`, empty brackets, double spaces.
- Unfilled placeholders: `{{...}}`, `[confirm ...]`, `[insert ...]`, TODO, TBD, XX.
- Anything matching the user's `offlimits.txt`.
- Banned words (delve, leverage, robust, seamless, journey, crucial, moreover and the rest of the list in the script), including forms like "seamlessly".
- Too many hashtags for the platform (LinkedIn 3, X 2, generic 5), and text over the X limit of 280 characters.

WARN, fix or explain:
- "Not just X, it's Y", one-line rhetorical questions ("The result?"), "Thoughts?" or "Agree?" closers, stock emoji.
- A link in a LinkedIn post body (put it in the first comment).
- Length outside the usual range for the platform, a first line longer than the feed shows.
- Sentence lengths that are all about the same.

## Checks the script cannot do

Read the text yourself before calling it READY:
- Every number, client, result and date is one the user gave you. Nothing invented. If unsure, ask.
- No employee names, internal figures or confidential details about the user's employer or clients.
- It sounds like the user: compare with past posts they have shared.
- One idea per post. The close is one question or one instruction, not both.

## Examples

`examples/bad-post.txt` fails on 9 rules. `examples/good-post.txt` passes on LinkedIn and fails on X for length.

## Exit codes

0 READY, 1 BLOCKED, 2 usage or config error (for example a bad regex in `offlimits.txt`).
