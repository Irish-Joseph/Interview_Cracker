//! Topic: Implementing a custom Iterator in Rust.
//!
//! Concepts (advanced):
//! - The `Iterator` trait and its only required method: `next()`
//! - `Item` associated type
//! - Lazy evaluation — items are produced one at a time, on demand
//! - Composing custom iterators with built-in adapters
//!   (`filter`, `map`, `take`, `collect`)
//! - `into_iter()` / `iter()` / `iter_mut()` borrowing semantics
//!
//! We implement `Countdown`, an iterator that yields `n, n-1, ..., 1`,
//! then show that it plugs straight into the standard adapter
//! ecosystem without any extra work.
//!
//! Validate:  rustc --crate-type lib --emit=metadata countdown.rs
//! (full type-check; final linking needs the MSVC linker on Windows)

/// An iterator that counts down from `start` to `1`.
struct Countdown {
    current: Option<u64>,
}

impl Countdown {
    /// Creates a countdown starting at `start`.
    /// `start = 0` yields an empty sequence.
    fn new(start: u64) -> Self {
        Countdown {
            current: if start == 0 { None } else { Some(start) },
        }
    }
}

/// Implementing Iterator only *requires* `next()`; everything else
/// (count, sum, for-loops, adapters) is provided by default methods.
impl Iterator for Countdown {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let value = self.current?; // None -> iterator is exhausted
        self.current = if value == 1 { None } else { Some(value - 1) };
        Some(value)
    }
}

fn main() {
    // 1. for-loops work immediately: the loop calls next() repeatedly.
    for value in Countdown::new(5) {
        print!("{value} ");
    }
    println!(); // -> 5 4 3 2 1

    // 2. Adapters compose for free. Filter evens, halve them, take 3.
    let transformed: Vec<u64> = Countdown::new(10)
        .filter(|v| v % 2 == 0) // 10 8 6 4 2
        .map(|v| v / 2)         // 5 4 3 2 1
        .take(3)                 // 5 4 3
        .collect();
    println!("transformed: {transformed:?}"); // -> [5, 4, 3]

    // 3. Built-in consuming methods.
    let sum: u64 = Countdown::new(4).sum();
    let count = Countdown::new(7).count();
    println!("sum 1..=4 = {sum}"); // -> 10
    println!("count from 7 = {count}"); // -> 7

    // 4. Iterators are lazy: no computation happens until consumed.
    // This closure prints as items are pulled — notice the order
    // matches the pull order, and `take(2)` stops the source early.
    let source = vec![10, 20, 30, 40];
    source
        .iter()          // &i32 items — borrows, does not move the vec
        .map(|v| {
            println!("  producing {v}");
            v * 2
        })
        .take(2)
        .for_each(|v| println!("  consumed {v}"));
    // The vec is still usable afterwards because iter() borrows it:
    println!("vec untouched: {source:?}");

    // Expected tail output:
    //   producing 10
    //   consumed 20
    //   producing 20
    //   consumed 40
    // vec untouched: [10, 20, 30, 40]
}
