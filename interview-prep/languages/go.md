# Go

Go interviews focus on the concurrency model (goroutines + channels),
explicit error handling, and the small set of language rules that differ
from C-family intuition (no inheritance, no exceptions, `interface{}`
everywhere). (Snippets below validated by inspection — no Go toolchain on
the authoring machine.)

---

### 🟢 Q. What is a goroutine, and how is it different from a thread?

**Answer.** A goroutine is a function executed concurrently by the Go
**runtime**, not the OS. The runtime multiplexes thousands of them onto a
small pool of OS threads (the GMP model: Goroutines, runnables on
Machine threads, driven by Ps). A goroutine starts at ~2KB of stack that
grows on demand, versus ~1-8MB fixed for an OS thread — so spawning them
is cheap, and the idiom is one goroutine per connection/task rather than a
thread pool you size by hand.

```go
package main

import "fmt"

func worker(id int, out chan<- int) {
    out <- id * id   // blocks until the value is received
}

func main() {
    out := make(chan int, 3) // buffered: workers never block
    for i := 1; i <= 3; i++ {
        go worker(i, out)    // start a goroutine
    }
    for i := 1; i <= 3; i++ {
        fmt.Println(<-out)   // 1, 4, 9 — in some order
    }
}
```

The key mental shift: concurrency is **explicit dataflow**. Goroutines
communicate by sending/receiving on channels, and a send on an unbuffered
channel *blocks* until the other side is ready — that blocking is the
synchronisation, not a lock.

---

### 🟡 Q. Buffered vs unbuffered channels — when does each cause a
goroutine to block?

**Answer.** An **unbuffered** channel is a direct handoff: send blocks
until a receiver is waiting, and receive blocks until a sender is waiting.
A **buffered** channel of size N absorbs up to N values without a waiting
peer; send blocks only when the buffer is full, receive only when it is
empty.

```go
ch := make(chan int)      // unbuffered
ch <- 1                   // BLOCKS forever here: no receiver yet

bch := make(chan int, 2)  // buffered, capacity 2
bch <- 1                  // fine: goes into the buffer
bch <- 2                  // fine: buffer full now
// bch <- 3               // would BLOCK: buffer full, no receiver
```

The classic deadlock is a send on an unbuffered channel (or a full buffer)
with nobody receiving — the runtime kills the program when every goroutine
is blocked. Rule of thumb: use unbuffered channels when you want strict
handoff/synchronisation, buffered channels when you want to decouple
producer and consumer rates or absorb bursts.

---

### 🟡 Q. How does Go handle errors, and why no exceptions?

**Answer.** Errors are **values**: fallible functions return an extra
`error` (an interface), and the caller checks it explicitly, usually
immediately. There are no exceptions, so there is no hidden control flow
and no "this call might throw halfway through" reasoning — every failure
point is visible at the call site.

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

func main() {
    r, err := divide(10, 2)
    if err != nil {
        fmt.Println("error:", err)  // handle the failure explicitly
        return
    }
    fmt.Println(r) // 5
}
```

The standard library's `errors.Is` / `errors.As` and the `%w` wrap verb let
you **wrap** errors to add context while keeping the original checkable:
`fmt.Errorf("reading config: %w", err)` means `errors.Is(wrapped,
os.ErrNotExist)` still matches the underlying `os.ErrNotExist`. The trade-
off to state: verbosity (the `if err != nil` dance) in exchange for
explicitness — and the idiomatic fix for deep chains is to let `?`-style
helpers or a single early return at each boundary do the work.

---

### 🟡 Q. What are interfaces in Go, and why is `io.Reader` so central?

**Answer.** An interface is a set of method requirements, and a type
satisfies it **implicitly** by implementing the methods — no `implements`
keyword. This makes interfaces small and adopted at the point of use: a
function takes `io.Reader` (a single `Read([]byte) (int, error)`) and can
be handed a file, a network connection, a `bytes.Buffer`, or your own
type, with no changes.

```go
// Anything with Read(p []byte) (int, error) is an io.Reader.
type MySource struct{ data []byte; pos int }

func (m *MySource) Read(p []byte) (int, error) {
    if m.pos >= len(m.data) {
        return 0, io.EOF
    }
    n := copy(p, m.data[m.pos:])
    m.pos += n
    return n, nil
}

// Now this generic decoder works on files, HTTP bodies, AND MySource:
func decode(r io.Reader) ([]byte, error) { return io.ReadAll(r) }
```

The design principle: **accept interfaces, return concrete types**. Small
interfaces (1-3 methods) keep things composable — `io.Reader`,
`io.Writer`, `io.Closer` combine into `io.ReadWriter`, `io.ReadCloser`,
etc. The flip side to mention: implicit satisfaction can make it hard to
find what implements an interface, and empty `interface{}`/`any` erases
type safety until you assert.

---

### 🔴 Q. A goroutine leaks in your service. What does that mean, how do
you find it, and how do you fix it?

**Answer.** A **goroutine leak** is a goroutine that can never finish —
usually blocked forever on a channel send/receive, a lock, or a `select`
with no ready case and no exit path. Each one holds its stack and any
closures (and the data they reference), so a leak is a slow memory growth
plus lost work, and it shows up as "goroutine count climbs linearly with
requests" in a runtime profile.

How you find it: the runtime traceback (`/debug/pprof/goroutine?debug=1`
or `go tool pprof`) groups leaked goroutines by the stack they're blocked
on — you'll see hundreds parked in `<-ch` or `select`. The fixes, in order
of idiom:

1. **Context cancellation** — thread a `context.Context` into long-running
   goroutines and `select` on `ctx.Done()` so a cancelled request can
   unblock its workers.
2. **Ensure every channel send has a receiver** (or a buffer that will be
   drained) — the usual leak is `resultCh <- x` where the caller already
   gave up and never receives.
3. **Prefer `select` with an exit case** over a bare `<-ch`, and close
   channels from a single owner so receivers can detect shutdown via the
   zero value.

The answer they're looking for is the mental model: a goroutine is only as
dead as its last blocking operation, so "leak" almost always means "someone
stopped receiving (or stopped cancelling) and this goroutine is waiting on
it forever."
