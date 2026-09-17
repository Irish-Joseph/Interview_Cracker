//! Topic: String vs &str — owned vs borrowed text.
//!
//! Concepts:
//! - `String`: heap-owned, growable, UTF-8
//! - `&str`: a *borrowed* slice of UTF-8 text (may point into
//!   static data or into a String)
//! - Automatic `String -> &str` coercion (Deref)
//! - Which one to use in function signatures (take `&str`!)
//! - String::from, to_string() and the From trait
//!
//! Rule of thumb:
//!   - OWN a string that outlives a call      -> String
//!   - JUST READ text you don't own           -> &str
//!   - FUNCTION PARAMETERS that read text     -> &str (most general)
//!
//! &str is the more general type: every String can become a &str,
//! but a &str cannot become a String without copying.
//!
//! Validate:  rustc --crate-type lib --emit=metadata string_vs_str.rs
//! (full type-check; final linking needs the MSVC linker on Windows)

/// A function that only READS text should take `&str`.
/// It works with string literals AND with Strings (auto-coercion).
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

/// A function that must OWN the result returns a String.
/// (Returning &str here would be a lifetime puzzle for no benefit.)
fn shout(text: &str) -> String {
    let mut upper: String = text.to_uppercase();
    upper.push_str("!!");
    upper
}

fn main() {
    // 1. &str literals: live in the program's static memory.
    let literal: &str = "hello &str world";

    // 2. String: heap-owned, built at runtime.
    let mut owned: String = String::from("hello String world");
    owned.push_str(" (grows)");

    // 3. Both work with a &str parameter — no conversion needed.
    // The String is auto-coerced to a &str via Deref.
    println!("literal words: {}", word_count(literal));
    println!("owned   words: {}", word_count(&owned));

    // 4. to_string() copies a &str into a new owned String.
    let copied: String = literal.to_string();
    println!("copied: {}", copied);

    // 5. String -> &str coercion in a binding.
    let borrowed: &str = &owned; // borrows the String's contents
    println!("borrowed slice: {}", borrowed);

    // 6. Building a String from pieces (runtime construction).
    let parts = ["rust", "strings", "are", "great"];
    let joined = parts.join(" ");          // returns a new String
    let with_count = format!("{} -> {} words", joined, word_count(&joined));
    println!("{with_count}");

    // 7. Ownership flows out of functions.
    let yell = shout("careful");
    println!("{yell}"); // -> CAREFUL!!
    // `yell` now owns its memory; it will be dropped at end of scope.

    // Expected output:
    // literal words: 3
    // owned   words: 4
    // copied: hello &str world
    // borrowed slice: hello String world (grows)
    // rust strings are great -> 4 words
    // CAREFUL!!
}
