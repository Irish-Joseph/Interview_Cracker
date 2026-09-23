// Topic: From/Into for infallible conversion; TryFrom/TryInto for validation.
// Concepts: conversion direction, blanket Into implementation, typed errors.
// Run: rustc --edition 2021 from_into_tryfrom.rs && ./from_into_tryfrom

use std::convert::TryFrom;

#[derive(Debug, PartialEq)]
struct UserId(u64);

#[derive(Debug, PartialEq)]
struct ParseUserIdError;

impl From<u32> for UserId {
    fn from(value: u32) -> Self {
        Self(u64::from(value))
    }
}

impl TryFrom<&str> for UserId {
    type Error = ParseUserIdError;

    fn try_from(raw: &str) -> Result<Self, Self::Error> {
        let digits = raw.strip_prefix("usr_").ok_or(ParseUserIdError)?;
        let value = digits.parse::<u64>().map_err(|_| ParseUserIdError)?;
        Ok(Self(value))
    }
}

fn describe(id: impl Into<UserId>) -> String {
    let UserId(value) = id.into();
    format!("user #{value}")
}

fn main() {
    // Implementing From<u32> gives Into<UserId> for u32 automatically.
    assert_eq!(describe(42_u32), "user #42");

    let parsed = UserId::try_from("usr_9001");
    assert_eq!(parsed, Ok(UserId(9001)));
    assert_eq!(UserId::try_from("9001"), Err(ParseUserIdError));
    assert_eq!(UserId::try_from("usr_nope"), Err(ParseUserIdError));

    println!("{}", describe(42_u32));
    println!("parsed: {:?}", parsed.unwrap());
}
