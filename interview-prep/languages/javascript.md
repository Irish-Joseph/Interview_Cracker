# JavaScript Interview Questions

---

### 🟢 Q. `var`, `let` and `const`?

**Answer.**

| | Scope | Hoisting | Reassign |
|---|---|---|---|
| `var` | function | hoisted, initialised `undefined` | yes |
| `let` | block | hoisted into the temporal dead zone | yes |
| `const` | block | same as `let` | no |

`const` prevents **rebinding the name**, not mutation of the value:

```js
const user = { name: "Sara" };
user.name = "Ali";        // fine — the object is mutable
user = {};                // TypeError — cannot rebind
```

Use `const` by default, `let` when you must reassign, and `var` never.

---

### 🟡 Q. What is a closure?

**Answer.** A function that retains access to the variables of the scope it was
created in, even after that scope has returned.

```js
function counter() {
  let count = 0;                 // stays alive via the closure
  return {
    increment: () => ++count,
    value: () => count,
  };
}
const c = counter();
c.increment();  c.increment();
c.value();      // 2
```

`count` is genuinely private — unreachable except through the returned functions.
This is the basis of the module pattern, memoisation, and every callback that
"remembers" something.

The classic interview trap:

```js
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));   // 3, 3, 3
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i));   // 0, 1, 2
```

`var` is function-scoped, so all three callbacks close over **one** variable,
which is 3 by the time they run. `let` creates a fresh binding per iteration.
Worked example: [`examples/javascript/basics/closures.js`](../../examples/javascript/basics/closures.js).

---

### 🔴 Q. Explain the event loop.

**Answer.** JavaScript is single-threaded but non-blocking. The runtime has:

- a **call stack** — what is executing now;
- **Web APIs / host APIs** — timers, network, file I/O, running outside the
  engine;
- a **macrotask queue** — `setTimeout`, I/O callbacks, UI events;
- a **microtask queue** — promise callbacks, `queueMicrotask`.

The loop: when the stack empties, **drain the entire microtask queue**, then take
**one** macrotask, then drain microtasks again. Microtasks always have priority.

```js
console.log("1");
setTimeout(() => console.log("2"), 0);       // macrotask
Promise.resolve().then(() => console.log("3")); // microtask
console.log("4");
// 1, 4, 3, 2
```

`2` comes last despite a 0 ms delay, because the microtask queue is drained
first. The follow-up: an infinite chain of microtasks **starves** the macrotask
queue and freezes the page — microtask priority is not free.
Worked example: [`examples/javascript/async/promises_and_event_loop.js`](../../examples/javascript/async/promises_and_event_loop.js).

---

### 🟡 Q. How does `this` get its value?

**Answer.** In a normal function `this` is determined by **how it is called**,
not where it is defined. Four rules, in precedence order:

1. **`new`** — `this` is the new object.
2. **Explicit** — `call`, `apply`, `bind` set it.
3. **Implicit** — `obj.method()` sets `this` to `obj`.
4. **Default** — `undefined` in strict mode, `globalThis` otherwise.

Arrow functions ignore all four: they have **no `this` of their own** and inherit
it lexically from the enclosing scope. That is the fix for the classic bug:

```js
class Timer {
  constructor() { this.seconds = 0; }
  startBroken() { setInterval(function () { this.seconds++; }, 1000); }  // wrong `this`
  start()       { setInterval(() => { this.seconds++; }, 1000); }        // correct
}
```

Worked example: [`examples/javascript/basics/this_and_binding.js`](../../examples/javascript/basics/this_and_binding.js).

---

### 🟡 Q. `==` vs `===`?

**Answer.** `===` compares type and value with no conversion. `==` coerces first,
using rules that are genuinely surprising:

```js
0 == "";          // true
0 == "0";         // true
"" == "0";        // false   <- not transitive!
null == undefined // true
null == 0         // false
NaN == NaN        // false
```

**Always use `===`.** The one accepted exception is `x == null`, which checks for
`null` or `undefined` in a single test.

For `NaN`, use `Number.isNaN(x)`. `NaN !== NaN` is required by IEEE 754 and is
also why `[NaN].includes(NaN)` is true (it uses SameValueZero) while
`[NaN].indexOf(NaN)` is -1 (it uses `===`).

---

### 🟡 Q. What is prototypal inheritance?

**Answer.** Every object has a hidden link to another object, its **prototype**.
A property miss walks up that chain until it is found or the chain ends at `null`.

```js
const animal = { speak() { return `${this.name} makes a sound`; } };
const dog = Object.create(animal);
dog.name = "Rex";
dog.speak();      // found on the prototype
```

`class` syntax is sugar over this — there are no classical classes underneath,
just constructor functions and prototype objects. That is why you can add a
method to every existing instance at runtime by assigning to the prototype,
which classical inheritance does not allow.

---

### 🟡 Q. Promise, async/await, and how do you run things in parallel?

**Answer.** A promise represents a value that is not ready yet, in one of three
states: pending, fulfilled, rejected. `async/await` is syntax over promises — an
`async` function always returns one, and `await` suspends until it settles.

The mistake that matters:

```js
// Sequential — 3 seconds, and usually a bug
const a = await fetchA();
const b = await fetchB();

// Parallel — 1 second
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

If the calls are independent, awaiting them one at a time wastes the whole
latency of each. Know the four combinators:

- `Promise.all` — all succeed, or reject on the **first** failure.
- `Promise.allSettled` — wait for all, never rejects; inspect each result.
- `Promise.race` — first to **settle**, success or failure (used for timeouts).
- `Promise.any` — first to **succeed**.

Worked example:
[`examples/typescript/async/async_await_parallel_vs_sequential.ts`](../../examples/typescript/async/async_await_parallel_vs_sequential.ts).

---

### 🟡 Q. Debounce vs throttle?

**Answer.** Both limit how often a function runs, in opposite ways.

- **Debounce** — wait until the events *stop*, then run once. Search-as-you-type,
  resize handlers, autosave.
- **Throttle** — run at most once per interval while events continue. Scroll
  position, mouse tracking, analytics.

"Fire after the user stops typing" is debounce; "fire at most every 200 ms while
scrolling" is throttle. Worked example:
[`examples/javascript/utilities/debounce_with_cancellation.js`](../../examples/javascript/utilities/debounce_with_cancellation.js).
