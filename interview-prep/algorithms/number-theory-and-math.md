# Number Theory & Math

The math questions that actually come up: GCD, modular arithmetic, primality,
and a handful of bit tricks. None of them require advanced theory — they
require knowing which tool fits which shape of problem.

---

### 🟢 Q. How does the Euclidean algorithm compute a GCD, and why is it fast?

**Answer.** `gcd(a, b) == gcd(b, a % b)`, repeated until the remainder is 0.
Each step shrinks the pair, and the remainder at least halves every two
steps, so it runs in O(log(min(a, b))) — which is why it is the workhorse
behind fraction reduction, CRT, and RSA.

```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

assert gcd(1071, 462) == 21
assert gcd(0, 5) == 5          # gcd(0, x) == x by convention
assert gcd(270, 192) == 6
```

The extended version also returns `x, y` with `a*x + b*y == gcd(a, b)` —
that identity is what makes modular inverses possible at all.

---

### 🟡 Q. When do you need modular arithmetic, and how do you divide "mod p"?

**Answer.** Modulo keeps numbers bounded — hashing, cyclic buffers, "is it
a power of two" checks, and big-prime arithmetic in cryptography. The trap
is division: `a / b mod p` is NOT `(a mod p) / (b mod p)`. You multiply by
the **modular inverse** of `b` instead, which exists only when
`gcd(b, p) == 1` (always true when `p` is prime and `b` is not a multiple
of it).

```python
# "1000 * 7^(mod -1) mod 13" — i.e. 1000/7 mod 13, done by multiplying
# 1000 by the modular inverse of 7.
p = 13
assert pow(7, -1, p) == 2        # 7 * 2 = 14 = 1 (mod 13)
answer = (1000 % p) * pow(7, -1, p) % p
assert answer == 11              # 1000 * 2 = 2000 = 11 (mod 13)
```

When `p` is prime you can also get the inverse from Fermat's little
theorem: `b^(p-2) mod p`. Python's `pow(base, exp, mod)` does fast
modular exponentiation, so this is cheap.

---

### 🟡 Q. Trial division vs a sieve — how do you test or generate primes?

**Answer.** To test ONE number, trial-divide up to its square root (skip
evens after 2): O(√n). To generate ALL primes up to n, use the Sieve of
Eratosthenes: mark multiples of each prime starting at its square, because
smaller multiples were already crossed off. The sieve is roughly
O(n log log n) and beats testing each number individually by a wide margin
once n is large.

