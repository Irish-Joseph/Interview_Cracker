// Topic: Go generics - type parameters, constraints and type inference.
//
// Before Go 1.18 a reusable Map/Filter/Keys helper meant either interface{}
// plus type assertions (no compile-time safety) or one copy per element type.
// Type parameters give you one implementation that stays fully type-checked.
//
// Concepts:
// - Declaring type parameters: func Name[T any](...)
// - Constraints as interfaces: comparable, ~underlying types, method sets
// - Type inference at the call site (usually no explicit [int] needed)
// - Generic structs and their methods
// - When NOT to reach for generics
//
// Run: go run go/generics/type_parameters_and_constraints.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"fmt"
	"sort"
	"strings"
)

// ---------------------------------------------------------------------------
// 1. `any` - the constraint that allows every type
// ---------------------------------------------------------------------------

// Map converts a []T into a []U. T and U are inferred from the arguments and
// the function literal, so callers write Map(nums, f) not Map[int, string].
func Map[T, U any](items []T, fn func(T) U) []U {
	out := make([]U, 0, len(items))
	for _, item := range items {
		out = append(out, fn(item))
	}
	return out
}

func Filter[T any](items []T, keep func(T) bool) []T {
	out := make([]T, 0, len(items))
	for _, item := range items {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// Reduce needs a separate accumulator type, hence two parameters.
func Reduce[T, A any](items []T, initial A, step func(A, T) A) A {
	acc := initial
	for _, item := range items {
		acc = step(acc, item)
	}
	return acc
}

// ---------------------------------------------------------------------------
// 2. `comparable` - types usable as map keys and with ==
// ---------------------------------------------------------------------------

func Keys[K comparable, V any](m map[K]V) []K {
	keys := make([]K, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	return keys
}

// GroupBy needs K comparable because it becomes a map key.
func GroupBy[T any, K comparable](items []T, classify func(T) K) map[K][]T {
	groups := make(map[K][]T)
	for _, item := range items {
		key := classify(item)
		groups[key] = append(groups[key], item)
	}
	return groups
}

// ---------------------------------------------------------------------------
// 3. Custom constraints - a union of underlying types
// ---------------------------------------------------------------------------

// The ~ means "any type whose *underlying* type is this", so a named type
// such as `type Celsius float64` still satisfies Number.
type Number interface {
	~int | ~int64 | ~float64
}

func Sum[T Number](values []T) T {
	var total T // the zero value of whatever T turned out to be
	for _, v := range values {
		total += v
	}
	return total
}

type Ordered interface {
	~int | ~int64 | ~float64 | ~string
}

func Max[T Ordered](values []T) (T, bool) {
	var best T
	if len(values) == 0 {
		return best, false
	}
	best = values[0]
	for _, v := range values[1:] {
		if v > best {
			best = v
		}
	}
	return best, true
}

type Celsius float64 // underlying type float64, so ~float64 accepts it

// ---------------------------------------------------------------------------
// 4. Constraints can require methods
// ---------------------------------------------------------------------------

type Stringer interface {
	String() string
}

func Join[T Stringer](items []T, sep string) string {
	parts := make([]string, len(items))
	for i, item := range items {
		parts[i] = item.String()
	}
	return strings.Join(parts, sep)
}

type Money struct {
	Cents int
}

func (m Money) String() string {
	return fmt.Sprintf("$%d.%02d", m.Cents/100, m.Cents%100)
}

// ---------------------------------------------------------------------------
// 5. Generic types carry their parameter into their methods
// ---------------------------------------------------------------------------

type Stack[T any] struct {
	items []T
}

func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

// Pop reports ok=false on an empty stack rather than panicking.
func (s *Stack[T]) Pop() (T, bool) {
	var zero T
	if len(s.items) == 0 {
		return zero, false
	}
	last := len(s.items) - 1
	item := s.items[last]
	s.items = s.items[:last]
	return item, true
}

func (s *Stack[T]) Len() int { return len(s.items) }

func main() {
	nums := []int{1, 2, 3, 4, 5, 6}

	// Type inference: no [int, string] needed at the call site.
	labels := Map(nums, func(n int) string { return fmt.Sprintf("#%d", n) })
	evens := Filter(nums, func(n int) bool { return n%2 == 0 })
	total := Reduce(nums, 0, func(acc, n int) int { return acc + n })

	fmt.Println("labels:", labels)
	fmt.Println("evens:", evens)
	fmt.Println("sum via Reduce:", total)

	stock := map[string]int{"apple": 4, "pear": 0, "plum": 7}
	keys := Keys(stock)
	sort.Strings(keys) // map order is random, so sort before printing
	fmt.Println("keys:", keys)

	words := []string{"ant", "bee", "ape", "bat", "cow"}
	groups := GroupBy(words, func(w string) byte { return w[0] })
	fmt.Println("group for byte 'a':", groups['a'])

	fmt.Println("Sum ints:", Sum(nums))
	fmt.Println("Sum floats:", Sum([]float64{1.5, 2.25}))
	fmt.Println("Sum named type:", Sum([]Celsius{20.5, 1.5})) // ~float64 in action

	if best, ok := Max(words); ok {
		fmt.Println("Max string:", best)
	}

	fmt.Println("prices:", Join([]Money{{1250}, {99}, {100000}}, ", "))

	var stack Stack[string]
	stack.Push("first")
	stack.Push("second")
	top, _ := stack.Pop()
	fmt.Printf("popped %q, %d left\n", top, stack.Len())

	// When NOT to use generics: if a function only ever handles one concrete
	// type, or if an ordinary interface already expresses the behaviour, a
	// type parameter just adds noise. Generics pay off when the *shape* of the
	// algorithm is shared but the element type genuinely varies.
}

/* Expected output:
labels: [#1 #2 #3 #4 #5 #6]
evens: [2 4 6]
sum via Reduce: 21
keys: [apple pear plum]
group for byte 'a': [ant ape]
Sum ints: 21
Sum floats: 3.75
Sum named type: 22
Max string: cow
prices: $12.50, $0.99, $1000.00
popped "second", 1 left
*/
