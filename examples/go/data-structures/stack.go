// Topic: Implement a LIFO stack using a slice.
//
// Concepts:
// - Structs with unexported fields
// - Methods with pointer receivers (mutation)
// - Slices as the backing storage
// - The ok-pattern: returning (value, ok bool)
// - Cap growth vs fixed-size (grows automatically here)
//
// A stack is Last-In-First-Out: Push adds to the top, Pop removes
// from the top. A slice is a natural fit because append and
// len(s)-1 are both O(1) amortized.
//
// Time Complexity: Push O(1) amortized, Pop O(1), Top O(1), Len O(1)
// Space Complexity: O(n)
//
// Run:  go run stack.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import "fmt"

// Stack is a LIFO container of ints backed by a slice.
type Stack struct {
	items []int // items[0] is the bottom, items[len-1] the top
}

// NewStack returns an empty stack.
func NewStack() *Stack {
	return &Stack{}
}

// Push adds a value on top of the stack.
func (s *Stack) Push(value int) {
	s.items = append(s.items, value)
}

// Pop removes and returns the top value.
// ok is false when the stack is empty.
func (s *Stack) Pop() (int, bool) {
	n := len(s.items)
	if n == 0 {
		return 0, false
	}
	top := s.items[n-1]
	s.items = s.items[:n-1] // drop the last element
	return top, true
}

// Top peeks at the top value without removing it.
func (s *Stack) Top() (int, bool) {
	if len(s.items) == 0 {
		return 0, false
	}
	return s.items[len(s.items)-1], true
}

// Len reports how many values are on the stack.
func (s *Stack) Len() int {
	return len(s.items)
}

// IsEmpty is a convenience wrapper.
func (s *Stack) IsEmpty() bool {
	return len(s.items) == 0
}

func main() {
	stack := NewStack()

	// Push a few values.
	for _, v := range []int{10, 20, 30} {
		stack.Push(v)
	}
	fmt.Printf("after pushing 10, 20, 30: len=%d top=", stack.Len())
	top, _ := stack.Top()
	fmt.Println(top) // -> 30

	// Pop everything; LIFO order means 30 comes out first.
	for !stack.IsEmpty() {
		v, _ := stack.Pop()
		fmt.Print(v, " ")
	}
	fmt.Println() // -> 30 20 10

	// Popping an empty stack uses the ok-pattern.
	if v, ok := stack.Pop(); ok {
		fmt.Println("unexpected:", v)
	} else {
		fmt.Println("pop on empty stack: ok=false (no panic)")
	}
}

// Expected output:
//
//	after pushing 10, 20, 30: len=3 top=30
//	30 20 10
//	pop on empty stack: ok=false (no panic)
