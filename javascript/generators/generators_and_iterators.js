/**
 * Topic: Generators and the iteration protocol.
 *
 * A generator function (`function*`) returns a lazy iterator: the body runs
 * only far enough to produce the next value, then pauses at `yield` until
 * someone asks again. That makes it a natural fit for infinite sequences,
 * streaming pipelines and objects you want to use in `for...of`.
 *
 * Concepts:
 * - function* / yield / yield*
 * - The iterator protocol: { next() -> { value, done } }
 * - Making any object iterable with [Symbol.iterator]
 * - Lazy pipelines that never build an intermediate array
 * - Sending values back in with next(value)
 * - Cleanup with try/finally and early `break`
 */

// ---------------------------------------------------------------------------
// 1. A generator is just a function that can pause
// ---------------------------------------------------------------------------

function* countdown(from) {
  while (from > 0) {
    yield from;
    from -= 1;
  }
  return "liftoff"; // becomes { value: 'liftoff', done: true }
}

// ---------------------------------------------------------------------------
// 2. Infinite sequences are fine, because nothing is computed early
// ---------------------------------------------------------------------------

function* naturals(start = 1) {
  let n = start;
  while (true) {
    yield n;
    n += 1;
  }
}

function* map(iterable, fn) {
  for (const item of iterable) yield fn(item);
}

function* filter(iterable, predicate) {
  for (const item of iterable) {
    if (predicate(item)) yield item;
  }
}

function* take(iterable, count) {
  if (count <= 0) return;
  let taken = 0;
  for (const item of iterable) {
    yield item;
    if (++taken === count) return;
  }
}

// ---------------------------------------------------------------------------
// 3. Any object becomes for...of-able by defining [Symbol.iterator]
// ---------------------------------------------------------------------------

class Playlist {
  #tracks = [];

  add(title, seconds) {
    this.#tracks.push({ title, seconds });
    return this;
  }

  // A generator method satisfies the iterable protocol in one line.
  *[Symbol.iterator]() {
    yield* this.#tracks;
  }

  // Extra named views: each returns a fresh lazy iterator.
  *titles() {
    for (const track of this.#tracks) yield track.title;
  }
}

// ---------------------------------------------------------------------------
// 4. yield* delegates to another iterable (handy for trees)
// ---------------------------------------------------------------------------

function* walk(node) {
  yield node.name;
  for (const child of node.children ?? []) {
    yield* walk(child);
  }
}

// ---------------------------------------------------------------------------
// 5. next(value) sends data back into the paused generator
// ---------------------------------------------------------------------------

function* runningTotal() {
  let total = 0;
  while (true) {
    // The value passed to next() becomes the result of this yield.
    const amount = yield total;
    total += amount ?? 0;
  }
}

// ---------------------------------------------------------------------------
// 6. finally always runs - even when the consumer breaks out early
// ---------------------------------------------------------------------------

function* openResource(name) {
  console.log(`open ${name}`);
  try {
    yield `${name}:row-1`;
    yield `${name}:row-2`;
    yield `${name}:row-3`;
  } finally {
    // for...of calls iterator.return() on break/throw, which resumes here.
    console.log(`close ${name}`);
  }
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

const timer = countdown(3);
console.log(timer.next()); // { value: 3, done: false }
console.log("spread (the `return` value is skipped):", [...countdown(3)]);

// Lazy pipeline: squares of even numbers, first four only.
const squaresOfEvens = take(
  map(
    filter(naturals(), (n) => n % 2 === 0),
    (n) => n * n,
  ),
  4,
);
console.log("lazy pipeline:", [...squaresOfEvens]);

const playlist = new Playlist()
  .add("Intro", 45)
  .add("Main theme", 210)
  .add("Outro", 80);

console.log("total seconds:", [...playlist].reduce((sum, t) => sum + t.seconds, 0));
console.log("titles:", [...playlist.titles()]);

const tree = {
  name: "src",
  children: [
    { name: "index.js" },
    { name: "lib", children: [{ name: "parse.js" }, { name: "format.js" }] },
  ],
};
console.log("walk:", [...walk(tree)]);

const totals = runningTotal();
totals.next(); // prime the generator: run up to the first yield
console.log("after +10:", totals.next(10).value);
console.log("after +5:", totals.next(5).value);

for (const row of openResource("report")) {
  console.log("read", row);
  if (row.endsWith("row-2")) break; // triggers the finally block
}

/* Expected output:
{ value: 3, done: false }
spread (the `return` value is skipped): [ 3, 2, 1 ]
lazy pipeline: [ 4, 16, 36, 64 ]
total seconds: 335
titles: [ 'Intro', 'Main theme', 'Outro' ]
walk: [ 'src', 'index.js', 'lib', 'parse.js', 'format.js' ]
after +10: 10
after +5: 15
open report
read report:row-1
read report:row-2
close report
*/
