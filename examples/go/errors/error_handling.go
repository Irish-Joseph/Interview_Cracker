// Topic: Go error handling — errors as values.
//
// Concepts:
// - The (T, error) return convention
// - Comparing sentinel errors with errors.Is
// - Unwrapping with %w to build error chains
// - Type-switching on custom errors with errors.As
// - fmt.Errorf for wrapping with context
//
// Go has NO exceptions. Errors are ordinary values returned as the
// LAST return value. The caller decides: handle, wrap and rethrow,
// or propagate. This makes control flow explicit and greppable.
//
// Time Complexity: n/a (idioms, not algorithms)
//
// Run:  go run error_handling.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"errors"
	"fmt"
)

// --- Sentinel errors: predeclared, compared with errors.Is ------------------

var (
	ErrNotFound   = errors.New("not found")
	ErrPermission = errors.New("permission denied")
)

// A custom error TYPE carries structured information.
type InvalidInputError struct {
	Field   string
	Problem string
}

func (e *InvalidInputError) Error() string {
	return fmt.Sprintf("invalid %s: %s", e.Field, e.Problem)
}

// getUser simulates a lookup that can fail in specific ways.
func getUser(id int) (string, error) {
	if id < 0 {
		// %w WRAPS the error, linking it into a chain so callers
		// can still find ErrPermission later with errors.Is.
		return "", fmt.Errorf("getUser(%d): %w", id, ErrPermission)
	}
	if id == 999 {
		return "", ErrNotFound
	}
	if id == 42 {
		return "", &InvalidInputError{Field: "id", Problem: "42 is banned"}
	}
	return fmt.Sprintf("user-%d", id), nil
}

func main() {
	// --- 1. Basic: check the error value ----------------------------------
	name, err := getUser(7)
	if err != nil {
		fmt.Println("unexpected error:", err)
		return
	}
	fmt.Println("ok:", name) // -> ok: user-7

	// --- 2. errors.Is: match sentinel errors anywhere in the chain --------
	_, err = getUser(-1)
	switch {
	case errors.Is(err, ErrPermission):
		fmt.Println("caught: permission denied (via wrapped chain)")
	case errors.Is(err, ErrNotFound):
		fmt.Println("caught: not found")
	default:
		fmt.Println("other error:", err)
	}
	// -> caught: permission denied (via wrapped chain)

	_, err = getUser(999)
	if errors.Is(err, ErrNotFound) {
		fmt.Println("caught: not found")
	}
	// -> caught: not found

	// --- 3. errors.As: extract a specific error TYPE for its data ----------
	_, err = getUser(42)
	var bad *InvalidInputError
	if errors.As(err, &bad) {
		fmt.Printf("caught invalid input on field %q: %s\n",
			bad.Field, bad.Problem)
	}
	// -> caught invalid input on field "id": 42 is banned

	// --- 4. Wrapping with context up the call stack -------------------------
	// Each layer adds its own context with %w; the full chain prints:
	if err := loadReport(999); err != nil {
		fmt.Println("top-level view:", err)
		// -> top-level view: loading report: user lookup: not found
	}
}

// Middle layer: add context, keep the chain intact.
func userLookup(id int) (string, error) {
	name, err := getUser(id)
	if err != nil {
		return "", fmt.Errorf("user lookup: %w", err)
	}
	return name, nil
}

// Top layer: one more level of context.
func loadReport(id int) error {
	if _, err := userLookup(id); err != nil {
		return fmt.Errorf("loading report: %w", err)
	}
	return nil
}
