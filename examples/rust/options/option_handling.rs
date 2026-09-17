//! Topic: Option<T> - Rust's answer to null.
//!
//! Rust has no null. A value that may be absent has type `Option<T>`, which is
//! either `Some(value)` or `None`. Because it is an ordinary enum, the compiler
//! forces you to say what happens in the `None` case before you can touch the
//! value - the null-pointer bug simply cannot compile.
//!
//! Concepts:
//! - match, `if let`, and `let ... else`
//! - Transforming without unwrapping: map, and_then, filter, or_else
//! - Supplying fallbacks: unwrap_or, unwrap_or_else, unwrap_or_default
//! - as_ref / as_deref, so a borrow does not move the Option
//! - ? inside a function that returns Option
//! - Option <-> Result conversion with ok_or
//!
//! Run:  rustc --edition 2021 option_handling.rs && ./option_handling

#[derive(Debug, Clone)]
struct User {
    name: String,
    nickname: Option<String>,
    manager_id: Option<u32>,
    id: u32,
}

// ---------------------------------------------------------------------------
// 1. The three ways to look inside
// ---------------------------------------------------------------------------

/// `match` handles both arms explicitly - the most verbose, always available.
fn greeting_with_match(user: &User) -> String {
    match &user.nickname {
        Some(nick) => format!("Hey {nick}!"),
        None => format!("Hello {}.", user.name),
    }
}

/// `if let` is `match` when you only care about one arm.
fn shout_nickname(user: &User) -> Option<String> {
    if let Some(nick) = &user.nickname {
        Some(nick.to_uppercase())
    } else {
        None
    }
}

/// `let ... else` unwraps into the surrounding scope, or diverges.
/// It keeps the happy path unindented, which reads well in long functions.
fn nickname_length(user: &User) -> usize {
    let Some(nick) = &user.nickname else {
        return 0;
    };
    nick.len()
}

// ---------------------------------------------------------------------------
// 2. Transform without unwrapping
// ---------------------------------------------------------------------------

/// map applies a function to the inner value and leaves None untouched.
/// Note `as_deref()`: it turns &Option<String> into Option<&str> so the
/// String is borrowed rather than moved out of `user`.
fn initial(user: &User) -> Option<char> {
    user.nickname.as_deref().and_then(|nick| nick.chars().next())
}

/// and_then (flat_map in other languages) is for functions that themselves
/// return Option - using map here would give a nested Option<Option<&User>>.
fn manager_of<'a>(user: &User, directory: &'a [User]) -> Option<&'a User> {
    user.manager_id
        .and_then(|id| directory.iter().find(|candidate| candidate.id == id))
}

/// filter turns a Some that fails a predicate into None.
fn long_nickname(user: &User) -> Option<&str> {
    user.nickname.as_deref().filter(|nick| nick.len() >= 4)
}

// ---------------------------------------------------------------------------
// 3. Fallbacks
// ---------------------------------------------------------------------------

fn display_name(user: &User) -> String {
    // unwrap_or_else takes a closure, so the fallback is only built when needed.
    user.nickname
        .clone()
        .unwrap_or_else(|| user.name.to_string())
}

fn manager_name(user: &User, directory: &[User]) -> String {
    manager_of(user, directory)
        .map(|manager| manager.name.clone())
        // unwrap_or is fine for a cheap, already-built value.
        .unwrap_or("(none)".to_string())
}

// ---------------------------------------------------------------------------
// 4. ? propagates None out of an Option-returning function
// ---------------------------------------------------------------------------

/// Reads "key=value"; every step that can fail short-circuits to None.
fn parse_port(config_line: &str) -> Option<u16> {
    let (key, value) = config_line.split_once('=')?;
    if key.trim() != "port" {
        return None;
    }
    value.trim().parse::<u16>().ok()
}

// ---------------------------------------------------------------------------
// 5. Option and Result convert both ways
// ---------------------------------------------------------------------------

fn require_manager(user: &User) -> Result<u32, String> {
    // ok_or_else attaches an error to the None case.
    user.manager_id
        .ok_or_else(|| format!("{} has no manager", user.name))
}

fn main() {
    let directory = vec![
        User {
            id: 1,
            name: "Ada Lovelace".to_string(),
            nickname: None,
            manager_id: None,
        },
        User {
            id: 2,
            name: "Grace Hopper".to_string(),
            nickname: Some("Amazing Grace".to_string()),
            manager_id: Some(1),
        },
        User {
            id: 3,
            name: "Alan Turing".to_string(),
            nickname: Some("Al".to_string()),
            manager_id: Some(99), // dangling reference: no user 99 exists
        },
    ];

    for user in &directory {
        println!("--- {} ---", user.name);
        println!("  match:     {}", greeting_with_match(user));
        println!("  if let:    {:?}", shout_nickname(user));
        println!("  let-else:  {}", nickname_length(user));
        println!("  initial:   {:?}", initial(user));
        println!("  long nick: {:?}", long_nickname(user));
        println!("  display:   {}", display_name(user));
        println!("  manager:   {}", manager_name(user, &directory));
        println!("  required:  {:?}", require_manager(user));
    }

    println!("--- parse_port ---");
    for line in ["port = 8080", "port=notanumber", "host=localhost", "broken"] {
        println!("  {line:?} -> {:?}", parse_port(line));
    }

    // Collecting Options: a single None makes the whole collection None.
    let all: Option<Vec<u16>> = ["1", "2", "3"].iter().map(|s| s.parse().ok()).collect();
    let any_bad: Option<Vec<u16>> = ["1", "x", "3"].iter().map(|s| s.parse().ok()).collect();
    println!("--- collect ---");
    println!("  all parsed: {all:?}");
    println!("  one failed: {any_bad:?}");

    // Rule of thumb: reserve .unwrap()/.expect() for cases that are impossible
    // by construction, and say why in the message. Everywhere else, handle the
    // None - the compiler is asking you a real question.
    let first = directory.first().expect("directory is built with 3 users");
    println!("first user id: {}", first.id);
}

/* Expected output (abridged):
--- Ada Lovelace ---
  match:     Hello Ada Lovelace.
  if let:    None
  let-else:  0
  initial:   None
  long nick: None
  display:   Ada Lovelace
  manager:   (none)
  required:  Err("Ada Lovelace has no manager")
--- Grace Hopper ---
  match:     Hey Amazing Grace!
  if let:    Some("AMAZING GRACE")
  let-else:  13
  initial:   Some('A')
  long nick: Some("Amazing Grace")
  display:   Amazing Grace
  manager:   Ada Lovelace
  required:  Ok(1)
...
--- parse_port ---
  "port = 8080" -> Some(8080)
  "port=notanumber" -> None
  "host=localhost" -> None
  "broken" -> None
--- collect ---
  all parsed: Some([1, 2, 3])
  one failed: None
first user id: 1
*/
