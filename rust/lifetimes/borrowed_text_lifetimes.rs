//! Lifetimes describe relationships between borrows; they do not extend values' lives.

/// The returned slice cannot outlive either input, so both share lifetime `'a`.
fn longest<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

/// A struct containing a reference must state how long that reference is valid.
#[derive(Debug)]
struct Excerpt<'a> {
    source: &'a str,
    start: usize,
    end: usize,
}

impl<'a> Excerpt<'a> {
    fn text(&self) -> &'a str {
        &self.source[self.start..self.end]
    }
}

/// Lifetime elision rules infer that the output borrows from `text`.
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap_or("")
}

fn main() {
    let short = String::from("Rust");
    let selected: &str;

    {
        let sentence = String::from("borrows prevent dangling references");
        selected = longest(&short, &sentence);
        // `selected` is valid here because both possible sources are alive.
        println!("Longest: {selected}");
    }

    let article = String::from("Lifetimes connect input and output references.");
    let excerpt = Excerpt {
        source: &article,
        start: 0,
        end: 9,
    };
    println!("Excerpt: {}", excerpt.text());
    println!("First word: {}", first_word(&article));
}
