/**
 * Topic: Closures — functions that remember their birthplace.
 *
 * Concepts:
 * - A closure = function + the variables it can see
 * - Private state that outlives the creating function
 * - Counter / factory patterns
 * - Shared vs per-instance state
 * - Closures in loops (the classic bug, and the fix)
 *
 * Every function in JavaScript captures the variables of the scope
 * where it was DEFINED — and keeps them alive even after that
 * scope has returned. That's a closure.
 *
 * Validate: node closures.js
 */

// --- 1. The basic closure: private state ----------------------------------

function makeCounter(start = 0) {
  let count = start; // PRIVATE: unreachable from outside

  return {
    increment: () => ++count,
    decrement: () => --count,
    value: () => count,
  };
}

const counter = makeCounter(10);
counter.increment();
counter.increment();
counter.decrement();
console.log("counter value:", counter.value()); // -> 11
// console.log(counter.count);                  // undefined — truly private

// Two counters are INDEPENDENT: each closure has its own `count`.
const a = makeCounter();
const b = makeCounter();
a.increment();
a.increment();
b.increment();
console.log("a:", a.value(), "b:", b.value()); // -> a: 2  b: 1

// --- 2. Factory pattern: pre-configured functions ---------------------------

function makeMultiplier(factor) {
  return (x) => x * factor;
}

const double = makeMultiplier(2);
const triple = makeMultiplier(3);
console.log("double(5) =", double(5), "triple(5) =", triple(5));
// -> 10, 15

// --- 3. Event-style: once() — run a function at most one time ---------------

function once(fn) {
  let called = false;
  let result;
  return (...args) => {
    if (!called) {
      called = true;
      result = fn(...args);
    }
    return result; // subsequent calls get the FIRST result
  };
}

const greetOnce = once((name) => `hello ${name}`);
console.log(greetOnce("alice")); // -> hello alice
console.log(greetOnce("bob"));   // -> hello alice (stuck with first)

// --- 4. The classic loop bug: shared variable captured by reference ---------

// WRONG: all callbacks close over the SAME `i` (with var) or the
// loop variable (with let it's fixed — see below).
const bad = [];
for (var i = 0; i < 3; i++) {
  bad.push(() => i);
}
console.log("var loop:  ", bad.map((f) => f())); // -> [3, 3, 3]

// FIX 1: let creates a fresh binding per iteration.
const good1 = [];
for (let i = 0; i < 3; i++) {
  good1.push(() => i);
}
console.log("let loop:  ", good1.map((f) => f())); // -> [0, 1, 2]

// FIX 2: capture the value in a fresh local (works even with var).
const good2 = [];
for (var j = 0; j < 3; j++) {
  const captured = j;            // a NEW variable per iteration
  good2.push(() => captured);
}
console.log("capture:   ", good2.map((f) => f())); // -> [0, 1, 2]

// --- 5. Shared state: multiple closures over one variable ---------------------

function makeWallet(balance) {
  let log = [];
  return {
    spend(amount) {
      if (amount > balance) throw new Error("insufficient funds");
      balance -= amount;
      log.push(`spent ${amount}`);
      return balance;
    },
    deposit(amount) {
      balance += amount;
      log.push(`added ${amount}`);
      return balance;
    },
    history() {
      return [...log];
    },
  };
}

const wallet = makeWallet(100);
wallet.spend(30);
wallet.deposit(10);
console.log("wallet:", wallet.spend(5), wallet.history());
// -> 75 [ 'spent 30', 'added 10', 'spent 5' ]
