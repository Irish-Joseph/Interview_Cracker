// Topic: Go slice patterns — append, slicing, copying, filtering.
//
// Concepts:
// - Slices as views into an underlying array (len vs cap)
// - append and its reallocation behavior
// - Sub-slicing with s[i:j] and the three-index form s[i:j:k]
// - Copying a slice properly (never trust a bare slice assignment)
// - The classic filter/transform loop
// - range over slices: index, value
//
// A slice is NOT a copy of the data — it's a small header
// (pointer, length, capacity) pointing at an array. Understanding
// that is the difference between "it worked" and "I know why".
//
// Time Complexity: O(n) for the linear patterns shown
//
// Run:  go run slice_patterns.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import "fmt"

func main() {
	// --- 1. len vs cap -----------------------------------------------------
	numbers := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	fmt.Printf("len=%d cap=%d\n", len(numbers), cap(numbers))

	// A sub-slice shares the SAME backing array.
	middle := numbers[2:5] // [3 4 5]
	fmt.Printf("middle=%v (len=%d cap=%d)\n", middle, len(middle), cap(middle))

	// Mutating the sub-slice mutates the original array!
	middle[0] = 99
	fmt.Printf("after middle[0]=99: numbers[2]=%d\n", numbers[2])
	// -> 99  (shared memory — the #1 slice gotcha)

	// --- 2. append ----------------------------------------------------------
	tiny := []int{1, 2, 3}
	tiny = append(tiny, 4, 5)      // may reuse spare capacity
	fmt.Println("after append:", tiny)

	// --- 3. Copying a slice (the safe way) ----------------------------------
	original := []int{1, 2, 3, 4, 5}
	copied := make([]int, len(original))
	copy(copied, original)          // copies min(len) elements
	copied[0] = 42
	fmt.Printf("original=%v copied=%v\n", original, copied)
	// original is unchanged: copy() is the idiomatic deep copy for
	// slices of value types.

	// --- 4. Filter + transform with a loop ----------------------------------
	evenDoubled := make([]int, 0, len(original)/2) // preallocate-ish
	for _, v := range original {
		if v%2 == 0 {
			evenDoubled = append(evenDoubled, v*2)
		}
	}
	fmt.Println("even values doubled:", evenDoubled)
	// -> [4 8] (from 2 and 4)

	// --- 5. Removing an element by index ------------------------------------
	// The idiomatic in-place removal shifts everything left, then
	// re-slices to drop the now-duplicate last slot.
	items := []string{"a", "b", "c", "d"}
	idx := 1
	items = append(items[:idx], items[idx+1:]...)
	fmt.Println("after removing index 1:", items)
	// -> [a c d]

	// --- 6. In-place reverse --------------------------------------------------
	reversed := []int{1, 2, 3, 4}
	for i, j := 0, len(reversed)-1; i < j; i, j = i+1, j-1 {
		reversed[i], reversed[j] = reversed[j], reversed[i]
	}
	fmt.Println("reversed:", reversed)
	// -> [4 3 2 1]
}
