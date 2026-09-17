"""
Topic: Palindrome check and character frequency counting.

Concepts:
- Normalizing input (lowercasing, stripping non-alphanumerics)
- Slicing with a step (`s[::-1]`)
- Counting with collections.Counter

A palindrome reads the same forwards and backwards. Real inputs
have mixed case, spaces and punctuation, so the first step is
always normalizing: keep only letters/digits, lowercase.

Example:
Input:  "A man, a plan, a canal: Panama"
Normalized: "amanaplanacanalpanama"
Output: True

Input:  "race a car"
Output: False

Time Complexity: O(n)
Space Complexity: O(n) for the normalized string / frequency table
"""

from collections import Counter


def normalize(text: str) -> str:
    """Keep only alphanumeric characters, lowercased."""
    return "".join(ch.lower() for ch in text if ch.isalnum())


def is_palindrome(text: str) -> bool:
    normalized = normalize(text)
    # s[::-1] is the idiomatic way to reverse a string.
    return normalized == normalized[::-1]


def char_frequency(text: str) -> dict[str, int]:
    """Count each character of the normalized text."""
    return dict(Counter(normalize(text)))


def top_char(text: str) -> tuple[str, int] | None:
    """Return the most common character (alphabetically first tie-break)."""
    freq = Counter(normalize(text))
    if not freq:
        return None
    # Sort by (count desc, char asc) so ties are deterministic.
    best = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return best


# --- Demo -----------------------------------------------------------------

cases = [
    "A man, a plan, a canal: Panama",  # palindrome
    "race a car",                       # not
    "Was it a car or a cat I saw?",     # palindrome
    "No 'x' in Nixon",                  # palindrome
    "",                                  # empty counts as palindrome
]

for case in cases:
    print(f"{case!r:38} -> palindrome: {is_palindrome(case)}")

sample = "A man, a plan, a canal: Panama"
print()
print(f"char frequencies for {sample!r}:")
for ch, count in sorted(char_frequency(sample).items()):
    print(f"  {ch!r}: {count}")

print(f"most common character: {top_char(sample)}")

# Expected tail output:
#   'a': 10
#   'c': 1
#   'l': 2
#   'm': 2
#   'n': 4
#   'p': 2
# most common character: ('a', 10)