```python
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    f = 3
    while f * f <= n:      # only need to test up to sqrt(n)
        if n % f == 0:
            return False
        f += 2
    return True

assert is_prime(2) and is_prime(3) and is_prime(7)
assert not is_prime(1) and not is_prime(0) and not is_prime(2**20)

def sieve(n: int) -> list[int]:
    prime = bytearray([1]) * (n + 1)
    prime[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if prime[i]:
            prime[i * i :: i] = bytearray(len(prime[i * i :: i]))
    return [i for i in range(n + 1) if prime[i]]

assert sieve(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

Starting each marking pass at `i*i` (not `2*i`) is the detail interviewers
probe for: everything below `i*i` that is a multiple of `i` already has a
smaller prime factor and was crossed off earlier.

---

### 🟡 Q. What are the bit tricks you should be able to write without looking up?

**Answer.** With `n` a non-negative int: `n & 1` tests parity; `n & (n-1)`
clears the lowest set bit (and is 0 exactly when `n` is a power of two);
`n | (n-1)` rounds up to the next all-ones mask; `n ^ (n-1)` isolates the
run of low bits. For the count of set bits, either loop-and-clear or
`bin(n).count("1")`.

```python
assert bin(12).count("1") == 2
assert (16 & 15) == 0 and (12 & 11) == 8   # 10000->0, 1100->1000
assert (5 & (5 - 1)) == 4                  # clear lowest set bit: 101 -> 100
assert (7 | (7 - 1)) == 7 and (6 | 5) == 7 # round up to next all-ones
assert ((n := 8) & (n - 1)) == 0            # power of two -> 0
```

The power-of-two test generalises to "is this a valid bitmask / block
size?" checks all over systems code. The XOR identity `a ^ a == 0` and
`a ^ 0 == a` is also how you find the single unpaired element in one pass.

---

### 🔴 Q. You need a/b as a fraction reduced to lowest terms, and a and b
are up to 10^18. What do you do, and what are the overflow traps?

**Answer.** Compute `g = gcd(a, b)` and return `(a//g, b//g)`. The Euclidean
algorithm is safe at that size in Python (arbitrary precision), but in
fixed-width languages the trap is not the GCD — it is anywhere you
**multiply** before dividing. If a problem needs `a * b / c` and you do
the multiplication first, you can overflow even when the final quotient
fits. Reduce by `gcd` factors *before* multiplying, or use a
bignum / `__int128` / `Math.multiplyHigh` equivalent.

```python
from math import gcd

def reduce(a: int, b: int) -> tuple[int, int]:
    g = gcd(a, b)
    return a // g, b // g

assert reduce(462, 1071) == (22, 51)   # gcd is 21
assert reduce(20, 50) == (2, 5)
assert reduce(0, 7) == (0, 1)
assert reduce(10**18, 10**18 - 10**9) == (10**9, 10**9 - 1)
```

The follow-up they will ask: the same for *adding* fractions
`a/b + c/d = (a*d + c*b) / (b*d)` — the numerator and denominator can be
quadratically larger than the inputs, so cross-reduce with
`gcd(a, d)` and `gcd(c, b)` before the big multiply.

---

### 🟢 Q. When is a number a power of two, and how do you find that power?

**Answer.** A positive integer is a power of two exactly when it has a
single set bit: `n > 0 and (n & (n - 1)) == 0`. To find the exponent use
the bit length minus one (`n.bit_length() - 1`), which is O(1) in Python.

```python
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

assert is_power_of_two(1) and is_power_of_two(1024)
assert not is_power_of_two(0) and not is_power_of_two(12)

assert (64).bit_length() - 1 == 6     # 64 == 2**6
```

Why it works: a power of two looks like `1000…0`; subtracting 1 gives
`0111…1`, so the AND is 0. Any number with two or more set bits keeps at
least one bit in common with `n-1`. The `n > 0` guard matters — 0 is `1000
& 0111`-free but is not a power of two.

### 🟡 Q. Why shouldn't I use floating point for money, and what do I use instead?

**Answer.** Because binary floating point cannot represent most decimal
fractions: `0.1` is `0.1000000000000000055511151231257827…` in a `double`,
so `0.1 + 0.2 == 0.3` is `false`. For money the error is not philosophical —
it is a cent that does not match the ledger, and it compounds silently over
aggregations (summing 10⁵ invoices in float drifts by a visible amount).

The standard fix is **fixed point in integer units**: store the *smallest
unit* (cents, millis, satoshis) as an integer. All arithmetic is exact
integer arithmetic; you only divide by 100 when rendering, and round with a
*named* rule (half-up is the usual choice for customer-facing display; be
consistent, because "which rounding" is as much a decision as the number).

Why not just use a `Decimal` type? Often that is fine and simpler — `Decimal`
is exactly fixed-point with a decimal exponent, and it is the right answer
for anything with variable precision (tax rates, exchange rates). The
integer-units approach wins when you need the value to be:

- **Stable on the wire and in the database** — `BIGINT cents` is unambiguous
  across languages; float-as-money is how `3.10` becomes `3.1000000000000001`.
- **Comparable and sortable without scale negotiation** — `Decimal("1.10")`
  and `Decimal("1.1")` are equal, but as *strings* or *scaled integers* you
  must pick one canonical scale and stick to it.
- **Safe against overflow reasoning** — with integers you can state the bound
  ("19 digits of cents covers any realistic total") and check it; float
  overflow is gradual and quiet.

The trap to name even if not asked: **rates are the exception.** "3.99%" is
not a count of a smallest unit; multiplying `cents × rate` needs a real
rational step (integer rate in basis points, or a Decimal), then a final
round to the smallest currency unit — and the rounding rule must be decided
*before* implementation, because half-up vs half-even changes totals over a
month of transactions.

Worked example of the float failure:
[`examples/python/numbers/float_vs_decimal.py`](../../examples/python/numbers/float_vs_decimal.py).

**Follow-up.** "Three friends split $100.00. How do the cents work out?"
Expected: 33.34 + 33.33 + 33.33 — the remainder of the integer division must
be allocated to named parties by rule (e.g. first N parties get the extra
cent), or the split does not sum back to the total, which is exactly the
ledger-mismatch the integer approach is meant to prevent.
