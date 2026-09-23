# C++ Interview Questions

---

### 🟢 Q. What is RAII, and why is it the centre of C++ resource management?

**Answer.** Resource Acquisition Is Initialization: bind a resource (memory,
file handle, lock, socket) to an object's **lifetime** — acquire it in the
constructor, release it in the destructor. Because destructors run
deterministically when the object goes out of scope, "cleanup" stops being a
thing you remember to do and becomes a thing the language does for you, on
every exit path including exceptions.

The follow-ups:

- This is why C++ has no garbage collector and no `finally`: a `std::lock_guard`
  or `std::unique_ptr` *is* the finally. If an exception unwinds the stack,
  every guard's destructor still runs.
- The flip side: destructors must be **predictable and cheap-ish**, and an
  exception thrown from a destructor during unwinding terminates the program —
  which is why destructors are written to never throw.
- The pattern's limits: RAII owns resources with a clear owner and scope. For
  resources shared between owners you graduate to smart pointers; for "I don't
  know who frees this" you have a design problem, not a tooling one.

---

### 🟢 Q. `unique_ptr`, `shared_ptr`, `weak_ptr` — when is each one right?

**Answer.** `unique_ptr` is the default: single ownership, zero overhead
(same size as a raw pointer), non-copyable but movable. `shared_ptr` is
reference-counted shared ownership — use it when you genuinely cannot decide
the owner up front. `weak_ptr` observes a `shared_ptr`'d object without
extending its life; `lock()` upgrades to a `shared_ptr` or gives you nothing.

The trade-offs that matter in an interview:

- `shared_ptr` costs an atomic increment/decrement on every copy and a second
  allocation for the control block — reach for it when shared ownership is
  real, not as a hedge.
- **Cycles**: two `shared_ptr`s pointing at each other never hit zero and
  leak. Break the back-edge with `weak_ptr` (parent owns children with
  `shared_ptr`, children point back with `weak_ptr`). See
  [`examples/rust/ownership/rc_refcell_cycles_and_weak.rs`](../../examples/rust/ownership/rc_refcell_cycles_and_weak.rs)
  for the same shape in Rust's `Rc`/`Weak`.
- A `unique_ptr` can be a member; a `shared_ptr` cycle can hide for months.
  The rule that keeps designs honest: if you have to ask "who owns this?",
  the answer should be exactly one thing, and `unique_ptr` should express it.

---

### 🟡 Q. What does "move semantics" actually do, and when does a move happen
implicitly?

**Answer.** A **move** transfers a resource from one object to another instead
of copying it: the moved-from object is left valid-but-unspecified (usually
empty), and the expensive copy is skipped. `std::move(x)` does not move
anything by itself — it is a cast to rvalue reference that *permits* a move
constructor/assignment to be selected.

The practical rules:

- Moves happen implicitly on **prvalues** (the result of a function returning
  by value, a freshly-built object). You write `std::move` only when you have
  a named object and deliberately want to give it away:
  `vec.push_back(std::move(big_string));`
- The classic bug: `return std::move(local);` — the `std::move` **prevents**
  copy elision (the compiler would have moved or elided anyway). Just write
  `return local;`.
- A moved-from object must not be *used*, only assigned to or destroyed.
  Reusing it as if it were still full is the "moved-from" class of bugs.
- The rule of zero/five: if you hand-write a destructor, copy, or move for a
  class that owns a resource, you need to think about all of them — or,
  better, hold the resource in a `unique_ptr` and delete your special members.

---

### 🟡 Q. `virtual` — what is the runtime cost, and what are the two traps?

**Answer.** A class with virtual functions gets a **vtable** (one per dynamic
type, shared by all its instances) and each object carries a **vptr**; a
virtual call reads the vptr and dispatches through the table — one extra
indirection, and the call usually cannot be inlined. The cost is real but
small; the design cost is that the type's behaviour is no longer knowable
from the static type.

The two traps (both demonstrated in
[`examples/cpp/oop/virtual_functions_and_the_vtable.cpp`](../../examples/cpp/oop/virtual_functions_and_the_vtable.cpp)):

- **Non-virtual destructor**: deleting a derived object through a base pointer
  runs only the base destructor — the derived part is skipped and its members
  leak. If a class is meant to be deleted polymorphically, its destructor
  must be `virtual` (or the class must be `final`/non-derivable).
- **Hiding**: a non-virtual member with the same name in a derived class
  compiles fine but is selected by the *static* type of the expression —
  `basePtr->f()` calls the base version even though the object is derived.
  The `override` keyword exists to make "I meant to override" explicit and to
  fail compilation when the base signature changes.

The follow-up this sets up: `virtual` on the *first* virtual call also cannot
be inlined, which is why hot single-type code sometimes uses the CRTP idiom
(static dispatch through templates) to buy the call back.

---

### 🔴 Q. Rule of zero, rule of three, rule of five — and how does a modern
codebase actually avoid all of them?

**Answer.** If a class owns a resource it must manage its five special
members consistently: destructor, copy constructor, copy assignment, move
constructor, move assignment. **Rule of three**: if you need one of the first
three, you probably need all three. **Rule of five**: with move semantics,
the count is five. **Rule of zero**: the best position is to need *none* —
hold resources in types that already manage themselves (`unique_ptr`,
`string`, `vector`) and let the implicit special members do the right thing.

Why this is the senior-level answer:

- Each hand-written special member is a place to get the invariant wrong —
  the copy that should be deep isn't, the assignment that doesn't free the
  old resource leaks, the move that leaves the source in an invalid state
  instead of a valid-but-unspecified one.
- The modern idiom: **own with smart pointers and containers, inherit
  behaviour, and let the compiler generate**. A class that is a bag of
  `std::string`, `std::vector`, and `std::unique_ptr` members gets correct
  copy/move/destruction for free, and the compiler will even tell you if you
  declare one special member and forget the rest (the others become
  deleted/implicit in ways you can see with `static_assert`).
- The escape hatch: when you genuinely need custom logic (a refcounted handle,
  a pooled allocation), write the five consistently — or wrap the resource in
  its own small class that owns the rule-of-five, and keep the surrounding
  classes rule-of-zero.

See also [`examples/cpp/raii/raii_and_move.cpp`](../../examples/cpp/raii/raii_and_move.cpp)
and [`examples/cpp/smart-pointers/`](../../examples/cpp/smart-pointers/).
