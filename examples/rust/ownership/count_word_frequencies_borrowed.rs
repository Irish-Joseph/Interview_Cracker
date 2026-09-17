//! Topic: Count word frequencies using borrowing (no cloning).
//!
//! Concepts:
//! - Immutable borrows (`&String`, `&str`)
//! - Borrowing vs moving values
//! - `HashMap` with `entry().or_insert()`
//!
//! The goal: count words in a sentence while NEVER cloning the
//! source string. Words are only *borrowed* as `&str` slices.
//!
//! Compile:  rustc count_word_frequencies_borrowed.rs
//! Run:      ./count_word_frequencies_borrowed

use std::collections::HashMap;

/// Counts how many times each word appears in `text`.
///
/// Note the signature: we borrow `text` (`&String`) and return a
/// brand-new `HashMap`, so the caller keeps ownership of `text`.
fn word_frequencies(text: &String) -> HashMap<String, usize> {
    let mut counts: HashMap<String, usize> = HashMap::new();

    // split() yields `&str` slices that borrow from `text` — no copies.
    for word in text.split_whitespace() {
        // Strip punctuation so "end." and "end" are the same word.
        let cleaned: &str = word.trim_matches(|c: char| !c.is_alphanumeric());

        // entry() borrows the map, or_insert() sets a default if absent.
        *counts.entry(cleaned.to_string()).or_insert(0) += 1;
    }

    counts
}

fn main() {
    // The sentence stays owned by main the whole time.
    let sentence = String::from(
        "the quick brown fox jumps over the lazy dog; the fox is quick!",
    );

    // `word_frequencies` only borrows `sentence` (notice the `&`).
    let counts = word_frequencies(&sentence);

    // `sentence` is still usable AFTER the function returned,
    // which proves we only borrowed it — we never moved it.
    println!("Original sentence: {sentence}");
    println!("Length: {} chars\n", sentence.len());

    // Print frequencies sorted by word for stable, readable output.
    let mut sorted: Vec<(&String, &usize)> = counts.iter().collect();
    sorted.sort_by_key(|(word, _)| *word);

    for (word, count) in sorted {
        println!("{word:>10}  {count}x");
    }

    // Expected output (sorted):
    //   brown     1x
    //     dog     1x
    //     fox     2x
    //      is     1x
    //    lazy     1x
    //   jumps     1x
    //    over     1x
    //   quick     2x
    //     the     3x
}
