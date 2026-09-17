// Topic: Go interfaces — implicit satisfaction, composition and type switches.
//
// Concepts:
// - Interfaces are satisfied IMPLICITLY: no "implements" keyword
// - Small interfaces (one or two methods) are the Go idiom
// - Accept interfaces, return structs
// - Interface composition (io.Writer + io.Closer style)
// - Type assertions and type switches for recovering the concrete type
// - The nil-interface trap: a nil pointer in a non-nil interface
// - Pointer vs value receivers decide WHICH type satisfies the interface
//
// The mental model: an interface value is a pair (concrete type, value).
// Code depends on behaviour, not on a type hierarchy — which is why Go has
// no inheritance and does not need it.
//
// Run:  go run interfaces_and_type_switch.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

// --- 1. A small interface -------------------------------------------------

// Notifier describes behaviour, not a family of types. Any type with this
// method satisfies it, including types in packages that never imported us.
type Notifier interface {
	Notify(message string) error
}

type EmailNotifier struct {
	Address string
}

// Value receiver: both EmailNotifier and *EmailNotifier satisfy Notifier.
func (e EmailNotifier) Notify(message string) error {
	fmt.Printf("   email to %s: %s\n", e.Address, message)
	return nil
}

type SMSNotifier struct {
	Number string
	sent   int
}

// Pointer receiver: only *SMSNotifier satisfies Notifier, because the method
// mutates the struct. Passing SMSNotifier{} where Notifier is wanted will
// not compile.
func (s *SMSNotifier) Notify(message string) error {
	if len(message) > 160 {
		return fmt.Errorf("message too long: %d chars", len(message))
	}
	s.sent++
	fmt.Printf("   sms to %s (#%d): %s\n", s.Number, s.sent, message)
	return nil
}

// notifyAll accepts the interface, so it works with any implementation —
// including test fakes written in the test file.
func notifyAll(targets []Notifier, message string) []error {
	var failures []error
	for _, target := range targets {
		if err := target.Notify(message); err != nil {
			failures = append(failures, err)
		}
	}
	return failures
}

// --- 2. Composition -------------------------------------------------------

type Reader interface{ Read() (string, error) }
type Closer interface{ Close() error }

// An interface can embed others. ReadCloser requires both methods, exactly
// like io.ReadCloser in the standard library.
type ReadCloser interface {
	Reader
	Closer
}

type memoryFile struct {
	lines  []string
	cursor int
	closed bool
}

func (m *memoryFile) Read() (string, error) {
	if m.closed {
		return "", errors.New("read on closed file")
	}
	if m.cursor >= len(m.lines) {
		return "", errEOF
	}
	line := m.lines[m.cursor]
	m.cursor++
	return line, nil
}

func (m *memoryFile) Close() error {
	m.closed = true
	return nil
}

var errEOF = errors.New("end of input")

// drain works with anything that reads and closes.
func drain(rc ReadCloser) (int, error) {
	defer rc.Close()
	count := 0
	for {
		_, err := rc.Read()
		if errors.Is(err, errEOF) {
			return count, nil
		}
		if err != nil {
			return count, err
		}
		count++
	}
}

// --- 3. Type assertions and type switches ---------------------------------

// describe recovers the concrete type behind an interface value.
func describe(value any) string {
	// The comma-ok form never panics; the single-value form does.
	if text, ok := value.(string); ok {
		return fmt.Sprintf("string of %d chars", len(text))
	}

	switch typed := value.(type) {
	case nil:
		return "nil"
	case int, int64:
		return fmt.Sprintf("integer %v", typed)
	case []int:
		sum := 0
		for _, n := range typed {
			sum += n
		}
		return fmt.Sprintf("[]int of %d values, sum %d", len(typed), sum)
	case error:
		return "error: " + typed.Error()
	case Notifier:
		// Interfaces work as cases too: this matches any Notifier.
		return fmt.Sprintf("a notifier (%T)", typed)
	default:
		return fmt.Sprintf("unhandled type %T", typed)
	}
}

// --- 4. The nil-interface trap --------------------------------------------

type auditError struct{ code int }

func (a *auditError) Error() string { return fmt.Sprintf("audit failed (%d)", a.code) }

// BROKEN: returns a non-nil interface holding a nil *auditError.
func brokenCheck(ok bool) error {
	var problem *auditError // nil pointer
	if !ok {
		problem = &auditError{code: 42}
	}
	return problem // the interface is (type=*auditError, value=nil) -> != nil
}

// CORRECT: return the untyped nil literal on the success path.
func fixedCheck(ok bool) error {
	if !ok {
		return &auditError{code: 42}
	}
	return nil
}

func main() {
	fmt.Println("1. implicit satisfaction")
	sms := &SMSNotifier{Number: "+3531234567"}
	targets := []Notifier{
		EmailNotifier{Address: "team@example.com"},
		sms,
	}
	failures := notifyAll(targets, "deploy finished")
	fmt.Printf("   failures: %d, sms counter: %d\n", len(failures), sms.sent)

	long := strings.Repeat("x", 200)
	failures = notifyAll([]Notifier{sms}, long)
	fmt.Printf("   long message failures: %v\n", failures)

	fmt.Println("\n2. composition")
	file := &memoryFile{lines: []string{"alpha", "beta", "gamma"}}
	count, err := drain(file)
	fmt.Printf("   read %d lines, err=%v, closed=%v\n", count, err, file.closed)

	fmt.Println("\n3. type switch")
	values := []any{
		"hello", 7, []int{1, 2, 3}, errors.New("disk full"),
		EmailNotifier{Address: "a@b.c"}, 3.14, nil,
	}
	descriptions := make([]string, 0, len(values))
	for _, v := range values {
		descriptions = append(descriptions, describe(v))
	}
	sort.Strings(descriptions)
	for _, d := range descriptions {
		fmt.Println("   " + d)
	}

	fmt.Println("\n4. the nil-interface trap")
	fmt.Printf("   brokenCheck(true) == nil ? %v  <- surprising\n", brokenCheck(true) == nil)
	fmt.Printf("   fixedCheck(true)  == nil ? %v\n", fixedCheck(true) == nil)
	fmt.Printf("   fixedCheck(false) -> %v\n", fixedCheck(false))

	// Guidance:
	// - Define the interface where it is USED, not next to the implementation.
	// - Keep it to the methods the caller actually calls.
	// - Return concrete types so callers keep every method available.
	// - Reach for a type switch only at boundaries; polymorphism is cleaner.
}
