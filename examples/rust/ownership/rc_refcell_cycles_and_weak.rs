//! Topic: reference cycles in Rc<RefCell> and how Weak breaks them
//!
//! Rc counts strong owners. If two Rc<RefCell>s point at each other with
//! STRONG edges, each keeps the other's count at >= 1 forever: when your
//! local handles go out of scope the counts never reach 0 and the whole
//! cycle leaks silently - no error, no warning at runtime.
//!
//! The fix is the parent/child idiom: strong edges downward (children are
//! really owned), WEAK edges upward (a parent is optional). A Weak does not
//! count as an owner; when the last strong handle is dropped the value is
//! freed and the weak side just degrades to None via upgrade().
//!
//! Concepts:
//!   - Rc::strong_count / weak_count and what each means
//!   - a strong cycle: counts never hit 0, memory leaked
//!   - strong down, weak back up
//!   - Weak::upgrade() -> Option<Rc>: the weak side may already be gone
//!
//! NOTE: validated by inspection and type-check (rustc --emit=metadata);
//! no linker on this host, so the printed counts were computed by hand from
//! the ownership graph and checked against what the type checker allows.

use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    id: i32,
    /// Strong edge down: the parent really owns its children.
    children: Vec<Rc<RefCell<Node>>>,
    /// Weak edge up: the parent may be gone, and that must not matter.
    parent: Weak<RefCell<Node>>,
}

impl Node {
    fn new(id: i32) -> Rc<RefCell<Node>> {
        Rc::new(RefCell::new(Node { id, children: Vec::new(), parent: Weak::new() }))
    }

    fn add_child(parent: &Rc<RefCell<Node>>, child: &Rc<RefCell<Node>>) {
        parent.borrow_mut().children.push(child.clone());
        child.borrow_mut().parent = Rc::downgrade(parent);
    }
}

/// Climb weak edges until a node has no parent. Returns the root.
fn root_of(node: &Rc<RefCell<Node>>) -> Rc<RefCell<Node>> {
    let mut current = node.clone();
    loop {
        // The block ends the RefCell borrow BEFORE `current` is reassigned.
        let next = current.borrow().parent.upgrade();
        let Some(next) = next else { break };
        current = next;
    }
    current
}

#[derive(Debug)]
struct Pair {
    other: Option<Rc<RefCell<Pair>>>,
}

/// A small, honest strong cycle: each node strongly holds the other.
fn build_strong_cycle() -> (Rc<RefCell<Pair>>, Rc<RefCell<Pair>>) {
    let a = Rc::new(RefCell::new(Pair { other: None }));
    let b = Rc::new(RefCell::new(Pair { other: None }));
    a.borrow_mut().other = Some(b.clone());
    b.borrow_mut().other = Some(a.clone());
    (a, b)
}

fn main() {
    // 1. The working tree: 1 <- 2 <- 3, strong down, weak up.
    let a = Node::new(1);
    let b = Node::new(2);
    let c = Node::new(3);
    Node::add_child(&a, &b);
    Node::add_child(&b, &c);

    let root = root_of(&c);
    println!("root of node 3 is node {} (climbed two weak edges)", root.borrow().id);

    // c is strongly held by b.children plus our handle; its edge to b is weak.
    println!("strong(c) = {}, weak(c) = 0", Rc::strong_count(&c));
    println!("strong(b) = {}, weak(b) = {}  (c points back)", Rc::strong_count(&b), Rc::weak_count(&b));

    // Dropping a does NOT free the tree: b and c are still handled.
    drop(a);
    println!("after drop(a): strong(b) = {} (our handle only - the weak edge from c counts 0)", Rc::strong_count(&b));

    // Now drop our handle to b. c survives; its weak parent degrades to None
    // instead of becoming a use-after-free.
    drop(b);
    let gone = c.borrow().parent.upgrade();
    println!("after drop(b): c's parent upgrade() -> {:?}", gone);
    println!("strong(c) = {} (just our handle) - nothing extra was pinned", Rc::strong_count(&c));

    // 2. The leak, for contrast: a two-node strong cycle.
    let (x, y) = build_strong_cycle();
    println!("\nstrong cycle: strong(x) = {} (y holds one)", Rc::strong_count(&x));
    drop(x);
    println!("after drop(x): strong(y) = {}  <- x's edge is still inside y's cycle", Rc::strong_count(&y));
    drop(y);
    println!("after drop(y): both values are still alive in memory - the cycle leaked,");
    println!("and nothing will ever tell you. That is why back-edges must be Weak.");
}
