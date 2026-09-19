//! Topic: Modules, visibility and paths - organising a Rust crate.
//!
//! Rust is private by default. Every item is visible only inside the module
//! that defines it (and its descendants) until you say `pub`. That default is
//! deliberate: it makes the public surface of a crate something you opt into
//! rather than something you leak by accident.
//!
//! Concepts:
//! - `mod` blocks, nested modules, and the module tree
//! - Private by default; `pub`, `pub(crate)`, `pub(super)`
//! - Absolute paths (`crate::`) vs relative (`self::`, `super::`)
//! - `use` to shorten paths, and `as` to rename
//! - Re-exporting with `pub use` to present a tidy public API
//! - Struct fields are private SEPARATELY from the struct itself
//! - Why an enum's variants are public as soon as the enum is
//!
//! Run:  rustc --edition 2021 modules_and_visibility.rs && ./modules_and_visibility

// ---------------------------------------------------------------------------
// 1. A module tree
// ---------------------------------------------------------------------------

mod store {
    // Visible anywhere in this crate, but NOT to an outside crate.
    pub(crate) const MAX_ITEMS: usize = 100;

    // Nested module. `pub` makes the MODULE reachable; its contents still
    // need their own `pub`.
    pub mod inventory {
        // A struct can be public while its fields stay private. Callers must
        // go through the constructor, so invariants cannot be bypassed.
        #[derive(Debug, Clone)]
        pub struct Item {
            pub name: String, // deliberately public
            quantity: u32,    // private: only this module may touch it
        }

        impl Item {
            pub fn new(name: &str, quantity: u32) -> Self {
                Item { name: name.to_string(), quantity }
            }

            pub fn quantity(&self) -> u32 {
                self.quantity
            }

            // Enforces an invariant that a public field could not.
            pub fn take(&mut self, amount: u32) -> Result<u32, String> {
                if amount > self.quantity {
                    return Err(format!("only {} left", self.quantity));
                }
                self.quantity -= amount;
                Ok(self.quantity)
            }

            // Visible to the PARENT module (store) but not beyond it.
            pub(super) fn restock(&mut self, amount: u32) {
                self.quantity += amount;
            }
        }

        // An enum's variants are public as soon as the enum is - there is no
        // per-variant visibility, unlike struct fields.
        #[derive(Debug, PartialEq)]
        pub enum Status {
            InStock(u32),
            OutOfStock,
        }

        pub fn status(item: &Item) -> Status {
            if item.quantity == 0 {
                Status::OutOfStock
            } else {
                Status::InStock(item.quantity)
            }
        }

        // No `pub`: private to this module, invisible even to `store`.
        fn audit_note(item: &Item) -> String {
            format!("{} x{}", item.name, item.quantity)
        }

        pub fn audit(item: &Item) -> String {
            // A module can always reach its own private items.
            audit_note(item)
        }
    }

    // `use` inside a module shortens paths for that module only.
    use self::inventory::{Item, Status};

    pub fn restock_all(items: &mut Vec<Item>, amount: u32) {
        for item in items.iter_mut() {
            // pub(super) means: callable from `store`, this item's parent.
            item.restock(amount);
        }
    }

    pub fn summarise(items: &[Item]) -> Vec<String> {
        items
            .iter()
            .map(|item| match inventory::status(item) {
                Status::InStock(n) => format!("{}: {} in stock", item.name, n),
                Status::OutOfStock => format!("{}: out of stock", item.name),
            })
            .collect()
    }

    // Re-export: callers write store::Item instead of store::inventory::Item.
    // This is how a crate presents a flat, stable API over a nested tree.
    pub use self::inventory::Item as StockItem;
}

// ---------------------------------------------------------------------------
// 2. A sibling module reaching across the tree
// ---------------------------------------------------------------------------

mod reporting {
    // `crate::` is an ABSOLUTE path from the crate root - unambiguous, and
    // the usual choice when reaching across the tree.
    use crate::store::inventory::{status, Item, Status};

    pub fn low_stock(items: &[Item], threshold: u32) -> Vec<&Item> {
        items
            .iter()
            .filter(|item| match status(item) {
                Status::InStock(n) => n < threshold,
                Status::OutOfStock => true,
            })
            .collect()
    }
}

// `use` at the root brings names into scope for main.
use store::inventory::{self, Status};
use store::StockItem; // the re-exported name

fn main() {
    println!("-- constructing through a public API --");
    let mut items = vec![
        StockItem::new("widget", 5), // the re-exported alias
        inventory::Item::new("gadget", 0),
        inventory::Item::new("sprocket", 2),
    ];
    for item in &items {
        println!("  {:?}", item);
    }

    println!("-- private fields force you through the methods --");
    // items[0].quantity = 999;   // ERROR: field `quantity` is private
    println!("  widget quantity via getter: {}", items[0].quantity());

    match items[0].take(3) {
        Ok(left) => println!("  took 3, {} left", left),
        Err(message) => println!("  could not take 3: {}", message),
    }
    match items[2].take(10) {
        Ok(left) => println!("  took 10, {} left", left),
        Err(message) => println!("  could not take 10: {}", message),
    }

    println!("-- enum variants are public with the enum --");
    for item in &items {
        println!("  {:<9} {:?}", item.name, inventory::status(item));
    }
    println!(
        "  gadget is out of stock: {}",
        inventory::status(&items[1]) == Status::OutOfStock
    );

    println!("-- pub(super): callable from the parent, not from here --");
    // items[0].restock(10);   // ERROR: `restock` is private to `store`
    store::restock_all(&mut items, 10);
    for line in store::summarise(&items) {
        println!("  {}", line);
    }

    println!("-- a private fn stays private, but its wrapper does not --");
    // inventory::audit_note(&items[0]);   // ERROR: private function
    println!("  {}", inventory::audit(&items[0]));

    println!("-- reaching across the tree with crate:: --");
    for item in reporting::low_stock(&items, 12) {
        println!("  low: {} ({})", item.name, item.quantity());
    }

    println!("-- pub(crate) --");
    // Visible throughout this crate; an external crate could not see it.
    println!("  store::MAX_ITEMS = {}", store::MAX_ITEMS);

    println!("-- visibility summary --");
    println!("  (default)    only this module and its descendants");
    println!("  pub(super)   this module's parent as well");
    println!("  pub(crate)   anywhere in this crate, but not outside it");
    println!("  pub          part of the crate's public API");
}

/* Expected output:
-- constructing through a public API --
  Item { name: "widget", quantity: 5 }
  Item { name: "gadget", quantity: 0 }
  Item { name: "sprocket", quantity: 2 }
-- private fields force you through the methods --
  widget quantity via getter: 5
  took 3, 2 left
  could not take 10: only 2 left
-- enum variants are public with the enum --
  widget    InStock(2)
  gadget    OutOfStock
  sprocket  InStock(2)
  gadget is out of stock: true
-- pub(super): callable from the parent, not from here --
  widget: 12 in stock
  gadget: 10 in stock
  sprocket: 12 in stock
-- a private fn stays private, but its wrapper does not --
  widget x12
-- reaching across the tree with crate:: --
  low: gadget (10)
-- pub(crate) --
  store::MAX_ITEMS = 100
*/
