// Topic: Cow<'a, str> for borrow-first, clone-only-when-needed APIs.
// Concepts: Borrowed vs Owned, to_mut, avoiding unconditional allocation.
// Run: rustc --edition 2021 cow_clone_on_write.rs && ./cow_clone_on_write

use std::borrow::Cow;

fn normalize_spaces(input: &str) -> Cow<'_, str> {
    if !input.contains("  ") {
        return Cow::Borrowed(input);
    }

    let mut output = String::with_capacity(input.len());
    let mut previous_space = false;
    for ch in input.chars() {
        if ch != ' ' || !previous_space {
            output.push(ch);
        }
        previous_space = ch == ' ';
    }
    Cow::Owned(output)
}

fn main() {
    let clean = "already clean";
    let borrowed = normalize_spaces(clean);
    assert!(matches!(borrowed, Cow::Borrowed(_)));

    let owned = normalize_spaces("needs   cleanup");
    assert!(matches!(owned, Cow::Owned(_)));
    assert_eq!(owned, "needs cleanup");

    println!("borrowed: {borrowed}");
    println!("owned: {owned}");
}
