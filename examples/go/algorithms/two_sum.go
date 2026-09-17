// Topic: Two Sum — find two numbers that add to a target.
//
// Concepts:
// - Slices and range loops
// - Maps for O(1) "have I seen this value?" lookups
// - The single-pass hash map algorithm
// - Returning (values, ok) idioms
//
// Given a slice of ints and a target, return the two values that sum
// to target. The classic O(n) approach: while scanning, store each
// value's index in a map; for each number x, check whether
// (target - x) was seen before.
//
// Time Complexity: O(n) — one pass, O(1) map operations
// Space Complexity: O(n) — the map
//
// Run:  go run two_sum.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import "fmt"

// twoSum returns a pair of values from nums that add up to target,
// along with their indices. The ok result is false when no pair exists.
func twoSum(nums []int, target int) (int, int, [2]int, bool) {
	// seen maps a value to the index where it first appeared.
	seen := make(map[int]int)

	for i, x := range nums {
		need := target - x
		if j, ok := seen[need]; ok {
			// `need` was seen at index j — we found the pair.
			return need, x, [2]int{j, i}, true
		}
		seen[x] = i
	}

	return 0, 0, [2]int{-1, -1}, false
}

func main() {
	cases := []struct {
		nums   []int
		target int
	}{
		{[]int{2, 7, 11, 15}, 9},  // -> 2 + 7
		{[]int{3, 2, 4}, 6},       // -> 2 + 4
		{[]int{1, 2, 3}, 100},     // -> no pair
		{[]int{-1, -2, -3}, -5},   // -> -2 + -3 (works with negatives)
	}

	for _, c := range cases {
		a, b, idx, ok := twoSum(c.nums, c.target)
		if !ok {
			fmt.Printf("nums=%v target=%d  -> no pair found\n", c.nums, c.target)
		} else {
			fmt.Printf("nums=%v target=%d  -> %d + %d = %d (indices %v)\n",
				c.nums, c.target, a, b, a+b, idx)
		}
	}
}

// Expected output:
//
//	nums=[2 7 11 15] target=9  -> 2 + 7 = 9 (indices [0 1])
//	nums=[3 2 4] target=6  -> 2 + 4 = 6 (indices [1 2])
//	nums=[1 2 3] target=100  -> no pair found
//	nums=[-1 -2 -3] target=-5  -> -2 + -3 = -5 (indices [1 2])
