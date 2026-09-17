"""
Challenge:  Coin Change (fewest coins)
Pattern:    Unbounded knapsack DP
Difficulty: Medium

PROBLEM
-------
Given coin denominations and a target amount, return the fewest coins needed to
make that amount. You have an unlimited supply of each coin. Return -1 if the
amount cannot be made.

EXAMPLES
--------
coins=[1,3,4], amount=6   -> 2    (3+3, NOT 4+1+1)
coins=[1,2,5], amount=11  -> 3    (5+5+1)
coins=[2],     amount=3   -> -1
coins=[1],     amount=0   -> 0

CONSTRAINTS
-----------
- Coins may be used any number of times.
- The amount may be 0.

HINT
----
Greedy (always take the largest coin that fits) is WRONG here. With coins
[1,3,4] and amount 6 it gives 4+1+1 = three coins, but 3+3 = two is better.
That failure is the whole reason this needs DP.

Define fewest[a] = the minimum coins to make amount a. To make a, you must have
placed some coin c last, leaving a-c - so try every coin and take the best.

Build upward from 0, and use a sentinel (infinity) for "not yet reachable" so
that unreachable amounts never look cheap.

COMPLEXITY
----------
Time:  O(amount * len(coins))
Space: O(amount)
"""


def coin_change(coins: list[int], amount: int) -> int:
    if amount < 0:
        return -1

    # fewest[a] = minimum coins to make amount a; infinity = unreachable.
    fewest = [0] + [float("inf")] * amount

    for current in range(1, amount + 1):
        for coin in coins:
            if coin <= current and fewest[current - coin] + 1 < fewest[current]:
                fewest[current] = fewest[current - coin] + 1

    return -1 if fewest[amount] == float("inf") else int(fewest[amount])


def _tests() -> None:
    assert coin_change([1, 3, 4], 6) == 2          # the case greedy gets wrong
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1
    assert coin_change([1], 0) == 0
    assert coin_change([], 0) == 0
    assert coin_change([], 5) == -1
    assert coin_change([5], 5) == 1
    assert coin_change([1, 2, 5], 100) == 20
    assert coin_change([186, 419, 83, 408], 6249) == 20
    assert coin_change([2, 5], 3) == -1
    assert coin_change([1, 2, 5], -1) == -1

    # Greedy really is wrong here - demonstrate it rather than assert it.
    def greedy(coins: list[int], amount: int) -> int:
        used = 0
        for coin in sorted(coins, reverse=True):
            take = amount // coin
            used += take
            amount -= take * coin
        return used if amount == 0 else -1

    assert greedy([1, 3, 4], 6) == 3 and coin_change([1, 3, 4], 6) == 2

    # Cross-check against BFS, which finds the fewest coins by construction.
    from collections import deque
    import random

    def reference(coins: list[int], amount: int) -> int:
        if amount == 0:
            return 0
        if not coins:
            return -1
        seen = {0}
        queue = deque([(0, 0)])
        while queue:
            total, used = queue.popleft()
            for coin in coins:
                nxt = total + coin
                if nxt == amount:
                    return used + 1
                if nxt < amount and nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, used + 1))
        return -1

    random.seed(53)
    for _ in range(300):
        coins = random.sample(range(1, 12), random.randint(1, 4))
        amount = random.randint(0, 40)
        assert coin_change(coins, amount) == reference(coins, amount), (coins, amount)

    print("coin_change: all tests passed (300 randomised cross-checks vs BFS)")


if __name__ == "__main__":
    _tests()
