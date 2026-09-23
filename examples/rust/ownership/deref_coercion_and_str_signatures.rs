//! Topic: deref coercion and why idiomatic Rust APIs take &str, not &String
//!
//! Rust will silently insert `&*` conversions ("deref coercions") at call
//! sites: &String -> &str, &Box<T> -> &T, &Rc<T> -> &T, &Vec<T> -> &[T].
//! This is the reason function parameters should usually be `&str` (or
//! `&[T]`): the caller may hold a String, a &str slice, a Box<str> or a
//! str in a struct, and ALL of them coerce to the parameter type - while a
//! `&String` parameter accepts only one of them.
//!
//! Concepts:
//!   - Deref trait: &T -> &U when T: Deref<Target = U>; the compiler applies
//!     it repeatedly at coercion sites (arguments, assignments, ...), at
//!     most along one chain, and NEVER in the other direction
//!   - &String -> &str works because String: Deref<Target = str>
//!   - &str -> &String does NOT work: there is no Deref from str to String
//!   - generics with `AsRef<str>` accept both &str and &String
//!     callers through one signature
//!
//! NOTE: validated by type-check (rustc --emit=metadata, --deny warnings);
//! no linker on this host, so the println! outputs were computed by hand
//! (they are plain string lengths - no platform behaviour).

use std::borrow::Cow;


// The idiomatic signature: every str-flavoured owner below can call this.
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

// The restrictive signature: only &String callers fit. Kept as the
// contrast - it compiles, which is the point (the compiler cannot tell).
#[allow(dead_code)]
fn word_count_str(text: &String) -> usize {
    text.split_whitespace().count()
}

fn main() {
    let owned = String::from("the quick brown fox");
    let borrowed: &str = "jumps over the lazy dog";

    // Both coerce to &str. This is the everyday case.
    println!("owned:   {}", word_count(&owned));
    println!("borrow:  {}", word_count(borrowed));

    // Slicing: a &str is (pointer, length) - slicing costs nothing.
    let slice = &owned[4..14];
    println!("slice:   {} = {:?}", word_count(slice), slice);

    // Box<str> and Cow<str> coerce too:
    let boxed: Box<str> = "one two three".into();
    let cow: Cow<'_, str> = Cow::Borrowed("four five");
    println!("boxed:   {}", word_count(&boxed));
    println!("cow:     {}", word_count(&cow));

    // The other direction does NOT exist. This would be a compile error:
    //   let s: &String = borrowed;   // E0308: expected &String, found &str
    // (The compiler cannot invent the allocation that &String requires.)

    // vec<i32> -> &[i32] is the slice version of the same coercion:
    let nums = vec![1, 2, 3, 4, 5];
    println!("slice len: {}", sum_slice(&nums));

    // AsRef<str> is for callers holding a Sized OWNER like String (a raw
    // &str cannot be T - it is unsized - which is exactly why the &str
    // parameter above is the default choice: it already covers both cases).
    let from_owned = String::from("asref sees this");
    println!("asref &String: {}", asref_len(&from_owned));

    // Coercion happens at the CALL SITE, once. Storing behind a pointer to
    // the trait target is the manual version:
    let dyn_str: &dyn std::fmt::Display = &owned;
    println!("dyn display: {}", dyn_str);
}

fn sum_slice(nums: &[i32]) -> usize {
    nums.iter().sum::<i32>() as usize
}

fn asref_len<T: AsRef<str>>(value: &T) -> usize {
    value.as_ref().len()
}
// Expected output (computed; pure string operations, no platform behaviour):
//
// owned:   4
// borrow:  5
// slice:   2 = "quick brow"
// boxed:   3
// cow:     2
// slice len: 15
// asref &String: 15
// dyn display: the quick brown fox
