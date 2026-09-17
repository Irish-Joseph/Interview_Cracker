//! Topic: Vec and HashMap - Rust's two workhorse collections.
//!
//! Both are growable and heap-allocated, and both interact with ownership in
//! ways that surprise newcomers: pushing MOVES a value in, indexing BORROWS
//! it back out, and removing gives ownership to you.
//!
//! Concepts:
//! - Vec: push/pop, indexing vs get(), iter / iter_mut / into_iter
//! - Why `v[10]` panics but `v.get(10)` returns None
//! - HashMap: insert, get, entry().or_insert() for counting and grouping
//! - Borrowing rules: you cannot hold a reference and mutate at the same time
//! - Sorting, deduplicating, and collecting iterators back into collections
//!
//! Run:  rustc --edition 2021 vec_and_hashmap.rs && ./vec_and_hashmap

use std::collections::HashMap;

fn main() {
    // -----------------------------------------------------------------------
    // 1. Vec basics
    // -----------------------------------------------------------------------
    let mut scores: Vec<i32> = Vec::new();
    scores.push(30);
    scores.push(10);
    scores.push(20);

    // vec! is the usual literal form; with_capacity avoids reallocation when
    // you already know roughly how many items are coming.
    let mut names = vec!["ada", "grace", "alan"];
    let mut reserved: Vec<u8> = Vec::with_capacity(16);
    reserved.push(1);

    println!("-- vec basics --");
    // capacity is how many items fit before the next reallocation. It is an
    // implementation detail and may differ between Rust versions.
    println!("  scores: {scores:?}  len={} capacity={}", scores.len(), scores.capacity());
    println!("  reserved: len={} capacity={}", reserved.len(), reserved.capacity());

    // Indexing panics on a bad index; get() hands you an Option instead.
    println!("  scores[0]    = {}", scores[0]);
    println!("  scores.get(0)= {:?}", scores.get(0));
    println!("  scores.get(9)= {:?}  (no panic)", scores.get(9));
    println!("  last()       = {:?}", scores.last());

    // pop() returns Option<T> and gives you OWNERSHIP of the value.
    let popped = scores.pop();
    println!("  popped {popped:?}, now {scores:?}");
    scores.push(20);

    // -----------------------------------------------------------------------
    // 2. Three ways to iterate, three different ownership stories
    // -----------------------------------------------------------------------
    println!("-- iteration --");

    // iter()      -> &T        : borrow each item, collection still usable
    let total: i32 = scores.iter().sum();
    println!("  sum via iter(): {total}, scores still usable: {scores:?}");

    // iter_mut()  -> &mut T    : borrow mutably and change in place
    for score in scores.iter_mut() {
        *score += 1; // deref to assign through the reference
    }
    println!("  after iter_mut +1: {scores:?}");

    // into_iter() -> T         : CONSUMES the vec; it cannot be used after
    let doubled: Vec<i32> = scores.clone().into_iter().map(|s| s * 2).collect();
    println!("  doubled (from a clone): {doubled:?}");

    // -----------------------------------------------------------------------
    // 3. Sorting and deduplicating
    // -----------------------------------------------------------------------
    let mut values = vec![5, 3, 9, 3, 1, 5, 5];
    values.sort();          // in place, ascending
    values.dedup();         // removes CONSECUTIVE duplicates -> sort first
    println!("-- sort/dedup --");
    println!("  {values:?}");

    names.sort_by_key(|name| name.len());
    println!("  by length: {names:?}");

    values.retain(|&v| v != 3);   // keep only what the predicate accepts
    println!("  after retain(!=3): {values:?}");

    // -----------------------------------------------------------------------
    // 4. HashMap basics
    // -----------------------------------------------------------------------
    let mut stock: HashMap<String, i32> = HashMap::new();
    stock.insert("apple".to_string(), 12);
    stock.insert("pear".to_string(), 0);
    // insert returns the PREVIOUS value, if there was one.
    let previous = stock.insert("apple".to_string(), 15);

    println!("-- hashmap --");
    println!("  insert returned the old value: {previous:?}");
    println!("  get(\"apple\")   = {:?}", stock.get("apple"));
    println!("  get(\"durian\")  = {:?}", stock.get("durian"));
    println!("  contains_key   = {}", stock.contains_key("pear"));
    // Unlike C++'s operator[], get() never inserts anything.

    // unwrap_or gives a default without inserting it.
    let kiwi = stock.get("kiwi").copied().unwrap_or(0);
    println!("  kiwi defaults to {kiwi}, map still has {} keys", stock.len());

    // -----------------------------------------------------------------------
    // 5. entry() - the idiomatic way to count and group
    // -----------------------------------------------------------------------
    let text = "the quick brown fox jumps over the lazy dog the end";

    let mut counts: HashMap<&str, i32> = HashMap::new();
    for word in text.split_whitespace() {
        // or_insert returns &mut to the value, existing or freshly inserted,
        // so the whole count-or-start-at-zero dance is one line.
        *counts.entry(word).or_insert(0) += 1;
    }

    let mut by_first_letter: HashMap<char, Vec<&str>> = HashMap::new();
    for word in text.split_whitespace() {
        by_first_letter
            .entry(word.chars().next().unwrap())
            .or_default()          // Vec::default() == empty vec
            .push(word);
    }

    println!("-- entry() --");
    let mut repeated: Vec<(&&str, &i32)> =
        counts.iter().filter(|(_, &n)| n > 1).collect();
    repeated.sort();
    println!("  words seen more than once: {repeated:?}");

    let mut letters: Vec<&char> = by_first_letter.keys().collect();
    letters.sort();
    println!("  distinct first letters: {}", letters.len());
    println!("  words starting with 't': {:?}", by_first_letter[&'t']);
}

/* Expected output:
-- vec basics --
  scores: [30, 10, 20]  len=3 capacity=4
  reserved: len=1 capacity=16
  scores[0]    = 30
  scores.get(0)= Some(30)
  scores.get(9)= None  (no panic)
  last()       = Some(20)
  popped Some(20), now [30, 10]
-- iteration --
  sum via iter(): 60, scores still usable: [30, 10, 20]
  after iter_mut +1: [31, 11, 21]
  doubled (from a clone): [62, 22, 42]
-- sort/dedup --
  [1, 3, 5, 9]
  by length: ["ada", "alan", "grace"]
  after retain(!=3): [1, 5, 9]
-- hashmap --
  insert returned the old value: Some(12)
  get("apple")   = Some(15)
  get("durian")  = None
  contains_key   = true
  kiwi defaults to 0, map still has 2 keys
-- entry() --
  words seen more than once: [("the", 3)]
  distinct first letters: 9
  words starting with 't': ["the", "the", "the"]

Note: HashMap iteration order is deliberately randomised in Rust, which is
why every listing above is sorted before printing.
*/
