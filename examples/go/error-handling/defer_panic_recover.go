// Topic: defer, panic and recover - the three traps that make interviews fail
//
// defer is "run this when the surrounding function returns", and its
// semantics have exactly three counter-intuitive corners:
//
//   1. Arguments are evaluated AT THE defer STATEMENT, not at run time.
//      (The function itself is called later, but with the values captured now.)
//   2. Multiple defers run LAST-IN-FIRST-OUT, like nested function returns.
//   3. recover() only works when called DIRECTLY by a deferred function.
//      A panic that skips past the only deferred recover unwinds all the way
//      up and crashes the program.
//
// Bonus: a deferred function CAN still change a NAMED return value, because
// it runs after the return value is assigned but before it is sent back.
//
// Run: go run defer_panic_recover.go
// NOTE: validated by inspection (no Go toolchain on this host); the expected
// output below was derived line by line from the defer ordering rules stated
// above - no timing or platform behaviour is involved.

package main

import "fmt"

// 1. Named return + defer: the defer runs after `result` is set to 21 but
//    before the caller receives it, so the caller sees 42.
func compute() (result int) {
	defer func() { result *= 2 }()
	return 21
}

// 2. The only recover that counts: called directly inside a deferred function.
//    Anything else - a goroutine spawned around the panic, a helper that
//    wraps recover(), recover() on a line after the panic - does NOT catch it.
func mayFail() {
	defer func() {
		if r := recover(); r != nil {
			fmt.Println("recovered:", r)
		}
	}()
	panic("boom")
}

// The version that DOES crash if called: its deferred function never calls
// recover(), so the panic keeps unwinding. (Left uncalled, on purpose.)
func wouldCrash() {
	defer fmt.Println("you will not see this line")
	panic("uncaught")
}

func main() {
	fmt.Println("named return + defer:", compute())

	// Trap 1: the deferred print captured i == 0, not the later 10.
	i := 0
	defer fmt.Println("deferred value:", i)
	i = 10
	fmt.Println("final value:", i)

	// Trap 2: LIFO - the last defer registered is the first to run.
	for k := 0; k < 3; k++ {
		defer fmt.Println("unwinding", k)
	}

	// Trap 3: this panic is caught, because mayFail's deferred function calls
	// recover() directly.
	mayFail()

	fmt.Println("back in main")
}

/*
Expected output:

named return + defer: 42
final value: 10
unwinding 2
unwinding 1
unwinding 0
deferred value: 0
recovered: boom
back in main
*/
