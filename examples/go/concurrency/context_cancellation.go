// Topic: Cancelling long-running work with context.Context.
//
// Concepts:
// - context.WithCancel for cooperative cancellation
// - select on a channel and ctx.Done()
// - Cancelling from outside a goroutine (main -> worker)
// - Always calling cancel() to release context resources
//
// This file is a standalone example (each Go example in this repo has
// its own main); run it directly: go run context_cancellation.go
//
// Example output (approximate):
//
//	tick
//	tick
//	tick
//	cancel requested
//	context cancelled, worker stopping
//	finished

package main

import (
	"context"
	"fmt"
	"time"
)

// worker emits a "tick" every second until the context is cancelled.
//
// The key pattern is the select statement: each loop iteration waits
// for either a tick timer to fire OR the context to be cancelled,
// whichever happens first.
func worker(ctx context.Context, ticker *time.Ticker) {
	defer ticker.Stop() // avoid leaking the ticker's goroutine

	for {
		select {
		case <-ticker.C:
			fmt.Println("tick")
		case <-ctx.Done():
			// Done() is closed when Cancel() is called (or timeout
			// expires, in timeout contexts). ctx.Err() tells you why.
			fmt.Println("context cancelled, worker stopping:", ctx.Err())
			return
		}
	}
}

func main() {
	// Create a context that main can cancel on demand.
	// cancel must be called (here via defer) even if nothing goes
	// wrong, so the context's internal resources are released.
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	ticker := time.NewTicker(time.Second)

	// The worker runs in its own goroutine so main stays free to
	// decide when to stop it.
	done := make(chan struct{})
	go func() {
		worker(ctx, ticker)
		close(done) // report back to main that the worker exited
	}()

	// Simulate main deciding after 3 seconds that the work is no
	// longer needed. In real code this decision might come from an
	// HTTP request leaving, a user command, or a shutdown signal.
	time.Sleep(3 * time.Second)
	fmt.Println("cancel requested")
	cancel()

	// Wait for the worker to acknowledge and exit cleanly instead
	// of printing "finished" while the worker is still shutting down.
	<-done
	fmt.Println("finished")
}
