//! Topic: Result and the `?` operator — error handling without exceptions.
//!
//! Concepts:
//! - `Result<T, E>`: success or failure encoded in the type system
//! - Matching on Result vs the `?` early-return operator
//! - Option combinators: `ok_or`, `map`, `unwrap_or`, `and_then`
//! - A custom error enum that unifies several error kinds
//! - `impl From<OtherError>` so `?` converts errors automatically
//! - `Box<dyn Error>` for quick programs, a real enum for libraries
//!
//! Rust has no exceptions. A function that can fail SAYS SO in its return
//! type, and the caller cannot ignore that without writing it down.
//!
//! Run: rustc result_and_error_propagation.rs && ./result_and_error_propagation

use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

// --- 1. The basic shape ---------------------------------------------------

/// Fails instead of panicking on division by zero.
fn divide(numerator: f64, denominator: f64) -> Result<f64, String> {
    if denominator == 0.0 {
        return Err("division by zero".to_string());
    }
    Ok(numerator / denominator)
}

// --- 2. A custom error enum -----------------------------------------------

/// One error type covering everything `parse_config_line` can hit.
#[derive(Debug)]
enum ConfigError {
    MissingSeparator(String),
    EmptyKey,
    BadNumber(ParseIntError),
    OutOfRange { key: String, value: i64 },
}

// Display is what users see; Debug is what developers see.
impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::MissingSeparator(line) => {
                write!(f, "line has no '=' separator: {:?}", line)
            }
            ConfigError::EmptyKey => write!(f, "key is empty"),
            ConfigError::BadNumber(err) => write!(f, "value is not a number: {}", err),
            ConfigError::OutOfRange { key, value } => {
                write!(f, "{} = {} is outside 1..=65535", key, value)
            }
        }
    }
}

// Implementing Error makes the type usable as `Box<dyn Error>` and lets
// callers walk the cause chain via `source()`.
impl Error for ConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            ConfigError::BadNumber(err) => Some(err),
            _ => None,
        }
    }
}

// The key to `?`: it applies `From` to convert the inner error into ours.
// With this impl, `text.parse::<i64>()?` just works inside a function
// returning Result<_, ConfigError>.
impl From<ParseIntError> for ConfigError {
    fn from(err: ParseIntError) -> Self {
        ConfigError::BadNumber(err)
    }
}

// --- 3. `?` in action -----------------------------------------------------

/// Parses one `key = port` line. Every failure path is a typed error.
fn parse_config_line(line: &str) -> Result<(String, i64), ConfigError> {
    // Option -> Result: `ok_or_else` supplies the error for the None case,
    // then `?` returns early if it was None.
    let (key, raw_value) = line
        .split_once('=')
        .ok_or_else(|| ConfigError::MissingSeparator(line.to_string()))?;

    let key = key.trim();
    if key.is_empty() {
        return Err(ConfigError::EmptyKey);
    }

    // No `map_err` needed: From<ParseIntError> above does the conversion.
    let value: i64 = raw_value.trim().parse()?;

    if !(1..=65535).contains(&value) {
        return Err(ConfigError::OutOfRange {
            key: key.to_string(),
            value,
        });
    }

    Ok((key.to_string(), value))
}

// --- 4. Box<dyn Error>: the quick option for main and small programs ------

fn total_of_ports(lines: &[&str]) -> Result<i64, Box<dyn Error>> {
    let mut total = 0;
    for line in lines {
        // ConfigError converts into Box<dyn Error> automatically.
        let (_, port) = parse_config_line(line)?;
        total += port;
    }
    Ok(total)
}

fn main() {
    // --- Matching explicitly ---------------------------------------------
    println!("1. explicit match");
    for (a, b) in [(10.0, 4.0), (1.0, 0.0)] {
        match divide(a, b) {
            Ok(value) => println!("   {} / {} = {}", a, b, value),
            Err(msg) => println!("   {} / {} failed: {}", a, b, msg),
        }
    }

    // --- Combinators instead of match ------------------------------------
    println!("\n2. combinators");
    // unwrap_or: substitute a default for the error case.
    println!("   unwrap_or:     {}", divide(1.0, 0.0).unwrap_or(f64::NAN));
    // map: transform the success value, leave the error untouched.
    println!("   map:           {:?}", divide(9.0, 2.0).map(|v| v * 100.0));
    // and_then: chain another fallible step.
    let chained = divide(100.0, 5.0).and_then(|v| divide(v, 0.0));
    println!("   and_then:      {:?}", chained);
    // is_ok / ok(): drop the error and get an Option back.
    println!("   ok():          {:?}", divide(8.0, 2.0).ok());

    // --- Typed errors from `?` -------------------------------------------
    println!("\n3. parse_config_line");
    let samples = ["port = 8080", "  = 80", "port = eighty", "port = 70000", "port 8080"];
    for line in samples {
        match parse_config_line(line) {
            Ok((key, value)) => println!("   ok   {:?} -> {} = {}", line, key, value),
            Err(err) => {
                println!("   err  {:?} -> {}", line, err);
                // The cause chain: BadNumber keeps the original ParseIntError.
                if let Some(source) = err.source() {
                    println!("        caused by: {}", source);
                }
            }
        }
    }

    // --- Propagating through a call stack --------------------------------
    println!("\n4. propagation with Box<dyn Error>");
    match total_of_ports(&["http = 80", "https = 443"]) {
        Ok(total) => println!("   total of ports: {}", total),
        Err(err) => println!("   failed: {}", err),
    }
    match total_of_ports(&["http = 80", "broken"]) {
        Ok(total) => println!("   total of ports: {}", total),
        Err(err) => println!("   failed: {}", err),
    }

    // --- When panicking is acceptable ------------------------------------
    // `unwrap` / `expect` abort the program. Reserve them for cases that
    // are genuinely impossible, and say why with `expect`:
    let port = parse_config_line("ssh = 22").expect("literal above is valid");
    println!("\n5. expect on a known-good value: {:?}", port);
}
