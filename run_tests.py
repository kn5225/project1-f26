"""
Strict test harness. Runs Dictionary.py (main) and app1..app6 with the spec
inputs, compares output to the spec, and validates the generated files.

Put this file in the project folder (next to Dictionary.py and app1.py ... app6.py).

    python run_tests.py              fast tests only
    python run_tests.py --slow       also run english enhanced insertion sort (minutes)
    python run_tests.py --only app3  run tests whose name contains "app3"
    python run_tests.py --dir PATH   project folder (default: folder of this script)

The only normalizations applied to BOTH spec and actual output:
  - blank lines ignored and runs of spaces collapsed (the PDF drops blank lines and extra spaces)
  - timing numbers replaced by <T>
  - curly apostrophes treated as straight ones (the PDF typesets them curly)
  - the truncated "List of letter combinations:" line is ignored
Everything else must match exactly, including ".txt" in dictionary names.

A test also fails if the script crashes, times out, or writes to stderr.
"""
import argparse
import difflib
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from typing import Callable, Optional

# ----------------------------------------------------------------------------
# prompts (typed answers are not echoed when stdout is captured, so they are
# re-inserted after each prompt to rebuild a terminal-style transcript)
# ----------------------------------------------------------------------------
P_MAIN = "Enter dictionary name (from file 'name'.txt): "
P_DICT = "Choose your dictionary: "
P_SDICT = "Choose your *sorted* dictionary: "
P_ALGO = "Choose your sorting algorithm: "
P_RAND = "How many random words would you like to search? "
P_FILE = "Enter file name to spell check: "
P_WORD = "Enter word to analyze: "
P_LETTERS = "Enter series of letter: "
P_NLET = "How many code letters to crack?: "


def P_OPT(k):
    return "Enter all the options for letter %d: " % k


@dataclass
class Test:
    name: str
    script: str
    answers: list             # [(prompt, typed answer), ...]
    expected: str
    mode: str = "lines"       # lines | contains
    requires: tuple = ()      # files that must exist before running
    slow: bool = False
    file_check: Optional[tuple] = None   # (filename, [expected lines])
    extra: Optional[Callable] = None     # extra check on the raw output


# ----------------------------------------------------------------------------
# expected outputs copied from the spec
# (name lines use "short.txt"/"english.txt", per the ruling that get_name()
#  returns the full filename)
# ----------------------------------------------------------------------------
PRELIM_BAD = """Enter dictionary name (from file 'name'.txt): portuguese
File portuguese.txt does not exist!"""

PRELIM_SHORT = """Enter dictionary name (from file 'name'.txt): short
Load short.txt
Name main dictionary: short.txt
Size main dictionary: 20
Five random words: tea cases file morning of
Name extracted dictionary: N/A
Display extracted dictionary:
tea
cases
file
morning
of
Extracted dictionary shuffled in <T>s:
Display extracted dictionary:
morning
tea
of
file
cases
Linear search for the word 'morning' in extracted dictionary
Is 'morning' found: True at index 0
Extracted dictionary sorted in <T>s:
Display extracted dictionary:
cases
file
morning
of
tea
Binary search for the word 'morning' in extracted dictionary
Is 'morning' found: True at index 2
Binary search for the word 'night' in extracted dictionary
'night' is not found so it must be inserted at index 3"""

PRELIM_ENGLISH = """Enter dictionary name (from file 'name'.txt): english
Load english.txt
Name main dictionary: english.txt
Size main dictionary: 99171
Five random words: skyjacking professionally ripped corrective dependability's
Name extracted dictionary: N/A
Display extracted dictionary:
skyjacking
professionally
ripped
corrective
dependability's
Extracted dictionary shuffled in <T>s:
Display extracted dictionary:
corrective
skyjacking
dependability's
ripped
professionally
Linear search for the word 'morning' in extracted dictionary
Is 'morning' found: False at index -1
Extracted dictionary sorted in <T>s:
Display extracted dictionary:
corrective
dependability's
professionally
ripped
skyjacking
Binary search for the word 'morning' in extracted dictionary
'morning' is not found so it must be inserted at index 2
Binary search for the word 'night' in extracted dictionary
'night' is not found so it must be inserted at index 2"""

