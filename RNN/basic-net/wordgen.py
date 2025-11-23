#!/usr/bin/env python3
"""
generate_synthetic_passwords.py

Generate a synthetic password corpus for defensive/security model training.
- Default target: 1000 passwords
- Avoids a small blacklist of known common leaked passwords
- Produces realistic patterns: base words, caps, leet, years, digit patterns, keyboard sequences
- Weighted sampling produces many common patterns and fewer exotic ones

USAGE:
    python generate_synthetic_passwords.py
    python generate_synthetic_passwords.py --target 5000 --out mypwds.txt --seed 42
"""

import argparse
import random
import itertools
from collections import Counter

# ---------------- CONFIG ----------------
DEFAULT_TARGET = 1000
OUTPUT_FILE = "synthetic_passwords.txt"
RANDOM_SEED = None  # set to int for reproducible output, or None

# User-supplied blacklist (do not generate these exact strings)
BLACKLIST = {
    "password"
}

# Base word seeds (not leaked lists — generic words and patterns)
BASE_WORDS = [
    "summer","winter","spring","autumn","coffee","sun","moon","star","blue","green",
    "dragon","shadow","hunter","guitar","piano","adminx","office","work","home","mobile",
    "flower","daisy","oak","rose","river","mountain","rock","stone","laptop",
    "flowerpot","succulent","orchid","garden","plant","leaf","breeze","starlight"
]

YEARS = [str(y) for y in range(1970, 2026)]
DIGIT_PATTERNS = ["", "1", "12", "123", "1234", "007", "111", "777", "000", "99", "88"]
SYMBOLS = ["", "!", "!!", "@", "#", "$", "%", "?", "_", "-"]
PREFIXES = ["", "the", "my", "iAm", "its", "best", "get"]
SUFFIXES = ["", "01", "123", "xyz", "007", "99"]
KEYBOARD_PATTERNS = ["qwerty","asdf","zxcv","12345","qazwsx","1q2w3e"]
RANDOM_EXTRA = ["!", "!!", "?"]

# Leetspeak map
LEET_MAP = {
    'a': ['4','@'],
    'b': ['8'],
    'e': ['3'],
    'i': ['1','!'],
    'l': ['1','|'],
    'o': ['0'],
    's': ['5','$'],
    't': ['7'],
    'g': ['9'],
    'z': ['2']
}

# Weights (higher weight -> more frequent)
WEIGHTS = {
    "simple_word": 30,
    "word+digits": 40,
    "word+year": 10,
    "word+symbol": 8,
    "word+word": 5,
    "leet_variant": 6,
    "keyboard_combo": 1
}

# Limits to keep runtime and memory sane
MAX_TRIES = 50000  # attempts to reach target size

# --------------- HELPERS ---------------
def capitalize_variants(w):
    variants = {w, w.capitalize(), w.upper()}
    if len(w) > 1:
        # alternating case
        alt = ''.join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(w))
        variants.add(alt)
        variants.add(w[0].upper() + w[1:])
    return list(variants)

def leet_transform(word, max_changes=2):
    # randomly replace up to max_changes characters with leet substitutions
    chars = list(word)
    idxs = [i for i,c in enumerate(chars) if c.lower() in LEET_MAP]
    if not idxs:
        return word
    num_changes = random.randint(1, min(max_changes, len(idxs)))
    chosen = random.sample(idxs, num_changes)
    for i in chosen:
        subs = LEET_MAP.get(chars[i].lower(), [])
        if subs:
            chars[i] = random.choice(subs)
    return ''.join(chars)

