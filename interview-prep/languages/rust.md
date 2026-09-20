# Rust

Rust interviews test one idea above all: do you understand **ownership**,
and can you reason about when the borrow checker accepts or rejects code?
The language features (traits, enums, iterators) are the icing; memory
safety without a garbage collector is the substance.

---

### 🟢 Q. What is ownership, and what does it mean to "move" a value?

**Answer.** Every value has exactly one **owner**; when the owner goes out
of scope, the value is dropped. Assignment and function arguments
**move** the value by default — the original binding is no longer usable.
This is what guarantees no double-free and no use-after-free without a GC.

```rust
fn takes_ownership(x: String) -> u32 {
    x.len() as u32
}

fn main() {
    let s = String::from("hello");
    let n = takes_ownership(s);   // `s` is MOVED into the function
    assert_eq!(n, 5);
    // println!("{}", s);         // COMPILE ERROR: `s` was moved
}
```

Types that implement `Copy` (ints, `bool`, floats, `char`, and
fixed-size arrays of those) are copied instead of moved, which is why
`let y = x;` feels free for `i32` but not for `String`.

---

### 🟡 Q. What are borrowing and lifetimes, and when does the borrow
checker reject your code?

**Answer.** A **borrow** (`&T` / `&mut T`) lets you use a value without
taking ownership. The rules: any number of shared borrows, OR exactly one
mutable borrow — never both at once. A **lifetime** annotation tells the
compiler how long a reference may outlive the data it points to; you
rarely write them explicitly, but `longest<'a>(a: &'a str, b: &'a str) ->
&'a str` shows the rule that the returned reference may live no longer
than the *shorter*-lived input.

```rust
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}

fn main() {
    let s1 = String::from("long string is long");
    let s2 = String::from("xyz");
    let result = longest(s1.as_str(), s2.as_str());
    assert_eq!(result, "long string is long");
    assert_eq!(first_word("  hello world"), "hello");
}
```

The classic rejection, and the one to be able to explain out loud:

```rust
fn main() {
    let result;
    {
        let s = String::from("hello");
        result = longest(s.as_str(), "world");
    }                       // `s` dropped here
    let _ = result.len();   // ERROR: `s` does not live long enough
}
```

`result` borrows from `s`, which dies at the closing brace — returning a
reference to it would dangle. The fix is to return an owned `String`
(`.to_string()`) or keep `s` alive for as long as `result` is used.

---

### 🟡 Q. How does Rust handle errors — `Option`, `Result`, and the `?`
operator?

**Answer.** Failure is a **value**, not an exception. `Option<T>` is
`Some(T)` or `None` for "no value"; `Result<T, E>` is `Ok(T)` or `Err(E)`
for recoverable failures. The `?` operator propagates an error: on `Err`
it returns early from the *current* function, on `Ok` it unwraps the
value — replacing the nested-matching pyramid of code.

```rust
fn parse_int(s: &str) -> Result<i64, String> {
    s.parse::<i64>().map_err(|e| format!("not a number: {e}"))
}

fn safe_div(a: i64, b: i64) -> Result<i64, String> {
    if b == 0 { return Err("division by zero".to_string()); }
    Ok(a / b)
}

// `?` returns early on Err, unwraps on Ok:
fn process(input: &str) -> Result<i64, String> {
    let n = parse_int(input)?;
    let half = safe_div(n, 2)?;
    Ok(half)
}

fn main() {
    assert_eq!(process("10"), Ok(5));
    assert!(process("abc").is_err());
    assert_eq!(safe_div(1, 0), Err("division by zero".to_string()));
}
```

The trade-off to state: `?` makes pipelines linear but forces every
function to thread a `Result` through its signature — errors are explicit
at every boundary (a feature), whereas exception-based languages let
failures surface only where they are caught (and silently, if never
caught).

---

### 🟡 Q. When do you reach for `Box`, `Rc`, or `RefCell`?

**Answer.** They solve the three limitations of the stack-ownership model:

- **`Box<T>`** — heap allocation / unknown-at-compile-time size /
  recursive types. Still a single owner.
- **`Rc<T>`** — *shared* ownership: many owners, one data. Reference
  counted; drops when the count hits 0. (Not thread-safe; use `Arc` with
  atomics for across-threads.)
- **`RefCell<T>`** — *interior mutability*: immutable binding, mutable
  contents, with the shared/mutable borrow rules checked **at runtime**
  instead of compile time.

```rust
use std::rc::Rc;
use std::cell::RefCell;

struct Node {
    value: i32,
    next: RefCell<Option<Rc<Node>>>,
}

fn push(head: &Rc<RefCell<Option<Rc<Node>>>>, value: i32) {
    let new = Rc::new(Node { value, next: RefCell::new(None) });
    (*head).borrow_mut().replace(new);   // unique write access for a moment
}

fn len(head: &Rc<RefCell<Option<Rc<Node>>>>) -> usize {
    let mut n = 0;
    let mut cur = head.borrow().clone(); // clone the Rc (cheap refcount bump)
    while let Some(node) = cur {
        n += 1;
        cur = node.next.borrow().clone();
    }
    n
}
```

`Rc` outside + `RefCell` inside is the standard shape for data with
multiple owners AND runtime-rearranged structure (graphs, trees you mutate
in place). The cost: `borrow()`/`borrow_mut()` panic at runtime on rule
violations, and `Rc` increments/decrements a counter on every clone/drop.

---

### 🔴 Q. Walk through what happens when a function with an `Option`
return value is called, and why `unwrap()` is a code smell in production.

**Answer.** The caller **must** handle both cases — the type system makes
`None` a visible branch, usually via `match`, `if let`, or `?`. `unwrap()`
(and `expect()`) say "I guarantee this is `Some`, panic otherwise" — fine
in tests and prototypes, but in production it converts a handleable
absence into a crash, typically deep in a request path where the real
cause (a bad input, a missing config key) is far away. The production
pattern is to propagate: return a `Result`/`Option` upward with `?`, map
the `None` into a meaningful error with `ok_or(...)`, or branch
deliberately with a default only when a default is genuinely correct.

```rust
fn find_user(id: u64) -> Option<String> {
    (id == 1).then(|| String::from("ada"))
}

fn greet(id: u64) -> Result<String, String> {
    let user = find_user(id)
        .ok_or_else(|| format!("no user with id {id}"))?;
    Ok(format!("hello {user}"))
}

fn main() {
    assert_eq!(greet(1), Ok("hello ada".to_string()));
    assert!(greet(2).is_err());
}
```

The follow-up: `Option` and `Result` are enums with **zero overhead** in
the `Some`/`Ok` case (a niche optimization means `Option<&T>` is the same
size as `&T`), so wrapping fallible values costs nothing at runtime — the
cost is purely at the call sites, which is exactly where you want the
attention.