APP1_SHORT = """Dictionaries: short english french spanish
Choose your dictionary: short
Load short.txt
**Dictionary short.txt contains 20 words
1-insertion
2-enhanced insertion sort
Choose your sorting algorithm: 1
**Dictionary short.txt shuffled in <T> seconds
**Dictionary short.txt sorted with -insertion- in <T> seconds
Save short_sorted.txt"""

# not in the spec, derived from app1.py's print statements for option 2
APP1_SHORT_ENH = """Dictionaries: short english french spanish
Choose your dictionary: short
Load short.txt
**Dictionary short.txt contains 20 words
1-insertion
2-enhanced insertion sort
Choose your sorting algorithm: 2
**Dictionary short.txt shuffled in <T> seconds
**Dictionary short.txt sorted with -enhanced insertion- in <T> second
Save short_sorted.txt"""

SHORT_SORTED_FILE = ["act", "animal", "ate", "cases", "cat", "class", "code",
                     "computer", "dictionary", "eat", "electrical", "file",
                     "morning", "of", "school", "screen", "simon", "sorting",
                     "tea", "this"]

APP1_ENGLISH = """Dictionaries: short english french spanish
Choose your dictionary: english
Load english.txt
**Dictionary english.txt contains 99171 words
1-insertion
2-enhanced insertion sort
Choose your sorting algorithm: 2
**Dictionary english.txt shuffled in <T> seconds
**Dictionary english.txt sorted with -enhanced insertion- in <T> second
Save english_sorted.txt"""

APP2_FRENCH = """Dictionaries: short english french spanish
Choose your *sorted* dictionary: french
Load french_sorted.txt
**Dictionary french_sorted.txt contains 139719 words
How many random words would you like to search? 3000
first few random words:
f\u00e9odal
pr\u00e9munissions
p\u00e2ti
discuterions
entrelacements
Search time is: <T>, with 16 average number of steps"""

APP3_LETTER = """Dictionaries: english french spanish
Choose your *sorted* dictionary: english
Load english_sorted.txt
Enter file name to spell check: letter
Dear (Studants,)
this is a sample file similar to the one that will
be used to test your projects. I (sugest) you use it
for testing your code and (developping) your software.
Have fun!
E. (Polizzi)"""

APP3_FRENCH = """Dictionaries: english french spanish
Choose your *sorted* dictionary: french
Load french_sorted.txt
Enter file name to spell check: sample_french
Extrait de (20,000) lieues sous les mers
De (Jules) (Verne)
Le (Nautilus) \u00e9tait alors revenu \u00e0 la surface des flots.
Un des marins, plac\u00e9 sur les derniers \u00e9chelons, d\u00e9vissait les boulons du panneau.
Mais les \u00e9crous \u00e9taient \u00e0 peine d\u00e9gag\u00e9s, que le panneau se releva avec une violence extr\u00eame,
\u00e9videmment tir\u00e9 par la ventouse (d'un) bras de poulpe.
Aussit\u00f4t un de ces longs bras se glissa comme un serpent par (l'ouverture,)
et vingt autres (s'agit\u00e8rent) au-dessus. (D'un) coup de hache, le capitaine (Nemo) coupa ce formidable tentacule,
qui glissa sur les \u00e9chelons en se tordant."""

APP3_POEM = """Dictionaries: english french spanish
Choose your *sorted* dictionary: english
Load english_sorted.txt
Enter file name to spell check: poem
File poem.txt does not exist!"""

APP4_TAE = """Dictionaries: short english french spanish
Choose your dictionary: short
Load short.txt
Enter word to analyze: tae
3 anagram(s) found
ate
tea
eat"""

