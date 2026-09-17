"""
Challenge:  Daily Temperatures
Pattern:    Monotonic stack
Difficulty: Medium

PROBLEM
-------
Given a list of daily temperatures, return a list where answer[i] is the number
of days you must wait after day i to get a warmer temperature. If no warmer day
exists, answer[i] is 0.

EXAMPLES
--------
[73,74,75,71,69,72,76,73] -> [1,1,4,2,1,1,0,0]
[30,40,50,60]             -> [1,1,1,0]
[30,60,90]                -> [1,1,0]

CONSTRAINTS
-----------
- Aim for O(n). The nested-loop solution is O(n^2).

HINT
----
Scanning forward from each day is O(n^2) and repeats work: if day 3 is colder
than day 4, then anything that warms day 4 also warms day 3.

Walk left to right keeping a stack of days that are still WAITING for a warmer
day. Because each new day is only pushed after resolving everyone it beats, the
temperatures on the stack are always decreasing.

Store indices, not temperatures - you need the index to compute the gap.

COMPLEXITY
----------
Time:  O(n) - every index is pushed once and popped at most once
Space: O(n) - a strictly decreasing input never pops until the end
"""


def daily_temperatures(temperatures: list[int]) -> list[int]:
    answer = [0] * len(temperatures)
    waiting: list[int] = []            # indices, temperatures decreasing

    for day, temperature in enumerate(temperatures):
        # Today resolves every earlier day that was colder.
        while waiting and temperatures[waiting[-1]] < temperature:
            earlier = waiting.pop()
            answer[earlier] = day - earlier

        waiting.append(day)

    # Days left waiting keep their 0 - no warmer day ever came.
    return answer


def _tests() -> None:
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert daily_temperatures([30, 60, 90]) == [1, 1, 0]
    assert daily_temperatures([]) == []
    assert daily_temperatures([50]) == [0]
    assert daily_temperatures([90, 80, 70]) == [0, 0, 0]     # never warmer
    assert daily_temperatures([50, 50, 50]) == [0, 0, 0]     # equal is not warmer

    # Cross-check against the naive O(n^2) scan.
    import random

    def reference(temps: list[int]) -> list[int]:
        out = [0] * len(temps)
        for i in range(len(temps)):
            for j in range(i + 1, len(temps)):
                if temps[j] > temps[i]:
                    out[i] = j - i
                    break
        return out

    random.seed(37)
    for _ in range(400):
        data = [random.randint(30, 40) for _ in range(random.randint(0, 12))]
        assert daily_temperatures(data) == reference(data), data

    print("daily_temperatures: all tests passed (400 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
