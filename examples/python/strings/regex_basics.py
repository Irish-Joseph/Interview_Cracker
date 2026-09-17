"""
Topic: Regular expressions in Python — the everyday patterns.

Concepts:
- re.match / re.search / re.findall (and what they differ in)
- Character classes: \\d, \\w, \\s and [abc]
- Quantifiers: +, *, ?, {n,m}
- Groups () and named groups (?P<name>...)
- Anchors: ^ and $
- re.IGNORECASE and other flags

Regexes describe PATTERNS in text. They are the standard tool for
validation, extraction and cleaning of messy strings — email-ish
checks, parsing logs, masking phone numbers, etc.

Time Complexity: usually O(n) for the patterns below; pathological
cases with nested quantifiers are avoided by writing simple patterns.
"""

import re

text = (
    "Order 1042 placed by user_7 on 2026-09-08 at 14:30:05 "
    "for 2 x widget (SKU AB-123). Support: help@example.com "
    "or call +49 30 123456."
)

# --- 1. match vs search ---------------------------------------------------
# match() only tries at the START of the string; search() scans.
print("match 'Order':", bool(re.match(r"Order", text)))    # True (at start)
print("match 'user':",  bool(re.match(r"user", text)))     # False (not at start)
print("search 'user':", bool(re.search(r"user", text)))    # True (found later)

# --- 2. Character classes ---------------------------------------------------
# \d digit, \w word char, \s whitespace
order_id = re.search(r"Order (\d+)", text)
print("order id:", order_id.group(1))            # -> 1042

timestamps = re.findall(r"\d{2}:\d{2}:\d{2}", text)
print("timestamps:", timestamps)                  # -> ['14:30:05']

# --- 3. Groups and named groups ----------------------------------------------
# Named groups make extracted data self-documenting.
date = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", text)
print("date parts:", date.groupdict())
# -> {'year': '2026', 'month': '09', 'day': '08'}

# --- 4. Quantifiers -----------------------------------------------------------
emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
print("emails found:", emails)                    # -> ['help@example.com']

skus = re.findall(r"SKU \w+-\d+", text)
print("skus found:", skus)                        # -> ['SKU AB-123']

# --- 5. Anchors: whole-string validation ----------------------------------------
def is_phone_number(value: str) -> bool:
    # ^...$ forces the ENTIRE string to match, not just a part.
    return bool(re.fullmatch(r"\+?\d[\d ]{6,14}", value))

for candidate in ["+49 30 123456", "12345", "abc 12345 "]:
    print(f"phone check {candidate!r:18} -> {is_phone_number(candidate)}")
# -> True, False, False (trailing space fails fullmatch)

# --- 6. Cleaning: removing/normalizing with re.sub --------------------------------
raw_tags = "  [INFO] started ,  [ERROR] disk full , [WARN] slow  "
cleaned = re.sub(r"\s+", " ", raw_tags).strip()     # collapse whitespace
normalized = re.sub(r"\[(\w+)\]", r"\1:", cleaned)  # [LEVEL] -> LEVEL:
print("normalized log:", normalized)
# -> INFO: started , ERROR: disk full , WARN: slow

# --- 7. Case-insensitive matching -------------------------------------------------
hits = re.findall(r"support", text, re.IGNORECASE)
print("case-insensitive 'support' hits:", len(hits))  # -> 1

# Cheat sheet:
#   \d \w \s      digit, word, whitespace (and their uppercase negations)
#   .            any char except newline
#   + * ? {n,m}  one+, any, optional, bounded repeat
#   ^ $          start / end (fullmatch = both, enforced)
#   (group)      capture; (?P<name>...) named capture
#   |            alternation:  cat|dog