APP4_UNLUCKY = """Dictionaries: short english french spanish
Choose your dictionary: short
Load short.txt
Enter word to analyze: unlucky
0 anagram(s) found"""

APP4_OPST = """Dictionaries: short english french spanish
Choose your dictionary: english
Load english.txt
Enter word to analyze: opst
6 anagram(s) found
stop
opts
post
tops
pots
spot"""

APP5_ENGLISH = """Dictionaries: short english french spanish
Choose your dictionary: english
Load english.txt
Enter series of letter: english
Number of non-zero letter combinations found: 127
61 anagram(s) found with scrabble score
e 1
n 1
l 1
i 1
s 1
g 2
in 2
es 2
ls 2
is 2
lei 3
lie 3
nil 3
gs 3
sin 3
ins 3
leg 4
gel 4
gin 4
lien 4
line 4
lens 4
sine 4
lies 4
isle 4
leis 4
h 4
glen 5
legs 5
gels 5
egis 5
sing 5
sign 5
gins 5
liens 5
lines 5
eh 5
he 5
hi 5
sh 5
glens 6
singe 6
sling 6
hen 6
hie 6
hes 6
she 6
his 6
single 7
hens 7
hies 7
shin 7
nigh 8
shine 8
sigh 8
hinge 9
neigh 9
hinges 10
neighs 10
sleigh 10
shingle 11"""

APP6_SHORT = """Dictionaries: short english french spanish
Choose your *sorted* dictionary: short
Load short_sorted.txt
How many code letters to crack?: 3
Enter all the options for letter 1: c e
Enter all the options for letter 2: a p
Enter all the options for letter 3: t i
All lock combinations to consider:
['c', 'e']
['a', 'p']
['t', 'i']
2 word(s) found:
cat
eat"""

# the spec only gives the count for the bike lock experiment
APP6_BIKE = """Load english_sorted.txt
21 word(s) found:"""

BIKE_OPTIONS = ["qetuls", "rufloq", "kmsarw", "wxsopg"]


def check_bike(raw_out):
    """Validate the printed word list of the bike lock experiment."""
    lines = [l.strip() for l in raw_out.replace("\r", "").split("\n") if l.strip()]
    idx = next((i for i, l in enumerate(lines)
                if re.match(r"^\d+ word\(s\) found:", l)), None)
    if idx is None:
        return False, ["no '<N> word(s) found:' line"]
    n = int(lines[idx].split()[0])
    words = lines[idx + 1:]
    problems = []
    if len(words) != n:
        problems.append("header says %d words but %d were printed" % (n, len(words)))
    if len(set(words)) != len(words):
        problems.append("duplicate words printed")
    if words != sorted(words):
        problems.append("words are not printed in sorted order")
    for w in words:
        if len(w) != 4 or any(c not in BIKE_OPTIONS[i] for i, c in enumerate(w)):
            problems.append("'%s' cannot be formed from the lock options" % w)
    return not problems, problems


