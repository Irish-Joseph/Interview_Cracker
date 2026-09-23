# C# Interview Questions

---

### 🟢 Q. Value types vs reference types — and where does each one live?

**Answer.** Value types (`int`, `struct`, `enum`) are stored **in place** —
on the stack when local, inline inside the object that contains them — and
are copied wholesale on assignment. Reference types (`class`, `string`,
`delegate`, arrays) store a reference; the object lives on the **managed
heap** and assignment copies the reference, not the object.

The follow-ups that separate a definition from understanding:

- `string` is a reference type that behaves like a value type: it is
  **immutable**, so "copying" it is just passing the reference around —
  there is never a mutation to share. That immutability is why strings can
  be interned and compared by value with `==`.
- A `struct` that holds a `string` or another class is a value type with
  reference-type *fields* — copying the struct copies the fields' references,
  so both copies see the same heap object. Value semantics stop at the first
  indirection.
- The interop cost: a `struct` boxed to `object` (or put in an
  `ArrayList`-style `object` collection) is copied to the heap — boxing is
  how value types pay the reference-type price.

See [`examples/csharp/basics/value_vs_reference_types.cs`](../../examples/csharp/basics/value_vs_reference_types.cs).

---

### 🟢 Q. `==` vs `.Equals()` vs `ReferenceEquals` — when do they disagree?

**Answer.** `ReferenceEquals(a, b)` (and `object.ReferenceEquals`) asks
"same object on the heap?" `a == b` is an operator: for most reference types
it **calls** `Equals`, but `string` and types that overload `==` decide
otherwise. `a.Equals(b)` is the virtual value-equality method.

The disagreements that actually bite:

- **`string`**: `"a" == "b"` compares *content* (the `==` operator for string
  is special-cased to do value equality, and treats nulls as equal to null).
  `ReferenceEquals("a", "a")` can be false — two equal strings are not
  necessarily the same interned instance.
- **`null`**: `null == null` is true; `null.Equals(x)` throws
  `NullReferenceException` (there is no object to call a method on).
- **Overloaded `==` without `Equals`**: a type that overloads `==` but not
  `Equals` gives you different answers from the two "equal" checks — the
  classic contract violation. If you overload one, override the other (and
  `GetHashCode`) to match.
- Arrays: `==` on arrays is reference equality; element-wise comparison is
  `SequenceEqual`.

---

### 🟡 Q. `async`/`await` — what does `await` actually do, and what is the
`async void` trap?

**Answer.** `await` does not block a thread. It registers the rest of the
method as a continuation to run when the awaited task completes, and **returns
from the method now** (the method becomes a state machine). The thread goes
back to the pool; the continuation runs later, on the captured
`synchronization context` (in UI code, back on the UI thread).

The traps:

- **`async void`** is for event handlers only. There is no `Task` to await, so
  an exception inside has nowhere to go — it escapes to the synchronization
  context and can crash the process. Everything else is `async Task` (or
  `ValueTask`), which lets the caller observe completion and exceptions.
- **`.Result` / `.Wait()`** on a task in a UI context deadlock: the thread
  blocks while the continuation waits for a free slot on that same context.
  `await` all the way down instead.
- **`async` does not mean parallel.** It means *asynchronous* — overlapping
  work by yielding, not running at the same instant. To run tasks concurrently
  you start several and `await Task.WhenAll` (see
  [`examples/csharp/async/async_await_task_when_all.cs`](../../examples/csharp/async/async_await_task_when_all.cs)).
- The `ConfigureAwait(false)` nuance: in library code you often don't need the
  continuation on the original context, and opting out avoids a hop (and a
  deadlock class) at the cost of resuming on a pool thread.

---

### 🟡 Q. `interface` vs `abstract class` — and what did C# 8 default
interface members change?

**Answer.** An **interface** is a capability contract: no state, and (before
C# 8) no implementation. A class can implement any number of them. An
**abstract class** is a common base: it can carry state and shared behaviour,
but a class has exactly **one** base class, so it competes with your real
inheritance chain. The decision: repeated *state*/behaviour you want written
once → abstract base; a capability that unrelated types should share →
interface.

What C# 8 changed: interfaces can now have **default implementations**. That
softens the line — an interface can carry behaviour — but it does not remove
the distinction, because a default interface method still cannot touch
instance *state* (there is none) and, more importantly, the reason to prefer
an interface is the **multiple-implementation** freedom an abstract base
cannot give. Default members are for *extending an existing interface without
breaking implementers* (add a method with a sensible default), not for
replacing a base class.

See [`examples/csharp/oop/interface_vs_abstract_class.cs`](../../examples/csharp/oop/interface_vs_abstract_class.cs).

---

### 🔴 Q. What is the difference between `Task`, `ValueTask`, and
`Task<T>` — and when is each the right return type?

**Answer.** `Task<T>` is the standard async result: a heap-allocated object
representing a computation that yields `T`. `ValueTask<T>` is the
**low-allocation** alternative for methods that *usually complete
synchronously*: it can either wrap an already-available `T` (no allocation)
or a `Task<T>` (allocation happens only on the async path). `Task` (no `T`)
is the fire-and-complete-notify version for work with no result.

The trade-off, stated precisely:

- **Default to `Task<T>`.** It is composable, can be stored, awaited multiple
  times, and plays well with the rest of the async API.
- **Use `ValueTask<T>` only on hot paths** where the method frequently returns
  a cached/synchronous result and the per-call allocation of a `Task` shows up
  in a profile. It comes with sharp edges: it must be awaited **exactly
  once** (it is a struct holding a by-ref-like result, not a shareable
  object), it cannot be stored for later in general, and returning a
  `ValueTask` that sometimes wraps a `Task` requires getting the
  `IsCanceled`/exception propagation right.
- The interview-grade framing: `ValueTask` is an *optimization with a contract*
  (single await, no caching), not a better `Task`. Choosing it without a
  measured allocation problem is premature, and misusing it (awaiting twice,
  storing it) is a real bug class.

See [`examples/csharp/async/`](../../examples/csharp/async/) for the
`Task.WhenAll` and cancellation patterns.
