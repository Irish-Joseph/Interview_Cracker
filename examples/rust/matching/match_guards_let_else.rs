// Topic: Pattern matching — match guards, let-else, and destructuring.
//
// Concepts:
// - match is exhaustive: the compiler forces you to handle every case
// - Match guards `if` add a condition without another nested match
// - Destructuring tuples, structs, and nested patterns in one binding
// - let-else (Rust 2024 / stable since 1.65): unwrap-or-early-return idiom
// - @ bindings: capture a value while matching on its shape
//
// Compile check: rustc --crate-type lib (no linker needed).
//
// Behaviour (see the assert!s): the functions below are pure and asserted.

/// Classify an HTTP-ish status code, showing guards and ranges.
fn describe(code: u16) -> &'static str {
    match code {
        200..=299 => "success",
        300..=399 => "redirection",
        // Guard: only 404 gets the special message, other 4xx are "client error".
        400..=499 if code == 404 => "not found",
        400..=499 => "client error",
        500..=599 => "server error",
        _ => "unknown",
    }
}

/// Destructure a nested tuple-struct pattern in one go.
struct Point {
    x: i32,
    y: i32,
}

fn point_info(p: (char, Point, bool)) -> String {
    let (label, Point { x, y }, active) = p;
    let pos = if x >= 0 && y >= 0 { "quadrant I" } else { "other quadrant" };
    format!("{label} at ({x}, {y}), {pos}, active={active}")
}

/// let-else: bind a value or bail early — replaces a verbose
/// `match opt { Some(v) => v, None => return }`.
fn first_digit<'a>(s: &'a str) -> Option<&'a str> {
    let Some(pos) = s.find(|c: char| c.is_ascii_digit()) else {
        return None; // no digit anywhere
    };
    Some(&s[pos..])
}

/// @ binding: match the shape AND keep the whole value.
fn summarize(items: &[i32]) -> &'static str {
    match items {
        [] => "empty",
        [_] => "single",
        [_, rest @ ..] if rest.len() > 3 => "long (many)",
        [_, ..] => "short",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn guards_and_ranges() {
        assert_eq!(describe(200), "success");
        assert_eq!(describe(301), "redirection");
        assert_eq!(describe(404), "not found");
        assert_eq!(describe(403), "client error");
        assert_eq!(describe(500), "server error");
        assert_eq!(describe(9999), "unknown");
    }

    #[test]
    fn destructuring() {
        assert_eq!(
            point_info(('A', Point { x: 1, y: 2 }, true)),
            "A at (1, 2), quadrant I, active=true"
        );
    }

    #[test]
    fn let_else_and_at_bindings() {
        assert_eq!(first_digit("abc123"), Some("123"));
        assert_eq!(first_digit("abc"), None);
        assert_eq!(summarize(&[]), "empty");
        assert_eq!(summarize(&[7]), "single");
        assert_eq!(summarize(&[1, 2]), "short");
        assert_eq!(summarize(&[1, 2, 3, 4, 5]), "long (many)");
    }
}

// A tiny `main` so the file also runs standalone: it just asserts the
// same invariants without the test harness.
fn main() {
    assert_eq!(describe(404), "not found");
    assert_eq!(describe(403), "client error");
    assert_eq!(
        point_info(('A', Point { x: 1, y: 2 }, true)),
        "A at (1, 2), quadrant I, active=true"
    );
    assert_eq!(first_digit("abc123"), Some("123"));
    assert_eq!(first_digit("abc"), None);
    assert_eq!(summarize(&[]), "empty");
    assert_eq!(summarize(&[7]), "single");
    assert_eq!(summarize(&[1, 2]), "short");
    assert_eq!(summarize(&[1, 2, 3, 4, 5]), "long (many)");
    println!("rust pattern matching: all checks passed");
}
