"""
Challenge:  Meeting Rooms II (minimum rooms required)
Pattern:    Sort by start + min-heap of end times
Difficulty: Medium

PROBLEM
-------
Given meeting time intervals [start, end], return the minimum number of
conference rooms required to hold them all.

EXAMPLES
--------
[[0,30],[5,10],[15,20]] -> 2
[[7,10],[2,4]]          -> 1    (they do not overlap)
[[1,5],[2,6],[3,7]]     -> 3    (all three overlap at time 3)

CONSTRAINTS
-----------
- A meeting ending at time t and another starting at t can share a room.

HINT
----
The answer is the maximum number of meetings happening at any single moment.

Two ways to see it:

(a) Sort by start time and keep a MIN-HEAP of the end times of meetings
    currently in progress. For each new meeting, if the earliest-ending meeting
    has already finished, reuse that room (pop it). Push the new end time. The
    heap size is the number of rooms in use; its maximum is the answer.

(b) The "chronological" trick: treat each start as +1 and each end as -1, sort
    all these events by time (ends before starts at equal times), and sweep.
    The running maximum is the answer.

Both are implemented below and must always agree.

COMPLEXITY
----------
Time:  O(n log n)
Space: O(n)
"""

import heapq


def min_meeting_rooms(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0

    ordered = sorted(intervals, key=lambda interval: interval[0])
    in_progress: list[int] = []          # min-heap of end times

    for start, end in ordered:
        # The earliest-ending meeting has finished, so its room is free.
        # A meeting ending exactly when this one starts can hand over its room.
        if in_progress and in_progress[0] <= start:
            heapq.heappop(in_progress)

        heapq.heappush(in_progress, end)

    # Everything left on the heap overlapped at some point.
    return len(in_progress)


def min_meeting_rooms_sweep(intervals: list[list[int]]) -> int:
    """Event sweep: +1 at each start, -1 at each end."""
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))

    # Sort by time; at equal times process the -1 first, so a room freed at
    # time t can be reused by a meeting starting at t.
    events.sort(key=lambda event: (event[0], event[1]))

    current = busiest = 0
    for _, delta in events:
        current += delta
        busiest = max(busiest, current)
    return busiest


def _tests() -> None:
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
    assert min_meeting_rooms([[1, 5], [2, 6], [3, 7]]) == 3
    assert min_meeting_rooms([]) == 0
    assert min_meeting_rooms([[1, 2]]) == 1
    assert min_meeting_rooms([[1, 2], [2, 3]]) == 1          # back-to-back
    assert min_meeting_rooms([[1, 3], [2, 4], [5, 6]]) == 2
    assert min_meeting_rooms([[1, 10], [2, 3], [4, 5]]) == 2

    # Both implementations must agree, and must match a brute-force sweep
    # over every integer point in time.
    import random

    def reference(intervals: list[list[int]]) -> int:
        if not intervals:
            return 0
        busiest = 0
        latest = max(end for _, end in intervals)
        for moment in range(latest + 1):
            # A meeting occupies its room over [start, end).
            concurrent = sum(1 for start, end in intervals if start <= moment < end)
            busiest = max(busiest, concurrent)
        return busiest

    random.seed(61)
    for _ in range(300):
        data = []
        for _ in range(random.randint(0, 8)):
            start = random.randint(0, 20)
            data.append([start, start + random.randint(1, 8)])

        heap_answer = min_meeting_rooms(data)
        sweep_answer = min_meeting_rooms_sweep(data)
        assert heap_answer == sweep_answer == reference(data), (data, heap_answer, sweep_answer)

    print("meeting_rooms: all tests passed (300 randomised cases, both variants)")


if __name__ == "__main__":
    _tests()
