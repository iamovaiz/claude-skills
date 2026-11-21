# post-check: catch what makes a post look machine-written

You wrote a LinkedIn post with AI help, edited it twice, and now there's an em dash in line one, a `,.` where a dash used to be, and a `{{CTA}}` you forgot to fill. post-check finds those in under a second, before your network does.

## What it catches

- Em dashes, curly quotes, the single `…` character, and invisible characters such as zero-width and non-breaking spaces
- Leftover punctuation from edits: `,.` `,,` `!!` `..` double spaces
- Unfilled placeholders: `{{...}}`, `[insert ...]`, TODO, TBD
- Words that read as AI-written: delve, leverage, seamless, journey, "thrilled to announce" and about 40 more
- Claims and names **you** have ruled out, from your own `offlimits.txt`
- Platform limits: hashtag count, X's 280 characters, LinkedIn's preview cut-off

It is a rule check, not an AI detector. Passing it doesn't make a post undetectable, and the skill tells Claude never to claim that.

## Use it

```bash
cp offlimits.example.txt ~/.config/post-check/offlimits.txt   # then add your own rules
python3 postcheck.py post.txt --platform linkedin              # or x, or generic
```

With the skill installed, ask Claude to "check this post before I publish it". Claude runs the script, rewrites what fails, and shows you the final text with the check result under it. It never posts for you.

## Off-limits file

One rule per line, `regex | label`:

```
\b500\s?k\b | 500K revenue claim (not provable)
\bacme\s?corp\b | client name (no publishing permission)
```

Put the numbers you can't prove and the names you have no permission to publish here. It is the check that saves you from the post you'd have to delete.

## Files

`SKILL.md` instructions for Claude, `postcheck.py` the checker (standard library, no network), `examples/` a post that fails on 9 rules and one that passes.
