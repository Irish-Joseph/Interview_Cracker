// Topic: Go map patterns — safe access, counting, grouping, deletion.
//
// Concepts:
// - The (value, ok) comma-ok idiom for reads
// - Maps are reference types (copies share data)
// - make(map[...]) and the nil-map pitfall
// - idiom: map[key] = map[key] + 1 for counting
// - Grouping slices into maps of slices
// - Iteration order is deliberately RANDOM
//
// A map is a hash table with O(1) average lookups. The patterns
// below are the idioms you will see in almost every Go codebase.
//
// Time Complexity: O(n) for the linear passes shown
//
// Run:  go run map_patterns.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"fmt"
	"sort"
)

func main() {
	// --- 1. The comma-ok idiom ------------------------------------------------
	// A missing key returns the zero value, which is ambiguous with a
	// real stored zero value. The two-form lookup removes the ambiguity.
	ages := map[string]int{"alice": 30, "bob": 0} // bob's 0 is REAL data

	v, ok := ages["carol"]
	fmt.Printf("carol: value=%d ok=%t\n", v, ok) // -> 0 false (absent)

	v, ok = ages["bob"]
	fmt.Printf("bob:   value=%d ok=%t\n", v, ok) // -> 0 true  (present!)

	// --- 2. Counting: the map[k] = map[k]+1 idiom -------------------------------
	words := []string{"go", "maps", "are", "go", "great", "maps"}
	freq := make(map[string]int)
	for _, w := range words {
		freq[w]++ // absent keys start at the zero value 0
	}
	fmt.Println("frequencies:", freq)
	// -> map[are:1 go:2 great:1 maps:2]

	// --- 3. Grouping: map of slices ----------------------------------------------
	people := []struct{ Name, Dept string }{
		{"Alice", "eng"}, {"Bob", "sales"}, {"Carol", "eng"}, {"Dan", "sales"},
	}
	byDept := make(map[string][]string)
	for _, p := range people {
		byDept[p.Dept] = append(byDept[p.Dept], p.Name)
	}
	fmt.Println("by dept:", byDept)
	// -> map[eng:[Alice Carol] sales:[Bob Dan]]

	// --- 4. Iteration order is random: sort keys for stable output ----------------
	// Never rely on map range order (it's intentionally randomized).
	keys := make([]string, 0, len(freq))
	for k := range freq {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	fmt.Print("sorted keys: ")
	for _, k := range keys {
		fmt.Printf("%s(%d) ", k, freq[k])
	}
	fmt.Println()
	// -> are(1) go(2) great(1) maps(2)

	// --- 5. Deletion: delete(k, m) is safe on missing keys -------------------------
	delete(freq, "go")
	fmt.Println("after delete go:", freq)
	// -> map[are:1 great:1 maps:2]

	// --- 6. Maps are reference types ------------------------------------------------
	first := map[string]int{"x": 1}
	second := first      // same underlying map!
	second["y"] = 2
	fmt.Println("first sees y too:", first)
	// -> map[x:1 y:2]  (assignment of a map variable copies only the header)

	// Delete an entry vs clear the whole map (Go 1.21+):
	clear(freq)
	fmt.Println("after clear:", freq) // -> map[]
}