TESTS = [
    Test("Dictionary.py main: bad name", "Dictionary.py",
         [(P_MAIN, "portuguese")], PRELIM_BAD),
    Test("Dictionary.py main: short", "Dictionary.py",
         [(P_MAIN, "short")], PRELIM_SHORT),
    Test("Dictionary.py main: english", "Dictionary.py",
         [(P_MAIN, "english")], PRELIM_ENGLISH),

    Test("app1 short (insertion)", "app1.py",
         [(P_DICT, "short"), (P_ALGO, "1")], APP1_SHORT,
         file_check=("short_sorted.txt", SHORT_SORTED_FILE)),
    Test("app1 short (enhanced insertion)", "app1.py",
         [(P_DICT, "short"), (P_ALGO, "2")], APP1_SHORT_ENH,
         file_check=("short_sorted.txt", SHORT_SORTED_FILE)),
    Test("app1 english (enhanced insertion)", "app1.py",
         [(P_DICT, "english"), (P_ALGO, "2")], APP1_ENGLISH, slow=True),

    Test("app2 french 3000 words", "app2.py",
         [(P_SDICT, "french"), (P_RAND, "3000")], APP2_FRENCH,
         requires=("french_sorted.txt",)),

    Test("app3 english letter", "app3.py",
         [(P_SDICT, "english"), (P_FILE, "letter")], APP3_LETTER,
         requires=("english_sorted.txt",)),
    Test("app3 french sample", "app3.py",
         [(P_SDICT, "french"), (P_FILE, "sample_french")], APP3_FRENCH,
         requires=("french_sorted.txt",)),
    Test("app3 missing file", "app3.py",
         [(P_SDICT, "english"), (P_FILE, "poem")], APP3_POEM,
         requires=("english_sorted.txt",)),

    Test("app4 short tae", "app4.py",
         [(P_DICT, "short"), (P_WORD, "tae")], APP4_TAE),
    Test("app4 short unlucky", "app4.py",
         [(P_DICT, "short"), (P_WORD, "unlucky")], APP4_UNLUCKY),
    Test("app4 english opst", "app4.py",
         [(P_DICT, "english"), (P_WORD, "opst")], APP4_OPST),

    Test("app5 english scrabble", "app5.py",
         [(P_DICT, "english"), (P_LETTERS, "english")], APP5_ENGLISH),

    Test("app6 short lock", "app6.py",
         [(P_SDICT, "short"), (P_NLET, "3"), (P_OPT(1), "c e"),
          (P_OPT(2), "a p"), (P_OPT(3), "t i")], APP6_SHORT,
         requires=("short_sorted.txt",)),
    Test("app6 english bike lock", "app6.py",
         [(P_SDICT, "english"), (P_NLET, "4"),
          (P_OPT(1), "q e t u l s"), (P_OPT(2), "r u f l o q"),
          (P_OPT(3), "k m s a r w"), (P_OPT(4), "w x s o p g")],
         APP6_BIKE, mode="contains", requires=("english_sorted.txt",),
         extra=check_bike),
]

SORTED_COUNTS = {"short": 20, "english": 99171, "french": 139719, "spanish": 86017}

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
TIME_LINE = re.compile(r"(shuffled in|sorted in|sorted with)")
NUM = re.compile(r"\d+(?:\.\d+)?(?:e[-+]?\d+)?")


def normalize(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line.strip())
        if not line:
            continue
        if line.startswith("List of letter combinations:"):
            continue
        if TIME_LINE.search(line):
            line = NUM.sub("<T>", line)
        line = re.sub(r"(Search time is: )[-+\d.eE]+", r"\1<T>", line)
        lines.append(line)
    return lines


def to_transcript(out, answers):
    pos = 0
    for prompt, ans in answers:
        i = out.find(prompt, pos)
        if i == -1:
            continue
        j = i + len(prompt)
        out = out[:j] + ans + "\n" + out[j:]
        pos = j + len(ans) + 1
    return out


def run_script(script, answers, cwd, timeout):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    stdin_text = "\n".join(a for _, a in answers) + "\n"
    try:
        p = subprocess.run([sys.executable, script], input=stdin_text,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=cwd, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "", -1
    return p.stdout, p.stderr, p.returncode


def diff_lines(exp, act):
    d = list(difflib.unified_diff(exp, act, "spec", "yours", lineterm="", n=2))
    if len(d) > 45:
        d = d[:45] + ["... (diff truncated)"]
    return d


def compare(test, actual_text):
    exp = normalize(test.expected)
    act = normalize(actual_text)
    if test.mode == "contains":
        missing = [l for l in exp if l not in act]
        return not missing, ["missing line: %s" % l for l in missing]
    return exp == act, diff_lines(exp, act)


def check_file(cwd, fname, expected):
    path = os.path.join(cwd, fname)
    if not os.path.exists(path):
        return False, ["%s was not created" % fname]
    try:
        with open(path, encoding="utf-8") as f:
            got = [l.strip() for l in f if l.strip()]
    except UnicodeDecodeError as e:
        return False, ["%s is not valid UTF-8: %s" % (fname, e)]
    if got == expected:
        return True, []
    return False, diff_lines(expected, got)


def check_sorted_file(cwd, name, count):
    """<name>_sorted.txt must hold exactly sorted(<name>.txt)."""
    src = os.path.join(cwd, name + ".txt")
    dst = os.path.join(cwd, name + "_sorted.txt")
    try:
        with open(src, encoding="utf-8") as f:
            orig = [l.strip() for l in f]
        with open(dst, encoding="utf-8") as f:
            got = [l.strip() for l in f]
    except UnicodeDecodeError as e:
        return False, ["not valid UTF-8: %s" % e]
    problems = []
    if len(got) != count:
        problems.append("expected %d words, found %d" % (count, len(got)))
    for i in range(len(got) - 1):
        if got[i] > got[i + 1]:
            problems.append("not sorted at line %d: %r > %r" % (i + 1, got[i], got[i + 1]))
            break
    if sorted(orig) != got and not problems:
        problems.append("words differ from %s.txt (lost, added or altered words)" % name)
    return not problems, problems


def report(label, ok, diff, counts):
    if ok:
        print("[PASS] %s" % label)
        counts["PASS"] += 1
    else:
        print("[FAIL] %s" % label)
        for l in diff:
            print("    " + l)
        counts["FAIL"] += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--slow", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}

    def wanted(name):
        return not args.only or args.only.lower() in name.lower()

    for t in TESTS:
        if not wanted(t.name):
            continue
        if t.slow and not args.slow:
            print("[SKIP] %s (slow, use --slow)" % t.name)
            counts["SKIP"] += 1
            continue
        if not os.path.exists(os.path.join(args.dir, t.script)):
            print("[SKIP] %s (%s not found)" % (t.name, t.script))
            counts["SKIP"] += 1
            continue
        missing = [r for r in t.requires if not os.path.exists(os.path.join(args.dir, r))]
        if missing:
            print("[SKIP] %s (missing %s, run app1 first)" % (t.name, ", ".join(missing)))
            counts["SKIP"] += 1
            continue

        timeout = 3600 if t.slow else args.timeout
        out, err, code = run_script(t.script, t.answers, args.dir, timeout)

        if out is None:
            report(t.name + " (timeout)", False, [], counts)
            continue
        if code != 0:
            report("%s (crashed, exit code %d)" % (t.name, code), False,
                   err.strip().split("\n")[-12:], counts)
            continue

        problems = []
        if err.strip():
            problems.append("wrote to stderr:")
            problems += ["  " + l for l in err.strip().split("\n")[-8:]]

        ok, diff = compare(t, to_transcript(out, t.answers))
        if not ok:
            problems += diff
        if t.file_check:
            ok, diff = check_file(args.dir, *t.file_check)
            if not ok:
                problems += ["file %s:" % t.file_check[0]] + diff
        if t.extra:
            ok, diff = t.extra(out)
            if not ok:
                problems += diff

        report(t.name, not problems, problems, counts)

    # integrity of every generated sorted file (includes spanish)
    for name, count in SORTED_COUNTS.items():
        label = "sorted file integrity: %s_sorted.txt" % name
        if not wanted(label):
            continue
        if not os.path.exists(os.path.join(args.dir, name + "_sorted.txt")):
            print("[SKIP] %s (file missing, run app1)" % label)
            counts["SKIP"] += 1
            continue
        ok, diff = check_sorted_file(args.dir, name, count)
        report(label, ok, diff, counts)

    print("\n%d passed, %d failed, %d skipped" %
          (counts["PASS"], counts["FAIL"], counts["SKIP"]))
    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
