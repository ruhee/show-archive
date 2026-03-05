#!/usr/bin/env python3
"""Check seen.md list is correctly alphabetized per the rules."""

import os
import re
import unicodedata

# Path to full/seen.md relative to project root (parent of scripts/)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_PATH = os.path.join(_ROOT, 'full', 'seen.md')


def normalize_for_key(s: str) -> str:
    """Remove diacritics (Ü→U etc) via NFD, keep only alnum and $, lowercase."""
    out = []
    for c in unicodedata.normalize('NFD', s):
        if unicodedata.category(c) != 'Mn':  # skip combining marks (diacritics)
            if c.isalnum() or c in '$':
                out.append(c.lower())
    return ''.join(out)


def sort_key(name: str) -> str:
    s = re.sub(r'^\s*1\.\s*', '', name.strip())
    s = re.sub(r'\s+x\d+.*$', '', s)
    s = re.sub(r'\s*\([^)]*\).*$', '', s)
    s = s.strip()
    if s.startswith('The '):
        s = s[4:]
    # Treat "&" as the word "and" for sorting (e.g. "Billie & The Hollies" -> "billieandthehollies")
    s = s.replace('&', 'and')
    s = re.sub(r'[\s\-.,\'"/\[\]!?]+', '', s)
    return normalize_for_key(s)


def main():
    with open(SEEN_PATH, 'r') as f:
        lines = f.readlines()

    entries = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('###'):
            continue
        # Line format: "1. Artist name x2" or "1. Artist name"
        m = re.match(r'^1\.\s+(.+)$', line)
        if m:
            raw = m.group(1)
            entries.append((raw, sort_key('1. ' + raw)))

    errors = []
    for i in range(len(entries) - 1):
        name_a, key_a = entries[i]
        name_b, key_b = entries[i + 1]
        if key_a > key_b:
            errors.append((i + 2, name_a, key_a, name_b, key_b))  # 1-based line approx

    if errors:
        print("Out-of-order pairs (line ~, first name, second name):\n")
        for line_no, name_a, key_a, name_b, key_b in errors:
            print(f"  Line ~{line_no}:")
            print(f"    \"{name_a}\"  key={key_a!r}")
            print(f"    \"{name_b}\"  key={key_b!r}")
            print(f"    -> {name_a!r} should come after {name_b!r}\n")
    else:
        print("All entries are in correct order.")


def reorder_file():
    """Read seen.md, sort entries by sort_key, write back."""
    with open(SEEN_PATH, 'r') as f:
        lines = f.readlines()

    header = []
    entries = []
    for line in lines:
        stripped = line.strip()
        m = re.match(r'^1\.\s+(.+)$', stripped)
        if m:
            raw = m.group(1)
            entries.append((raw, sort_key('1. ' + raw)))
        else:
            if not entries:  # still in header (before first list item)
                header.append(line)

    entries.sort(key=lambda x: x[1])
    with open(SEEN_PATH, 'w') as f:
        f.writelines(header)
        for raw, _ in entries:
            f.write('1. ' + raw + '\n')
        f.write('\n')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--reorder':
        reorder_file()
        print('Reordered full/seen.md')
    else:
        main()
