//! Topic: Structs, methods and derive macros in Rust.
//!
//! Concepts:
//! - Defining structs (named fields, tuple structs)
//! - Constructor functions via `impl` blocks (no `new` requirement)
//! - `&self` vs `&mut self` vs `self` (ownership) receivers
//! - Derive macros: Debug, Clone, PartialEq
//! - Struct update syntax (`..other`)
//!
//! Structs bundle data; impl blocks attach behavior. The receiver
//! choice controls the borrowing rules:
//!   &self      -> read access (many at once)
//!   &mut self  -> write access (one at a time)
//!   self       -> takes ownership (the struct is consumed)
//!
//! Validate:  rustc --crate-type lib --emit=metadata structs_methods.rs
//! (full type-check; final linking needs the MSVC linker on Windows)

/// Derive gives us standard implementations for free.
#[derive(Debug, Clone, PartialEq)]
struct Book {
    title: String,
    author: String,
    pages: u32,
}

impl Book {
    /// Constructor convention: `new` with the most common arguments.
    /// (Not required — it's just a plain associated function.)
    fn new(title: &str, author: &str, pages: u32) -> Self {
        Book {
            title: title.to_string(),
            author: author.to_string(),
            pages, // shorthand for `pages: pages`
        }
    }

    /// Read-only method: many callers can share &Book at once.
    fn summary(&self) -> String {
        format!("{} by {} ({} pages)", self.title, self.author, self.pages)
    }

    /// Mutating method: exclusive access while running.
    fn add_pages(&mut self, extra: u32) {
        self.pages += extra;
    }

    /// Consuming method: takes ownership and returns something new.
    /// After this call the old Book no longer exists.
    fn make_excerpt(self) -> String {
        // `self` is moved in; we can use it freely and it's dropped here.
        format!("excerpt from {}", self.title)
    }
}

/// Tuple struct: positional fields (like a lightweight wrapper).
#[derive(Debug)]
struct Point(f64, f64);

impl Point {
    fn distance_to_origin(&self) -> f64 {
        (self.0 * self.0 + self.1 * self.1).sqrt()
    }
}

fn main() {
    // --- Derives in action ----------------------------------------------------
    let mut dune = Book::new("Dune", "Frank Herbert", 412);
    println!("{:?}", dune);                 // Debug derive
    let dune_copy = dune.clone();           // Clone derive (deep copy)
    println!("equal: {}", dune == dune_copy); // PartialEq derive

    // --- &self: shared read ----------------------------------------------------
    println!("{}", dune.summary());
    // -> Dune by Frank Herbert (412 pages)

    // --- &mut self: exclusive write ---------------------------------------------
    dune.add_pages(20);
    println!("{}", dune.summary());
    // -> Dune by Frank Herbert (432 pages)

    // --- Struct update syntax: copy fields, override some -------------------------
    let paper_edition = Book {
        pages: 448,                          // different page count
        ..dune_copy                          // rest copied from dune_copy
    };
    println!("{}", paper_edition.summary());
    // -> Dune by Frank Herbert (448 pages)

    // --- Consuming method: ownership moves ------------------------------------------
    let bladerunner = Book::new("Blade Runner", "Philip K. Dick", 205);
    let excerpt = bladerunner.make_excerpt(); // bladerunner is MOVED
    println!("{}", excerpt);
    // -> excerpt from Blade Runner
    // println!("{}", bladerunner.summary()); // would NOT compile:
    // bladerunner was moved into make_excerpt.

    // --- Tuple struct -----------------------------------------------------------------
    let p = Point(3.0, 4.0);
    println!("distance: {}", p.distance_to_origin());
    // -> distance: 5
}
