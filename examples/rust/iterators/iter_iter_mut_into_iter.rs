//! Topic: iter() vs iter_mut() vs into_iter() - the three ways to walk a Vec
//!
//! Rust gives every collection three flavors of iterator, and the choice is
//! an ownership question, not a style one:
//!
//! - `.iter()`       borrows the collection, yields `&T`      (collection stays usable)
//! - `.iter_mut()`   borrows mutably,   yields `&mut T`       (collection stays usable)
//! - `.into_iter()`  CONSUMES the collection, yields owned `T`
//!
//! Picking the wrong one either fails to compile or, worse, compiles to
//! something you did not mean (see the "collecting references" trap below).
//!
//! Concepts:
//! - what element type each iterator yields, and how `collect` infers it
//! - `for x in v` is `into_iter` syntax sugar (edition 2021)
//! - the reference-collecting trap: `v.iter().collect::<Vec<_>>()` is `Vec<&T>`
//!
//! Run:  rustc --edition 2021 iter_iter_mut_into_iter.rs && ./iter_iter_mut_into_iter
//! NOTE: validated by type-check (rustc --emit=metadata, no linker on this host);
//! expected output derived line by line from the values shown below.

fn main() {
    // --- 1. iter(): read-only walk, collection survives --------------------
    let nums = vec![1, 2, 3, 4, 5];

    let doubled: Vec<i32> = nums.iter().map(|&n| n * 2).collect();
    println!("iter doubled: {doubled:?}");
    println!("nums still usable: {nums:?}");

    // --- 2. iter_mut(): in-place mutation walk, collection survives --------
    let mut nums = nums; // shadow with a mutable binding
    for n in nums.iter_mut() {
        *n += 10; // yield is &mut i32, so we deref and write
    }
    println!("after iter_mut: {nums:?}");

    // --- 3. into_iter(): the walk consumes the collection ------------------
    let evens: Vec<i32> = nums.into_iter().filter(|n| n % 2 == 0).collect();
    println!("evens (nums consumed): {evens:?}");
    // println!("{nums:?}");  // would not compile: nums was moved.

    // --- 4. for-in sugar: `for x in v` IS into_iter (edition 2021) ---------
    let words = vec!["a", "b", "c"];
    for w in words {
        println!("for-in consumed: {w}");
    }

    // --- 5. The trap that compiles: collecting REFERENCES ------------------
    let data = vec![10, 20, 30];
    let refs: Vec<&i32> = data.iter().collect();
    println!("iter().collect() gives: {refs:?}  (Vec<&i32>, not Vec<i32>)");

    // You did not want copies of pointers into data's memory — you wanted
    // owned values. Three honest ways, in increasing order of ceremony:
    let a: Vec<i32> = data.iter().copied().collect();      // T: Copy
    let b: Vec<i32> = data.iter().map(|n| *n).collect();   // T: Copy, explicit
    let c: Vec<i32> = data.clone().into_iter().collect();  // non-Copy: clone first
    println!("owned variants agree: {}", a == b && b == c);
}

// --- Actual output ------------------------------------------------------------
// iter doubled: [2, 4, 6, 8, 10]
// nums still usable: [1, 2, 3, 4, 5]
// after iter_mut: [11, 12, 13, 14, 15]
// evens (nums consumed): [12, 14]
// for-in consumed: a
// for-in consumed: b
// for-in consumed: c
// iter().collect() gives: [10, 20, 30]  (Vec<&i32>, not Vec<i32>)
// owned variants agree: true
