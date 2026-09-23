/**
 * Topic: Cooperative cancellation with AbortController.
 *
 * Concepts:
 * - One signal can cancel several operations
 * - throwIfAborted() closes the start-before-listener race
 * - Cleanup removes listeners and timers
 *
 * Run: node examples/javascript/async/abort_controller_cancellation.js
 * Expected output: completed: fast; cancelled: AbortError
 */

function delay(ms, { signal } = {}) {
  return new Promise((resolve, reject) => {
    // Cancellation may have happened before this function started.
    signal?.throwIfAborted();

    const timer = setTimeout(() => {
      signal?.removeEventListener("abort", onAbort);
      resolve(`waited ${ms}ms`);
    }, ms);

    function onAbort() {
      clearTimeout(timer);
      reject(signal.reason);
    }

    signal?.addEventListener("abort", onAbort, { once: true });
  });
}

async function main() {
  const completed = await delay(1);
  console.log("completed: fast");
  if (completed !== "waited 1ms") throw new Error("unexpected result");

  const controller = new AbortController();
  const pending = delay(1_000, { signal: controller.signal });
  controller.abort(new DOMException("user cancelled", "AbortError"));

  try {
    await pending;
    throw new Error("delay should have rejected");
  } catch (error) {
    if (!(error instanceof DOMException) || error.name !== "AbortError") {
      throw error;
    }
    console.log(`cancelled: ${error.name}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
