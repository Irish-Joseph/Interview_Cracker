"""
Topic: float vs Decimal - where 0.1 + 0.2 breaks, and why

float holds a binary approximation, so 0.1 + 0.2 is 0.30000000000000004.
Decimal is base-10 and exact for the strings you give it - but only if you
construct it from a *string*. Decimal(0.1) lifts the float's inexact value
and "fixes" nothing.

Run: python float_vs_decimal.py
"""

from decimal import Decimal, ROUND_HALF_UP

print("== floats are binary approximations ==")
print(f"0.1 + 0.2            = {0.1 + 0.2!r}")
print(f"0.1 + 0.2 == 0.3     : {0.1 + 0.2 == 0.3}")
print(f"1.1 * 3              = {1.1 * 3!r}")

# The usual band-aid: compare with a tolerance, or round for display.
print(f"abs diff < 1e-9      : {abs((0.1 + 0.2) - 0.3) < 1e-9}")
print(f"round for display    : {round(0.1 + 0.2, 10)}")

print()
print("== Decimal is base-10 - but only from strings ==")
print(f"Decimal('0.1') + Decimal('0.2') = {Decimal('0.1') + Decimal('0.2')}")
print(f"Decimal(0.1)                    = {Decimal(0.1)}   <- float lifted, inexactness kept")
print(f"Decimal(0.1) == Decimal('0.1')  : {Decimal(0.1) == Decimal('0.1')}")

print()
print("== money: exact arithmetic, exact rounding ==")
prices = [Decimal("19.99"), Decimal("5.50"), Decimal("3.33")]
total = sum(prices)
print(f"19.99 + 5.50 + 3.33 = {total}")
# A percentage computed the float way, and the Decimal way.
# (float * Decimal is a TypeError, so cast first - itself a signal
#  that the two systems are deliberately kept apart)
discount_f = 0.07 * float(total)
discount_d = total * Decimal("0.07")
print(f"7% off, float   : {discount_f!r}")
print(f"7% off, Decimal : {discount_d}")
# HALF_UP is what people expect from "rounding"; the default is HALF_EVEN.
print(f"Decimal('2.5').quantize(0, HALF_UP)   = {Decimal('2.5').quantize(Decimal('1'), rounding=ROUND_HALF_UP)}")
print(f"Decimal('3.5').quantize(0, HALF_UP)   = {Decimal('3.5').quantize(Decimal('1'), rounding=ROUND_HALF_UP)}")
print(f"Decimal('2.5') default (HALF_EVEN)    = {Decimal('2.5').quantize(Decimal('1'))}")

print()
print("== cost of Decimal: speed ==")
import timeit
t_float = timeit.timeit("0.1 + 0.2 + 0.3", number=1_000_000)
t_dec = timeit.timeit("Decimal('0.1') + Decimal('0.2') + Decimal('0.3')",
                      globals={"Decimal": Decimal}, number=1_000_000)
print(f"1M float adds   : {t_float:.3f}s")
print(f"1M Decimal adds : {t_dec:.3f}s  (about {t_dec / t_float:.0f}x slower)")

print()
print("== rule of thumb ==")
print("floats: geometry, physics, graphics, anything approximate and fast")
print("Decimal: money, taxes, invoices - build from strings, pick a rounding")
