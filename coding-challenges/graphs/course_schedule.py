"""
Challenge:  Course Schedule (can all courses be finished?)
Pattern:    Topological sort / cycle detection
Difficulty: Medium

PROBLEM
-------
There are numCourses courses labelled 0..numCourses-1. prerequisites[i] =
[a, b] means you must take course b before course a. Return True if you can
finish every course.

EXAMPLES
--------
2, [[1, 0]]           -> True    (take 0, then 1)
2, [[1, 0], [0, 1]]   -> False   (each needs the other first)
3, [[1, 0], [2, 1]]   -> True

CONSTRAINTS
-----------
- There may be courses with no prerequisites at all.
- Duplicate edges are possible.

HINT
----
"Can I order these so every prerequisite comes first?" is exactly a topological
sort. And a topological sort exists if and only if the graph has NO CYCLE -
a cycle is a set of courses that each (transitively) require each other.

So the question "can all courses be finished?" is really "is this directed
graph acyclic?".

Kahn's algorithm: repeatedly take a course with no remaining prerequisites.
If you run out of such courses before placing them all, the rest form a cycle.

COMPLEXITY
----------
Time:  O(V + E)
Space: O(V + E)
"""

from collections import defaultdict, deque


def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    return len(course_order(num_courses, prerequisites)) == num_courses


def course_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """Return a valid ordering, or [] if none exists (i.e. there is a cycle)."""
    unlocks: dict[int, list[int]] = defaultdict(list)   # prereq -> courses it unlocks
    remaining = [0] * num_courses                       # in-degree per course

    for course, prerequisite in prerequisites:
        unlocks[prerequisite].append(course)
        remaining[course] += 1

    # Start with everything that has no prerequisites.
    queue = deque(c for c in range(num_courses) if remaining[c] == 0)
    order: list[int] = []

    while queue:
        course = queue.popleft()
        order.append(course)
        for unlocked in unlocks[course]:
            remaining[unlocked] -= 1
            if remaining[unlocked] == 0:      # all its prerequisites are placed
                queue.append(unlocked)

    # Fewer than num_courses placed means the remainder is a cycle.
    return order if len(order) == num_courses else []


def _tests() -> None:
    assert can_finish(2, [[1, 0]]) is True
    assert can_finish(2, [[1, 0], [0, 1]]) is False          # mutual dependency
    assert can_finish(3, [[1, 0], [2, 1]]) is True
    assert can_finish(1, []) is True                         # no prerequisites
    assert can_finish(0, []) is True                         # no courses
    assert can_finish(3, []) is True                         # all independent
    assert can_finish(3, [[0, 1], [1, 2], [2, 0]]) is False   # 3-cycle
    assert can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) is True   # diamond
    assert can_finish(2, [[1, 0], [1, 0]]) is True           # duplicate edge

    # A self-loop is a cycle of length one.
    assert can_finish(1, [[0, 0]]) is False

    # The returned order must actually satisfy every prerequisite.
    def order_is_valid(n: int, prereqs: list[list[int]], order: list[int]) -> bool:
        position = {course: i for i, course in enumerate(order)}
        return all(position[b] < position[a] for a, b in prereqs)

    for n, prereqs in [(3, [[1, 0], [2, 1]]),
                       (4, [[1, 0], [2, 0], [3, 1], [3, 2]]),
                       (5, [[1, 0], [2, 1], [3, 2], [4, 3]])]:
        order = course_order(n, prereqs)
        assert len(order) == n and order_is_valid(n, prereqs, order), (n, prereqs, order)

    # Randomised: a DAG built from a random topological order is always
    # finishable; adding a back-edge always creates a cycle.
    import random

    random.seed(47)
    for _ in range(300):
        n = random.randint(2, 8)
        labels = list(range(n))
        random.shuffle(labels)                 # labels[i] comes before labels[j] for i<j
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < 0.3:
                    edges.append([labels[j], labels[i]])    # later needs earlier
        assert can_finish(n, edges) is True, (n, edges)

        # A full chain plus a back-edge from the last course to the first
        # is always a cycle, so it must never be finishable.
        chain = [[labels[i + 1], labels[i]] for i in range(n - 1)]
        assert can_finish(n, chain) is True, (n, chain)
        assert can_finish(n, chain + [[labels[0], labels[n - 1]]]) is False

    print("course_schedule: all tests passed (300 randomised DAGs and cycles)")


if __name__ == "__main__":
    _tests()