def make_candidate_by_pattern(base):
    """Construct one candidate password based on weighted patterns."""
    p = random.choices(list(WEIGHTS.keys()), weights=list(WEIGHTS.values()), k=1)[0]

    if p == "simple_word":
        w = random.choice(capitalize_variants(base))
        # sometimes append a small digit pattern to keep realistic
        if random.random() < 0.3:
            w += random.choice(DIGIT_PATTERNS)
        return w

    if p == "word+digits":
        w = random.choice(capitalize_variants(base))
        w += random.choice(DIGIT_PATTERNS) or str(random.randint(1,9999))
        if random.random() < 0.1:
            w += random.choice(SYMBOLS)
        return w

    if p == "word+year":
        w = random.choice(capitalize_variants(base))
        w += random.choice(YEARS)
        # sometimes add symbol
        if random.random() < 0.2:
            w += random.choice(SYMBOLS)
        return w

    if p == "word+symbol":
        w = random.choice(capitalize_variants(base))
        w += random.choice(SYMBOLS) + random.choice(DIGIT_PATTERNS)
        return w

    if p == "word+word":
        other = random.choice(BASE_WORDS)
        w1 = random.choice(capitalize_variants(base))
        w2 = random.choice(capitalize_variants(other))
        sep = random.choice(["", ".", "_", "-"])
        return w1 + sep + w2 + random.choice(DIGIT_PATTERNS)

    if p == "leet_variant":
        w = leet_transform(random.choice(capitalize_variants(base)))
        # sometimes mix with digits
        if random.random() < 0.5:
            w += random.choice(DIGIT_PATTERNS)
        return w

    if p == "keyboard_combo":
        k = random.choice(KEYBOARD_PATTERNS)
        w = random.choice(capitalize_variants(base))
        # join either k+w or w+k
        if random.random() < 0.5:
            return k + w + random.choice(DIGIT_PATTERNS)
        else:
            return w + k + random.choice(DIGIT_PATTERNS)

    # fallback
    return base + random.choice(DIGIT_PATTERNS)

# --------------- MAIN GENERATION ---------------
def generate_passwords(target=DEFAULT_TARGET, seed=None, blacklist=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    blacklist = set(blacklist or set())
    produced = set()
    attempts = 0

    # Basic seeding: include some purely random combos to increase diversity
    while len(produced) < target and attempts < MAX_TRIES:
        attempts += 1
        base = random.choice(BASE_WORDS)
        candidate = make_candidate_by_pattern(base)

        # randomly apply an extra leet or symbol occasionally
        if random.random() < 0.08:
            candidate = leet_transform(candidate, max_changes=2)
        if random.random() < 0.05:
            candidate += random.choice(RANDOM_EXTRA)

        # ensure it's not obviously blacklisted and not too short
        if candidate.lower() in (s.lower() for s in blacklist):
            continue
        if len(candidate) < 4:
            continue

        produced.add(candidate)

    # if we didn't reach target, try to expand by combining tokens deterministically
    if len(produced) < target:
        extras = []
        for a, b in itertools.product(BASE_WORDS, repeat=2):
            if len(produced) >= target:
                break
            cand = a + random.choice(["", ".", "_", "-"]) + b + random.choice(DIGIT_PATTERNS)
            if cand.lower() in (s.lower() for s in blacklist):
                continue
            if len(cand) >= 4:
                produced.add(cand)
        # still maybe insufficient — pad with random character sequences (defensive)
    # Final padding if still short
    pad_attempts = 0
    while len(produced) < target and pad_attempts < target * 10:
        pad_attempts += 1
        # generate a pseudo-random but human-like token
        w1 = random.choice(BASE_WORDS)
        w2 = random.choice(BASE_WORDS)
        cand = w1[:max(2, len(w1)//2)] + "." + w2[:max(2, len(w2)//2)] + str(random.randint(0,999))
        if cand.lower() in (s.lower() for s in blacklist):
            continue
        produced.add(cand)

    return list(produced)

# ----------------- CLI -------------------
def main():
    parser = argparse.ArgumentParser(description="Synthetic Password Generator (ethical use)")
    parser.add_argument("--target", type=int, default=DEFAULT_TARGET, help="number of passwords to generate")
    parser.add_argument("--out", type=str, default=OUTPUT_FILE, help="output filename")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    args = parser.parse_args()

    pwds = generate_passwords(target=args.target, seed=args.seed, blacklist=BLACKLIST)
    # Shuffle for distribution
    random.shuffle(pwds)
    # Write to file
    with open(args.out, "w", encoding="utf-8") as f:
        for p in pwds:
            f.write(p + "\n")

    print(f"Generated {len(pwds)} passwords -> {args.out}")
    print("\nSample (first 20):")
    for s in pwds[:20]:
        print(s)

if __name__ == "__main__":
    main()
