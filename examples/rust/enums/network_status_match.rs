//! Topic: Rust enums with data and exhaustive matching.
//!
//! Concepts:
//! - Enums that carry data (algebraic data types)
//! - `match` and the compiler's exhaustiveness checking
//! - The wildcard arm `_` and when to (not) use it
//! - Expression orientation: match arms produce values
//! - `if let` for the common single-pattern case
//!
//! Unlike C/Java enums (plain constants), Rust enum variants can
//! each carry different payloads — making them a replacement for
//! unions, tagged types, and even nullable values (`Option`).
//!
//! Validate:  rustc --crate-type lib --emit=metadata network_status.rs
//! (full type-check; final linking needs the MSVC linker on Windows)

/// A network probe result. Each variant carries the data that is
/// only relevant to that outcome.
enum NetworkStatus {
    Connected { latency_ms: u32 },   // struct-like: named fields
    Retrying { attempts: u8 },       // struct-like
    Timeout(u32),                    // tuple-like: seconds waited
    Offline,                         // unit-like: no data
}

/// Returns a human-readable line for any status.
///
/// The compiler FORCES us to handle every variant. Add a new
/// variant to `NetworkStatus` and this function will not compile
/// until a match arm is added — bugs that are silent in most
/// other languages become compile errors here.
fn describe(status: &NetworkStatus) -> String {
    match status {
        NetworkStatus::Connected { latency_ms } => {
            format!("connected ({} ms)", latency_ms)
        }
        NetworkStatus::Retrying { attempts } => {
            format!("retrying (attempt {})", attempts)
        }
        NetworkStatus::Timeout(secs) => format!("timed out after {} s", secs),
        NetworkStatus::Offline => "offline".to_string(),
    }
}

/// Expression-oriented match: the whole match is a single value.
fn is_actionable(status: &NetworkStatus) -> bool {
    matches!(
        status,
        NetworkStatus::Connected { .. } | NetworkStatus::Retrying { .. }
    )
}

/// `if let` is sugar for a match with one interesting arm.
fn maybe_latency(status: &NetworkStatus) -> Option<u32> {
    if let NetworkStatus::Connected { latency_ms } = status {
        Some(*latency_ms)
    } else {
        None
    }
}

fn main() {
    let statuses = vec![
        NetworkStatus::Connected { latency_ms: 23 },
        NetworkStatus::Retrying { attempts: 2 },
        NetworkStatus::Timeout(5),
        NetworkStatus::Offline,
    ];

    for status in &statuses {
        println!(
            "{:<28} actionable={:<5} latency={:?}",
            describe(status),
            is_actionable(status),
            maybe_latency(status)
        );
    }

    // Expected output:
    // connected (23 ms)            actionable=true  latency=Some(23)
    // retrying (attempt 2)         actionable=true  latency=None
    // timed out after 5 s          actionable=false latency=None
    // offline                      actionable=false latency=None
}
