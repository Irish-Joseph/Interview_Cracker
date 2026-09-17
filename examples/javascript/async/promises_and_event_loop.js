/**
 * Topic: Promises and the JavaScript event loop.
 *
 * Concepts:
 * - Promise states: pending -> fulfilled | rejected
 * - Writing a promise by hand (the executor)
 * - .then / .catch / .finally chains
 * - Promise.all vs Promise.race vs Promise.allSettled vs Promise.any
 * - Microtasks: why .then callbacks run before the next "tick"
 * - Unhandled rejection awareness
 *
 * A promise is a placeholder for a value that will exist later.
 * Chaining .then avoids callback pyramids; the event loop processes
 * promise callbacks (microtasks) before timers or I/O (macrotasks).
 *
 * Validate: node promises_event_loop.js
 */

// --- 1. A promise from scratch ------------------------------------------------

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// A promise that resolves with a computed value:
function fetchUser(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id === 404) {
        reject(new Error("user not found"));
      } else {
        resolve({ id, name: `user-${id}` });
      }
    }, 30);
  });
}

// --- 2. Chaining: then -> then -> catch -----------------------------------------

async function demoChains() {
  const user = await fetchUser(7);
  console.log("fetched:", JSON.stringify(user));   // -> {"id":7,"name":"user-7"}

  try {
    await fetchUser(404);
  } catch (err) {
    console.log("caught:", err.message);           // -> user not found
  }
}

// The non-async style (same thing):
fetchUser(8)
  .then((u) => console.log("then-style:", u.name)) // -> user-8
  .catch(console.error)
  .finally(() => console.log("finally ran"));        // always

// --- 3. The four combinators -------------------------------------------------------

async function demoCombinators() {
  // Promise.all: ALL must succeed; rejects on the FIRST failure.
  const results = await Promise.all([
    delay(50).then(() => "slow"),
    delay(10).then(() => "fast"),
  ]);
  console.log("all:   ", results.join(","), "(order preserved)");
  // -> all:    slow,fast (order preserved)  — took ~50ms, ran in parallel

  // Promise.race: first to settle wins (great for timeouts).
  const winner = await Promise.race([
    delay(100).then(() => "slow task"),
    delay(20).then(() => "fast task"),
  ]);
  console.log("race:  ", winner);                  // -> fast task

  // Timeout idiom: race your work against a timer.
  const withTimeout = await Promise.race([
    delay(100).then(() => "done"),
    delay(20).then(() => {
      throw new Error("timed out");
    }),
  ]).catch((e) => `error: ${e.message}`);
  console.log("timeout demo:", withTimeout);        // -> error: timed out

  // Promise.allSettled: never throws; reports every outcome.
  const settled = await Promise.allSettled([
    delay(10).then(() => "ok1"),
    delay(10).then(() => {
      throw new Error("boom");
    }),
    delay(10).then(() => "ok2"),
  ]);
  console.log(
    "allSettled:",
    settled.map((s) => (s.status === "fulfilled" ? s.value : s.reason.message)).join(", ")
  );
  // -> allSettled: ok1, boom, ok2

  // Promise.any: first FULFILLED wins; rejects only if ALL fail.
  const anyOk = await Promise.any([
    delay(30).then(() => {
      throw new Error("nope1");
    }),
    delay(15).then(() => "yes!"),
  ]);
  console.log("any:   ", anyOk);                    // -> yes!
}

// --- 4. Event loop: microtasks before macrotasks ------------------------------------

async function demoEventLoop() {
  console.log("1: sync code");

  setTimeout(() => console.log("4: setTimeout (macrotask)"), 0);

  await Promise.resolve(); // next microtask checkpoint
  console.log("3: after one microtask tick");

  // Microtask queue drains BEFORE any timer fires:
  Promise.resolve().then(() => console.log("2: .then (microtask)"));

  // Actual order and why:
  //  1) sync code runs, setTimeout is scheduled (macrotask),
  //     then `await` queues the continuation as a microtask and
  //     suspends this function.
  //  2) The continuation ("3") runs — and ITS body registers the
  //     `.then` microtask, which is queued next.
  //  3) The `.then` callback ("2") runs.
  //  4) Only after ALL microtasks are drained does the timer fire.
  //
  // Expected order:
  // 1: sync code
  // 3: after one microtask tick
  // 2: .then (microtask)
  // 4: setTimeout (macrotask)
}

// --- Run -----------------------------------------------------------------------------

(async () => {
  await demoChains();
  await demoCombinators();
  await demoEventLoop();
})();
