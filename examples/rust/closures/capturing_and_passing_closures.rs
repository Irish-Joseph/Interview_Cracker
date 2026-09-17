// Topic: Closures — anonymous functions that capture their environment.
//
// Concepts:
// - Closure syntax |args| -> ret { body }
// - Capturing variables by reference, mutable reference, or ownership
// - Passing closures as arguments (higher-order functions)
// - Closure return values
//
// Example output:
//   add10(5) = 15
//   count is now 4 (closure borrowed `count` mutably)
//   mapped: [2, 4, 6, 8, 10]
//   kept: 15 (closure took ownership of the Vec)

fn main() {
    // A closure capturing a local variable by (immutable) reference.
    let base = 10;
    let add10 = |x: i32| x + base;
    println!("add10(5) = {}", add10(5));

    // A closure that mutates captured state: it borrows `count` mutably.
    let mut count = 1;
    let mut increment = || count += 1;
    increment();
    increment();
    increment();
    println!("count is now {} (closure borrowed `count` mutably)", count);

    // Closures as arguments: map() takes a closure that transforms items.
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = numbers.iter().map(|n| n * 2).collect();
    println!("mapped: {:?}", doubled);

    // Closure as a stored value with an explicit return type:
    let double_and_check = |n: i32| -> i32 {
        let result = n * 2;
        if result > 100 {
            -1 // signal overflow-ish cases
        } else {
            result
        }
    };
    assert_eq!(double_and_check(6), 12);

    // Ownership capture: this closure MOVES `numbers` into itself.
    let owns = |v: Vec<i32>| v.iter().sum::<i32>();
    let size = owns(numbers); // `numbers` may no longer be used after this
    println!("kept: {} (closure took ownership of the Vec)", size);
}
