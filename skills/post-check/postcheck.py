#!/usr/bin/env python3
"""post-check: rule-based pre-publish check for social posts, comments and DMs.

Usage:
  python3 -I postcheck.py post.txt [--platform linkedin|x|generic]
                                   [--offlimits FILE] [--banned FILE]
  cat post.txt | python3 -I postcheck.py -

No dependencies, no network. Exit code 0 = READY, 1 = BLOCKED, 2 = usage error.
"""
import argparse
import os
import re
import sys
import unicodedata

PLATFORMS = {
    # name: (max hashtags, min chars warn, max chars warn, hard max chars, first-line warn)
    "linkedin": (3, 400, 2000, 3000, 140),
    "x": (2, 0, 280, 280, 280),
    "generic": (5, 0, 5000, None, 200),
}

SLOP = [
    "delve", "leverage", "robust", "seamless", "cutting-edge", "game-changer", "game changer",
    "synergy", "passionate", "results-driven", "journey", "unlock", "empower", "elevate",
    "tapestry", "testament", "landscape", "realm", "embark", "foster", "underscore", "showcase",
    "crucial", "pivotal", "transformative", "innovative", "world-class", "state-of-the-art",
    "moreover", "furthermore", "additionally", "navigate", "let that sink in", "fast-paced world",
    "thrilled to announce", "excited to share", "in conclusion", "ultimately", "dive into",
    "deep dive", "holistic",
]

INVISIBLE_EXTRA = {" ", " ", " ", " ", " "}


def find_config(explicit, name):
    if explicit:
        return explicit
    for p in (os.path.join(os.getcwd(), name),
              os.path.expanduser(os.path.join("~/.config/post-check", name))):
        if os.path.isfile(p):
            return p
    return None


def read_rules(path):
    """One rule per line: `regex | label`. Lines starting with # are comments."""
    rules = []
    if not path:
        return rules
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            pat, _, label = line.partition(" | ")
            try:
                re.compile(pat)
            except re.error as exc:
                print(f"bad regex in {path}: {pat!r} ({exc})", file=sys.stderr)
                sys.exit(2)
            rules.append((pat, label.strip() or pat))
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="text file to check, or - for stdin")
    ap.add_argument("--platform", choices=PLATFORMS, default="linkedin")
    ap.add_argument("--offlimits", help="file of claims/names that must never appear")
    ap.add_argument("--banned", help="file of extra banned words or phrases")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    max_tags, min_len, max_len, hard_max, first_max = PLATFORMS[args.platform]
    fails, warns = [], []

    def lines_with(pat, flags=0):
        out = []
        for n, line in enumerate(text.splitlines(), 1):
            if re.search(pat, line, flags):
                out.append(f"L{n}: {line.strip()[:70]}")
        return out

    # 1. Invisible / format characters
    inv = [c for c in text if unicodedata.category(c) == "Cf" or c in INVISIBLE_EXTRA]
    if inv:
        names = sorted({f"U+{ord(c):04X}" for c in inv})
        fails.append(f"Invisible characters ({len(inv)}): {', '.join(names)}")

    # 2. Typography
    for ch, name in [("—", "em dash"), ("–", "en dash"), ("“", "curly quote"),
                     ("”", "curly quote"), ("‘", "curly apostrophe"),
                     ("’", "curly apostrophe"), ("…", "ellipsis character")]:
        if ch in text:
            fails.append(f"{name}: {text.count(ch)}x")

    # 3. Stray punctuation
    for pat, name in [(r",\s*[.!?]", "comma before full stop"), (r",\s*,", "double comma"),
                      (r"\s[,.;:](?=\s|$)", "space before punctuation"),
                      (r"^\s*[,;:]", "line starts with punctuation"),
                      (r"[!?]{2,}|(?<!\.)\.\.(?!\.)", "repeated end punctuation"),
                      (r"\(\s*\)|\S {2,}\S", "empty brackets or double space")]:
        hits = lines_with(pat, re.M)
        if hits:
            fails.append(f"{name}: " + " | ".join(hits[:3]))

    # 4. Unfilled placeholders
    ph = re.findall(r"\{\{[^}]*\}\}|\[(?:confirm|todo|tbd|x+|insert)[^\]]*\]|\bTODO\b|\bTBD\b|\bXX+\b",
                    text, re.I)
    if ph:
        fails.append(f"Unfilled placeholders: {', '.join(sorted(set(ph)))}")

    # 5. Off-limits claims and names (user config)
    off_path = find_config(args.offlimits, "offlimits.txt")
    for pat, label in read_rules(off_path):
        if re.search(pat, text, re.I):
            fails.append(f"Off-limits: {label}")

    # 6. Banned vocabulary
    banned = list(SLOP) + [label for _, label in read_rules(find_config(args.banned, "banned.txt"))]
    found = []
    for w in banned:
        suffix = r"\w*" if " " not in w else ""
        if re.search(r"(?<![\w-])" + re.escape(w) + suffix + r"(?![\w-])", text, re.I):
            found.append(w)
    if found:
        fails.append(f"Banned words: {', '.join(found)}")

    # 7. Structural tells (warn)
    for pat, name in [(r"\bnot (just|only)\b[^.\n]*\b(it'?s|but)\b", "'not just X, it's Y' shape"),
                      (r"^\s*(the (result|catch|truth|answer|kicker)|why|how)\?\s*$",
                       "one-line rhetorical question"),
                      (r"\b(thoughts|agree|who else)\?\s*$", "reflex engagement bait"),
                      (r"[\U0001F680\U0001F525\U0001F4A1✨\U0001F3AF\U0001F447]", "stock emoji")]:
        hits = lines_with(pat, re.I | re.M)
        if hits:
            warns.append(f"{name}: " + " | ".join(hits[:2]))

    # 8. Format
    tags = re.findall(r"#\w+", text)
    if len(tags) > max_tags:
        fails.append(f"Hashtags: {len(tags)} (max {max_tags} for {args.platform})")
    body = re.sub(r"#\w+", "", text)
    if args.platform == "linkedin" and re.search(r"https?://|www\.", body):
        warns.append("Link in post body: move it to the first comment")
    n = len(text.strip())
    if hard_max and n > hard_max:
        fails.append(f"Length {n} chars is over the {args.platform} limit of {hard_max}")
    elif n < min_len or n > max_len:
        warns.append(f"Length {n} chars (outside {min_len} to {max_len} for {args.platform})")
    first = text.strip().splitlines()[0] if text.strip() else ""
    if len(first) > first_max:
        warns.append(f"First line is {len(first)} chars; feeds cut at about {first_max}")
    sents = [s for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", body)) if len(s.split()) > 2]
    if len(sents) >= 5:
        lens = [len(s.split()) for s in sents]
        mean = sum(lens) / len(lens)
        sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
        if sd / mean < 0.35:
            warns.append(f"Sentence lengths too even (variation {sd/mean:.2f}); break one, let one run long")

    print(f"POST CHECK  {args.platform}, {n} chars, {len(tags)} hashtags"
          + (f", off-limits list: {off_path}" if off_path else ", no off-limits list found"))
    for f in fails:
        print("  FAIL  " + f)
    for w in warns:
        print("  WARN  " + w)
    print("  RESULT  " + ("BLOCKED: fix every FAIL" if fails
                          else ("READY after you review the WARNs" if warns else "READY")))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
