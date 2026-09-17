/**
 * Topic: async/await — parallel vs sequential async work.
 *
 * Concepts:
 * - async functions always return a Promise
 * - await suspends without blocking the event loop
 * - Promise.all: run promises IN PARALLEL, wait for all
 * - Promise.allSettled: survive individual failures
 * - try/catch around awaited promises
 * - Measuring the difference between parallel and sequential
 *
 * The key idea: `await` in a loop makes requests SERIAL (total
 * time = sum). Promise.all makes them PARALLEL (total time ≈ max).
 * That single distinction is the most common performance bug in
 * async code.
 *
 * Validate (Node 22+): node --experimental-strip-types async_await_patterns.ts
 */

/** Fake network call: resolves after `ms` with a value. */
function fetchItem(id: number, ms: number): Promise<string> {
  return new Promise((resolve) => setTimeout(() => resolve(`item-${id}`), ms));
}

/** A call that always fails — for the allSettled demo. */
function failingFetch(ms: number): Promise<string> {
  return new Promise((_, reject) => setTimeout(() => reject(new Error("500")), ms));
}

async function main() {
  // --- 1. Basic await: sequential (SLOW for independent calls) ------------
  const t0 = Date.now();
  const seq: string[] = [];
  for (let i = 1; i <= 3; i++) {
    const item = await fetchItem(i, 100); // waits each time
    seq.push(item);
  }
  console.log(`sequential: [${seq.join(", ")}] in ${Date.now() - t0}ms`);
  // -> ~300ms  (100 + 100 + 100)

  // --- 2. Promise.all: parallel (FAST) --------------------------------------
  const t1 = Date.now();
  const parallel = await Promise.all([
    fetchItem(1, 100),
    fetchItem(2, 100),
    fetchItem(3, 100),
  ]);
  console.log(`parallel:   [${parallel.join(", ")}] in ${Date.now() - t1}ms`);
  // -> ~100ms  (they overlap)

  // Order is preserved: results line up with the input array,
  // regardless of which promise resolves first.
  const mixed = await Promise.all([fetchItem(1, 200), fetchItem(2, 50)]);
  console.log(`order kept: [${mixed.join(", ")}]`);
  // -> [item-1, item-2]  even though item-2 finished first

  // --- 3. try/catch: one failure rejects the whole Promise.all --------------
  try {
    await Promise.all([fetchItem(1, 50), failingFetch(50)]);
  } catch (err) {
    console.log(`Promise.all rejected: ${(err as Error).message}`);
    // -> 500
  }

  // --- 4. Promise.allSettled: see every outcome, never throws ---------------
  const settled = await Promise.allSettled([
    fetchItem(1, 50),
    failingFetch(50),
    fetchItem(2, 50),
  ]);
  for (const outcome of settled) {
    if (outcome.status === "fulfilled") {
      console.log(`  fulfilled: ${outcome.value}`);
    } else {
      console.log(`  rejected:  ${outcome.reason.message}`);
    }
  }
  // -> fulfilled: item-1
  //    rejected:  500
  //    fulfilled: item-2

  // --- 5. Awaiting a non-Promise is fine (resolves immediately) -------------
  const value = await 42; // legal, but rarely useful
  console.log(`awaiting a plain value: ${value}`);
}

main().catch(console.error);
