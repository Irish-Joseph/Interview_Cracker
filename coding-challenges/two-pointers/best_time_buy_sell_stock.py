"""
Challenge:  Best Time to Buy and Sell One Stock
Pattern:    Two pointers (sweep: one pointer tracks the running minimum)
Difficulty: Easy

PROBLEM
-------
Given a list of daily prices, you may buy on one day and sell on a LATER day,
at most once. Return the maximum profit; return 0 if no profit is possible.

EXAMPLES
--------
[7, 1, 5, 3, 6, 4] -> 5   (buy at 1, sell at 6)
[7, 6, 4, 3, 1]    -> 0   (falling market: do not trade at all)
[2, 4, 1]          -> 2   (the best pair is not (first, last))

CONSTRAINTS
-----------
- 0 <= len(prices) <= 10**5, prices[i] >= 0.
- Buy strictly before sell (same-day round trips are not allowed).
- O(n) time, O(1) extra space.

HINT
----
The O(n^2) approach tries every (buy, sell) pair. But for a FIXED sell day,
the best buy day is just the cheapest price seen strictly before it. Can you
carry that cheapest-so-far forward in one pass?

COMPLEXITY
----------
Time:  O(n) - one pass; each day is visited once
Space: O(1) - just the running minimum and the best profit so far
"""


def max_profit(prices):
    best = 0
    cheapest_so_far = None  # no purchase yet

    for price in prices:
        # Two roles in one pass: this price could be the cheapest BUY
        # (update the minimum) or the best SELL for that minimum.
        if cheapest_so_far is None or price < cheapest_so_far:
            cheapest_so_far = price
        else:
            best = max(best, price - cheapest_so_far)

    return best


def _brute_force(prices):
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best


def _tests() -> None:
    # Empty and single: nothing to trade.
    assert max_profit([]) == 0
    assert max_profit([5]) == 0

    # The case that defeats the "buy first, sell last" reading:
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5

    # Falling market: the answer is 0, not the smallest loss.
    assert max_profit([7, 6, 4, 3, 1]) == 0

    # Best pair is not the endpoints; equal prices; single step up.
    assert max_profit([2, 4, 1]) == 2
    assert max_profit([3, 3, 3]) == 0
    assert max_profit([1, 2]) == 1

    # Cross-check against the brute-force reference on randomised inputs.
    import random
    random.seed(25)
    for _ in range(300):
        n = random.randint(0, 9)
        prices = [random.randint(0, 10) for _ in range(n)]
        assert max_profit(prices) == _brute_force(prices), prices

    print("best_time_buy_sell_stock: all tests passed")


if __name__ == "__main__":
    _tests()
