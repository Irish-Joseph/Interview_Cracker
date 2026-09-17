//! Topic: Fearless concurrency — threads, channels and shared state.
//!
//! Concepts:
//! - `thread::spawn` and joining to collect results
//! - `move` closures: why a thread must OWN what it touches
//! - `mpsc` channels: many producers, one consumer
//! - Dropping senders is what ends a receiver loop
//! - `Arc<T>` for shared ownership across threads
//! - `Mutex<T>` for shared MUTATION, and why the lock wraps the data
//! - `Send` and `Sync`: the traits that make the compiler the race detector
//!
//! Rust does not detect data races at run time — it refuses to compile them.
//! Shared mutable state must be wrapped in a type that makes the sharing
//! sound (Mutex, RwLock, atomics), and the ownership rules do the rest.
//!
//! Run: rustc --edition 2021 -O threads_and_channels.rs && ./threads_and_channels

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::Duration;

// --- 1. Spawn and join ----------------------------------------------------

fn spawn_and_join() {
    println!("1. spawn and join");

    let mut handles = Vec::new();

    for worker_id in 0..4 {
        // `move` transfers ownership of `worker_id` into the closure. Without
        // it the closure would borrow a local that may die before the thread.
        let handle = thread::spawn(move || {
            let work: u64 = (1..=200_000).map(|n| n % (worker_id + 2)).sum();
            thread::sleep(Duration::from_millis(10));
            (worker_id, work)
        });
        handles.push(handle);
    }

    // join() blocks until that thread finishes and hands back its return
    // value. It returns Result: Err means the thread panicked.
    for handle in handles {
        match handle.join() {
            Ok((id, total)) => println!("   worker {id} produced {total}"),
            Err(_) => println!("   a worker panicked"),
        }
    }
}

// --- 2. Channels: mpsc ----------------------------------------------------

fn channel_pipeline() {
    println!("\n2. channel pipeline");

    let (sender, receiver) = mpsc::channel::<String>();

    // Multiple producers: clone the sender, one per thread.
    for producer_id in 0..3 {
        let sender = sender.clone();
        thread::spawn(move || {
            for item in 0..3 {
                sender
                    .send(format!("p{producer_id}-item{item}"))
                    .expect("receiver is alive");
            }
            // This clone drops here, at the end of the thread.
        });
    }

    // The ORIGINAL sender must be dropped too, or the loop below never ends:
    // the receiver keeps waiting while any sender still exists.
    drop(sender);

    // Iterating a receiver blocks until a message arrives and stops when
    // every sender is gone.
    let mut received: Vec<String> = receiver.iter().collect();
    received.sort();
    println!("   received {} messages: {:?}", received.len(), received);
}

// --- 3. Shared state: Arc<Mutex<T>> ---------------------------------------

fn shared_counter() {
    println!("\n3. shared state with Arc<Mutex<T>>");

    // Arc = Atomically Reference Counted: shared OWNERSHIP across threads.
    // Mutex = mutual exclusion: shared MUTATION, one thread at a time.
    // The data lives INSIDE the mutex, so there is no way to touch it
    // without holding the lock. That is the whole trick.
    let tally = Arc::new(Mutex::new(HashMap::<String, usize>::new()));
    let mut handles = Vec::new();

    let words = ["alpha", "beta", "alpha", "gamma", "beta", "alpha"];

    for chunk in words.chunks(2) {
        let tally = Arc::clone(&tally); // bumps the refcount, not a deep copy
        let chunk: Vec<String> = chunk.iter().map(|s| s.to_string()).collect();

        handles.push(thread::spawn(move || {
            for word in chunk {
                // lock() blocks until the mutex is free and returns a guard.
                // The guard derefs to the data and unlocks when it is dropped
                // — no manual unlock, and no forgetting it on an early return.
                let mut map = tally.lock().expect("mutex poisoned");
                *map.entry(word).or_insert(0) += 1;
            } // guard dropped at the end of each iteration
        }));
    }

    for handle in handles {
        handle.join().expect("worker thread panicked");
    }

    // Every thread is done, so the Arc count is back to one.
    let map = tally.lock().unwrap();
    let mut counts: Vec<_> = map.iter().collect();
    counts.sort();
    println!("   counts: {counts:?}");
    println!("   arc strong count: {}", Arc::strong_count(&tally));
}

// --- 4. Atomics: a lock-free counter --------------------------------------

fn atomic_counter() {
    println!("\n4. atomics");

    // For a single integer, a Mutex is overkill: an atomic updates the value
    // with one CPU instruction and never blocks.
    let hits = Arc::new(AtomicUsize::new(0));
    let mut handles = Vec::new();

    for _ in 0..8 {
        let hits = Arc::clone(&hits);
        handles.push(thread::spawn(move || {
            for _ in 0..10_000 {
                hits.fetch_add(1, Ordering::Relaxed);
            }
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    // Exactly 80_000 — no lost updates, which is precisely what a data race
    // would cost you in a language that allowed one.
    println!("   total hits: {}", hits.load(Ordering::SeqCst));
}

// --- 5. Scoped threads: borrowing instead of moving -----------------------

fn scoped_borrow() {
    println!("\n5. scoped threads (Rust 1.63+)");

    let readings = vec![12.5, 9.0, 33.25, 7.75, 18.0];
    let label = String::from("sensor-A");

    // thread::scope guarantees every thread inside finishes before it
    // returns, so the threads may BORROW locals instead of taking ownership.
    // Before scoped threads this needed Arc, or a 'static lifetime.
    thread::scope(|scope| {
        let max_handle = scope.spawn(|| {
            readings.iter().cloned().fold(f64::MIN, f64::max)
        });
        let sum_handle = scope.spawn(|| readings.iter().sum::<f64>());

        println!("   {label}: max {}", max_handle.join().unwrap());
        println!("   {label}: sum {}", sum_handle.join().unwrap());
    });

    // `readings` is still usable here: it was only ever borrowed.
    println!("   still owned locally: {} readings", readings.len());
}

fn main() {
    spawn_and_join();
    channel_pipeline();
    shared_counter();
    atomic_counter();
    scoped_borrow();

    // What the compiler is enforcing behind all of this:
    //
    //   Send  — the type may be MOVED to another thread.
    //   Sync  — &T may be SHARED with another thread.
    //
    // Rc<T> is neither (its refcount is not atomic), which is why the
    // compiler rejects Rc across threads and points you at Arc. Nothing
    // here is a run-time check: get it wrong and the build fails.
}
