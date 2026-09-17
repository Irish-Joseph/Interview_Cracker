// Topic: Rate limiter using channels (token bucket).
//
// Concepts:
// - Goroutines as a background "refill" worker
// - Channels as a bounded token bucket
// - The ctx (context) pattern for clean shutdown
// - Non-blocking select for "try" semantics
//
// The bucket holds at most `capacity` tokens. A background
// goroutine adds one token every `interval`. A caller may either
// wait for a token (Allow) or check immediately (TryAllow).
//
// This is the classic way to answer "limit to N requests per
// period" in idiomatic Go: no mutexes, just channels.
//
// Run:  go run token_bucket_rate_limiter.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"context"
	"fmt"
	"time"
)

// TokenBucket is a rate limiter that releases at most
// rate tokens per second, with bursts up to capacity.
type TokenBucket struct {
	tokens chan struct{} // each empty struct is one token
	cancel context.CancelFunc
}

// NewTokenBucket creates a bucket that starts FULL (capacity tokens)
// and refills one token every interval.
func NewTokenBucket(capacity int, interval time.Duration) *TokenBucket {
	tokens := make(chan struct{}, capacity)
	for i := 0; i < capacity; i++ {
		tokens <- struct{}{} // start with a full bucket
	}

	// Refill worker: one token per interval, until context is done.
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				// Non-blocking fill: if the bucket is already full
				// (callers are slow), the token is simply discarded.
				select {
				case tokens <- struct{}{}:
				default:
				}
			}
		}
	}()

	return &TokenBucket{tokens: tokens, cancel: cancel}
}

// Allow blocks until a token is available (or the bucket is stopped).
func (tb *TokenBucket) Allow() {
	<-tb.tokens
}

// TryAllow reports whether a token is available right now,
// taking it if so. It never blocks.
func (tb *TokenBucket) TryAllow() bool {
	select {
	case <-tb.tokens:
		return true
	default:
		return false
	}
}

// Stop shuts down the refill worker.
func (tb *TokenBucket) Stop() {
	tb.cancel()
}

func main() {
	// Limit: max 2 tokens, refill 1 token every 500ms
	// => sustained 2 req/s, burst of 2.
	limiter := NewTokenBucket(2, 500*time.Millisecond)
	defer limiter.Stop()

	// Fire 5 requests as fast as the limiter allows.
	start := time.Now()
	for i := 1; i <= 5; i++ {
		limiter.Allow()
		elapsed := time.Since(start).Round(time.Millisecond)
		fmt.Printf("request %d served at %v\n", i, elapsed)
	}

	fmt.Println()

	// Demonstrate the non-blocking variant:
	fresh := NewTokenBucket(1, time.Hour) // effectively no refill
	defer fresh.Stop()

	fmt.Println("try 1:", fresh.TryAllow()) // true  (bucket starts full)
	fmt.Println("try 2:", fresh.TryAllow()) // false (empty, no refill)
}

// Expected output (approximate):
//
//	request 1 served at 0ms
//	request 2 served at 0ms
//	request 3 served at 500ms
//	request 4 served at 1s
//	request 5 served at 1.5s
//
//	try 1: true
//	try 2: false
