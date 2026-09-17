/**
 * Topic: Implement a debounce function (with cancellation).
 *
 * Concepts:
 * - Closures capturing per-call state
 * - setTimeout / clearTimeout
 * - lastArgs pattern for correct arguments at fire time
 * - cancel() and flush() extensions
 *
 * A debounced function delays invoking `fn` until `wait` ms have
 * passed since the LAST call. Rapid repeated calls keep resetting
 * the timer, so the function fires only after a quiet period.
 *
 * Classic uses: search-as-you-type, resize handlers, autosave.
 *
 * Validate: node debounce_with_cancellation.js
 */

function debounce(fn, wait) {
  let timer = null;      // the pending timer (or null if idle)
  let lastArgs = null;   // arguments from the most recent call

  function debounced(...args) {
    lastArgs = args;
    // Every call cancels the previous pending invocation.
    if (timer !== null) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      timer = null;
      fn(...lastArgs);   // invoke with the LAST set of arguments
    }, wait);
  }

  // Cancel a pending invocation without firing it.
  debounced.cancel = () => {
    if (timer !== null) {
      clearTimeout(timer);
      timer = null;
      lastArgs = null;
    }
  };

  // Fire the pending invocation immediately (if any).
  debounced.flush = () => {
    if (timer !== null) {
      clearTimeout(timer);
      timer = null;
      fn(...lastArgs);
      lastArgs = null;
    }
  };

  return debounced;
}

// --- Demo with a small fake clock helper ---------------------------------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const log = [];
  const onSearch = debounce((query) => log.push(query), 50);

  // Simulate a user typing "cat" quickly, one character at a time.
  for (const letter of "cat") {
    onSearch(letter);
    await sleep(20);
  }

  await sleep(80); // allow the 50ms debounce window to elapse
  console.log("fired with:", JSON.stringify(log));
  // -> fired with: ["t"]
  // Only the LAST call's arguments were used; the earlier ones
  // were cancelled by subsequent calls.

  // Demonstrate cancel():
  const counter = { value: 0 };
  const increment = debounce(() => counter.value++, 30);

  increment();
  increment();
  increment();
  increment.cancel();   // wipe out the pending call
  await sleep(60);
  console.log("after cancel, counter =", counter.value); // -> 0

  // Demonstrate flush():
  const another = debounce(() => (counter.value += 100), 30);
  another();
  another.flush();      // fire immediately instead of waiting
  await sleep(60);
  console.log("after flush,  counter =", counter.value); // -> 100
}

main();
