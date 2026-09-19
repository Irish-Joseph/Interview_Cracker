/**
 * Topic: Error handling - throwing, catching, and not losing the cause.
 *
 * JavaScript lets you throw ANY value, which is exactly why discipline
 * matters: throw an Error (or a subclass) so you keep a stack trace, and
 * never swallow one silently.
 *
 * Concepts:
 * - Custom Error subclasses, and why `name` and `Error.captureStackTrace` help
 * - try / catch / finally, and that finally runs even after return
 * - `cause` (ES2022): wrap an error without discarding the original
 * - Narrowing in catch: instanceof, because catch has no type
 * - async/await errors, and the unhandled-rejection trap
 * - Promise.all vs Promise.allSettled when failures are expected
 * - Retry with a typed "is this retryable?" decision
 */

// ---------------------------------------------------------------------------
// 1. Custom error types
// ---------------------------------------------------------------------------

class AppError extends Error {
  constructor(message, options = {}) {
    super(message, options); // passes { cause } through in ES2022+
    // Without this the name is "Error", which makes logs misleading.
    this.name = this.constructor.name;
  }
}

class ValidationError extends AppError {
  constructor(field, message) {
    super(message);
    this.field = field; // carry the context a caller needs to react
  }
}

class HttpError extends AppError {
  constructor(status, message, options) {
    super(message, options);
    this.status = status;
  }

  // A typed decision beats scattering `if (status === 503)` everywhere.
  get retryable() {
    return this.status >= 500 || this.status === 429;
  }
}

// ---------------------------------------------------------------------------
// 2. try / catch / finally
// ---------------------------------------------------------------------------

function parseConfig(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed.port !== "number") {
      throw new ValidationError("port", "port must be a number");
    }
    return parsed;
  } catch (error) {
    // catch receives ANY thrown value, so narrow before using it.
    if (error instanceof ValidationError) {
      throw error; // already ours: rethrow unchanged, trace intact
    }
    if (error instanceof SyntaxError) {
      // Wrap, preserving the original via `cause`. Losing the cause is the
      // single most common way to make a production bug unreadable.
      throw new AppError(`config is not valid JSON`, { cause: error });
    }
    throw error;
  } finally {
    // Runs on success, on throw, and on early return. Use it for cleanup.
    // Do NOT return from finally: it silently overrides the real result.
  }
}

function finallyWins() {
  try {
    return "from try";
  } finally {
    // eslint-disable-next-line no-unsafe-finally
    return "from finally"; // overrides the try's return - almost always a bug
  }
}

// ---------------------------------------------------------------------------
// 3. Async errors
// ---------------------------------------------------------------------------

function flakyFetch(attempt) {
  // Simulates a server that fails twice, then succeeds.
  return new Promise((resolve, reject) => {
    if (attempt < 3) {
      reject(new HttpError(503, `service unavailable (attempt ${attempt})`));
    } else {
      resolve({ ok: true, attempt });
    }
  });
}

async function withRetry(operation, { attempts = 3, onRetry = () => {} } = {}) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      return await operation(attempt);
    } catch (error) {
      lastError = error;
      // Only retry what is worth retrying. Retrying a 400 just wastes time.
      if (!(error instanceof HttpError) || !error.retryable || attempt === attempts) {
        throw error;
      }
      onRetry(attempt, error);
    }
  }
  throw lastError;
}

// ---------------------------------------------------------------------------
// 4. Several operations at once
// ---------------------------------------------------------------------------

async function loadAll(ids) {
  // Promise.all REJECTS on the first failure and discards the successes.
  // Use it when any failure makes the whole result useless.
  return Promise.all(ids.map((id) => lookup(id)));
}

async function loadWhatWeCan(ids) {
  // allSettled never rejects: you inspect each outcome. Use it when a
  // partial result is still worth having.
  const results = await Promise.allSettled(ids.map((id) => lookup(id)));
  return {
    loaded: results.filter((r) => r.status === "fulfilled").map((r) => r.value),
    failed: results
      .filter((r) => r.status === "rejected")
      .map((r) => r.reason.message),
  };
}

async function lookup(id) {
  if (id < 0) throw new ValidationError("id", `id must be positive, got ${id}`);
  return { id, name: `user-${id}` };
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

async function main() {
  console.log("-- custom errors --");
  try {
    parseConfig('{"port": "8080"}');
  } catch (error) {
    console.log(`  ${error.name}: ${error.message} (field: ${error.field})`);
    console.log("  instanceof AppError:", error instanceof AppError);
    console.log("  instanceof Error:   ", error instanceof Error);
  }

  console.log("-- wrapping with cause --");
  try {
    parseConfig("{not json");
  } catch (error) {
    console.log(`  ${error.name}: ${error.message}`);
    console.log(`  caused by -> ${error.cause.name}: ${error.cause.message.slice(0, 40)}`);
  }

  console.log("-- finally overrides return --");
  console.log("  finallyWins():", finallyWins(), "(the try's value was lost)");

  console.log("-- retry only what is retryable --");
  const result = await withRetry(flakyFetch, {
    attempts: 4,
    onRetry: (attempt, error) => console.log(`  attempt ${attempt} failed: ${error.message}`),
  });
  console.log("  succeeded:", JSON.stringify(result));

  console.log("-- a non-retryable error fails fast --");
  try {
    await withRetry(async () => {
      throw new HttpError(400, "bad request");
    });
  } catch (error) {
    console.log(`  gave up immediately: ${error.name} ${error.status} (retryable=${error.retryable})`);
  }

  console.log("-- all vs allSettled --");
  try {
    await loadAll([1, -2, 3]);
  } catch (error) {
    console.log("  Promise.all rejected on the first failure:", error.message);
  }
  console.log("  allSettled:", JSON.stringify(await loadWhatWeCan([1, -2, 3])));

  console.log("-- the unhandled rejection trap --");
  // Calling an async function WITHOUT await or .catch() produces an
  // unhandled rejection. In Node this terminates the process by default.
  const promise = lookup(-1);
  promise.catch((error) => console.log("  handled late:", error.message));
}

main();

/* Expected output:
-- custom errors --
  ValidationError: port must be a number (field: port)
  instanceof AppError: true
  instanceof Error:    true
-- wrapping with cause --
  AppError: config is not valid JSON
  caused by -> SyntaxError: ...
-- finally overrides return --
  finallyWins(): from finally (the try's value was lost)
-- retry only what is retryable --
  attempt 1 failed: service unavailable (attempt 1)
  attempt 2 failed: service unavailable (attempt 2)
  succeeded: {"ok":true,"attempt":3}
-- a non-retryable error fails fast --
  gave up immediately: HttpError 400 (retryable=false)
-- all vs allSettled --
  Promise.all rejected on the first failure: id must be positive, got -2
  allSettled: {"loaded":[{"id":1,...},{"id":3,...}],"failed":["id must be positive, got -2"]}
-- the unhandled rejection trap --
  handled late: id must be positive, got -1
*/
