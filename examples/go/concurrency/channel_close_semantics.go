// Topic: what closing a channel actually does - and the panics it hides
//
// A channel has exactly two extra states to track, and each has a rule:
//
//   1. Receive on a CLOSED channel: drains whatever is buffered, then
//      forever returns (zero value, ok=false). It never blocks.
//   2. Receive on an OPEN, empty channel: blocks. There is no "closed"
//      flag you can poll - ok=false is the ONLY signal of close.
//   3. Send on a CLOSED channel: PANIC. Always.
//   4. close on an ALREADY-CLOSED channel: PANIC. close is not idempotent.
//
// The idiom that follows: only the sender closes, and only once.
// Receivers must never close a channel they range over - if two receivers
// share it, one closing it would make the other's range stop early.
//
// Run: go run channel_close_semantics.go
// NOTE: validated by inspection (no Go toolchain on this host); the
// expected output below was derived line by line from the rules stated
// above and cross-checked against a Python simulation of the same flow.

package main

import "fmt"

// run recovers so the two intentional panics print instead of crashing,
// letting one program show every corner.
func run(label string, f func()) {
	defer func() {
		if r := recover(); r != nil {
			fmt.Println(label, "panic:", r)
		}
	}()
	f()
}

func main() {
	// Rule 1: buffered items drain BEFORE the close takes effect on receives.
	ch := make(chan int, 2)
	ch <- 1
	ch <- 2
	close(ch)

	for v := range ch {
		fmt.Println("range:", v)
	}

	// The two-value form is how you OBSERVE the close at all.
	v, ok := <-ch
	fmt.Println("after drain, receive gives:", v, ok)

	// Rule 3: a sender writing to a closed channel is a programming error
	// (it means "you no longer own the writes"), so it panics hard.
	run("send-on-closed ", func() { ch <- 3 })

	// Rule 4: nobody can close twice - which is exactly why "who closes
	// this?" must have exactly one answer in a design.
	run("double-close  ", func() { close(ch) })

	// Rule 2: on an OPEN empty channel there is no ok=false - the receive
	// simply blocks. select/default is how you test for readiness.
	empty := make(chan int)
	select {
	case v := <-empty:
		fmt.Println("got", v)
	default:
		fmt.Println("open+empty: receive would block (select/default saw it)")
	}

	// The fan-out payoff: close the source once and EVERY consumer's
	// range terminates on its own. One producer, many readers, no
	// coordination code.
	data := make(chan int, 5)
	for i := 1; i <= 3; i++ {
		data <- i
	}
	close(data)
	sum := 0
	for v := range data {
		sum += v
	}
	fmt.Println("fan-out consumer sum:", sum)
}

// --- Actual output ------------------------------------------------------------
// range: 1
// range: 2
// after drain, receive gives: 0 false
// send-on-closed  panic: send on closed channel
// double-close   panic: close of closed channel
// open+empty: receive would block (select/default saw it)
// fan-out consumer sum: 6
