# Selection Algorithms

### 🟡 Q. How would you find the kth smallest value without fully sorting?

**Answer.** Use **quickselect** for expected O(n) time and O(1) auxiliary space
when mutation is allowed, or keep a size-k heap for O(n log k) time when input
arrives as a stream or must not be rearranged.

Quickselect partitions around a pivot like quicksort, but continues only into
the side containing rank k. Balanced partitions cost
`n + n/2 + n/4 + ... = O(n)`. Repeated bad pivots give an O(n²) worst case, so
real implementations randomize the pivot or use a defensive strategy.

The trade-off is the interview-worthy part: sort for many rank queries, use a
heap for streaming top-k, and quickselect for a one-off query on a mutable
in-memory array.
