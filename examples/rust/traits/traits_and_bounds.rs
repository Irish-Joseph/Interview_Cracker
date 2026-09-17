//! Topic: Traits — Rust's interface system.
//!
//! Concepts (advanced):
//! - Defining traits with required + provided methods
//! - Implementing traits for your own types
//! - Trait bounds on generics (`T: Display`)
//! - Multiple bounds (`T: Add + Copy`)
//! - `dyn Trait`: dynamic dispatch (trait objects)
//! - The blanket impl trick (`impl<T: Display> Wrap<T>`)
//!
//! Traits are how Rust achieves "do the same thing with many
//! types" — statically (bounds, monomorphized) or dynamically
//! (dyn, vtable). Static dispatch is faster and can inline;
//! dynamic dispatch lets you hold heterogeneous collections.
//!
//! Validate:  rustc --crate-type lib --emit=metadata traits_demo.rs
//! (full type-check; final linking needs the MSVC linker on Windows)

use std::fmt;

/// A trait: required method + provided (default) methods.
trait Describable {
    /// Every implementor MUST provide this.
    fn describe(&self) -> String;

    /// Default implementation — can be overridden, but isn't required.
    fn shout(&self) -> String {
        let base = self.describe();
        format!("{}!!", base.to_uppercase())
    }
}

// --- Implementing the trait for concrete types -------------------------------

struct Circle {
    radius: f64,
}

struct Point {
    x: f64,
    y: f64,
}

impl Describable for Circle {
    fn describe(&self) -> String {
        format!("circle r={}", self.radius)
    }
    // shout() is inherited automatically from the default.
}

impl Describable for Point {
    fn describe(&self) -> String {
        format!("point ({}, {})", self.x, self.y)
    }

    // Overriding the default to show it CAN be replaced:
    fn shout(&self) -> String {
        format!("@{}", self.describe())
    }
}

// --- Trait bounds: generic code constrained to "any Describable" --------------

/// Works with Circle, Point, or ANY future type implementing Describable.
/// The compiler generates a specialized copy per type (monomorphization).
fn print_described<T: Describable>(item: &T) {
    println!("  quiet: {}", item.describe());
    println!("  loud:  {}", item.shout());
}

/// Multiple bounds: T must implement BOTH Display and Describable.
fn label<T: fmt::Display + Describable>(tag: &T) -> String {
    format!("[{}] {}", tag, tag.describe())
}

#[derive(Debug)]
struct Named {
    name: String,
}

impl fmt::Display for Named {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Named({})", self.name)
    }
}

impl Describable for Named {
    fn describe(&self) -> String {
        format!("named thing '{}'", self.name)
    }
}

// --- dyn Trait: dynamic dispatch for heterogeneous collections -----------------

/// A box of "any describable thing". The vtable lets one function
/// call .describe() on wildly different types at runtime.
fn print_all(describables: &[Box<dyn Describable>]) {
    for d in describables {
        println!("  dyn: {}", d.describe());
    }
}

fn main() {
    let circle = Circle { radius: 2.0 };
    let point = Point { x: 1.0, y: 2.0 };
    let named = Named {
        name: "widget".to_string(),
    };

    // Static dispatch: same function, three different specializations.
    println!("static dispatch:");
    print_described(&circle);
    print_described(&point);
    print_described(&named);

    println!("\nmultiple bounds:");
    println!("  {}", label(&named));

    // Dynamic dispatch: one vector, many types, no generics needed.
    // The explicit type annotation is what lets the vec hold MIXED
    // types — inference alone would latch onto the first element.
    let mixed: Vec<Box<dyn Describable>> = vec![
        Box::new(Circle { radius: 5.0 }),
        Box::new(Point { x: 0.0, y: 0.0 }),
        Box::new(Named {
            name: "origin".to_string(),
        }),
    ];
    println!("\ndynamic dispatch (dyn Describable):");
    print_all(&mixed);

    // Expected output:
    // static dispatch:
    //   quiet: circle r=2
    //   loud:  CIRCLE R=2!!
    //   quiet: point (1, 2)
    //   loud:  @point (1, 2)
    //   quiet: named thing 'widget'
    //   loud:  NAMED THING 'WIDGET'!!
    //
    // multiple bounds:
    //   [Named(widget)] named thing 'widget'
    //
    // dynamic dispatch (dyn Describable):
    //   dyn: circle r=5
    //   dyn: point (0, 0)
    //   dyn: named thing 'origin'
}
