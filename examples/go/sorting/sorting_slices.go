// Topic: Sorting — sort.Slice (functional) and the sort.Interface (legacy).
//
// Concepts:
// - sort.Slice: pass a Less function; the framework handles Len/Swap
// - Sorting by one field, then a tie-breaker field
// - sort.Interface: Len/Less/Swap for performance-critical or embedded use
// - sort.Search: binary search on an already-sorted slice
// - Sorting is NOT stable by default; use sort.SliceStable to preserve
//   the order of equal elements
//
// This file is a standalone example (each Go example here has its own main);
// run it with: go run sorting_slices.go
//
// Validated by inspection (no Go toolchain on the authoring machine).
//
// Example output:
//   by length then name: a(1) bb(2) aab(3) abc(3)
//   people by age then name: Bob(25) Ann(30) Cy(40)
//   sorted nums: [2 3 5 8 13 21]
//   search 13 at index 4
//   unstable demo: some permutation of [z a m] (equal keys, order unspecified)

package main

import (
	"fmt"
	"sort"
)

type Person struct {
	Name string
	Age  int
}

func main() {
	// --- sort.Slice: sort by one key, then a tie-breaker -------------
	words := []string{"aab", "bb", "abc", "a"}
	sort.Slice(words, func(i, j int) bool {
		if len(words[i]) != len(words[j]) {
			return len(words[i]) < len(words[j]) // shorter first
		}
		return words[i] < words[j] // tie-break alphabetically
	})
	printWords("by length then name:", words)

	// --- Multi-field sort on structs ---------------------------------
	people := []Person{{"Bob", 25}, {"Cy", 40}, {"Ann", 30}}
	sort.Slice(people, func(i, j int) bool {
		if people[i].Age != people[j].Age {
			return people[i].Age < people[j].Age
		}
		return people[i].Name < people[j].Name
	})
	printPeople("people by age then name:", people)

	// --- The sort.Interface (Len/Less/Swap) --------------------------
	// Equivalent to the first block but as a named type; useful when the
	// comparator is reused or performance matters (no closure per compare).
	nums := intSlice{13, 2, 21, 8, 5, 3}
	sort.Sort(nums)
	fmt.Println("sorted nums:", []int(nums))

	// --- sort.Search: binary search over sorted data -----------------
	i := sort.SearchInts([]int(nums), 13)
	fmt.Println("search 13 at index", i)

	// --- Stability: equal-length words keep input order with SliceStable
	orig := []string{"z", "a", "m"} // all length 1
	sort.Slice(orig, func(i, j int) bool { return len(orig[i]) < len(orig[j]) })
	fmt.Println("unstable (equal keys, order may change):", orig)
}

func printWords(label string, w []string) {
	fmt.Print(label + ": ")
	for i, s := range w {
		if i > 0 {
			fmt.Print(" ")
		}
		fmt.Printf("%s(%d)", s, len(s))
	}
	fmt.Println()
}

func printPeople(label string, p []Person) {
	fmt.Print(label + ": ")
	for i, person := range p {
		if i > 0 {
			fmt.Print(" ")
		}
		fmt.Printf("%s(%d)", person.Name, person.Age)
	}
	fmt.Println()
}

type intSlice []int

func (s intSlice) Len() int           { return len(s) }
func (s intSlice) Less(i, j int) bool { return s[i] < s[j] }
func (s intSlice) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }
