/**
 * Topic: Type narrowing with the `in` operator and `unknown`.
 *
 * Concepts:
 * - `unknown`: the safe opposite of `any`
 * - Narrowing unknown with typeof / instanceof / in
 * - The `in` operator as a type guard for union members
 * - Exhaustive switch on a finite union
 * - Why `unknown` at boundaries beats `any`
 *
 * `any` turns the compiler OFF for that value. `unknown` turns it
 * ON in strict mode: you must narrow before using it. Data from
 * APIs, JSON, env vars — treat it as unknown, then narrow.
 *
 * Validate (Node 22+): node --experimental-strip-types narrowing_unknown.ts
 */

// --- 1. unknown: can't do anything until narrowed -------------------------

declare function fromTheNetwork(): unknown;

function describe(value: unknown): string {
  // `value.toString()` here would be a COMPILE ERROR:
  // unknown has no known members.

  if (typeof value === "string") {
    return `string of length ${value.length}`; // narrowed: string methods ok
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return `finite number ${value}`;
  }
  if (Array.isArray(value)) {
    return `array of ${value.length}`;
  }
  if (value === null) {
    return "null";
  }
  if (typeof value === "object") {
    return "object";
  }
  return `other (${typeof value})`;
}

console.log(describe("hello"));     // -> string of length 5
console.log(describe(42));          // -> finite number 42
console.log(describe([1, 2, 3]));   // -> array of 3
console.log(describe(null));        // -> null
console.log(describe({ a: 1 }));    // -> object
console.log(describe(true));        // -> other (boolean)

// --- 2. `in`: narrowing union members by their fields ----------------------

type ApiEvent =
  | { type: "click"; x: number; y: number }
  | { type: "key"; key: string }
  | { type: "focus"; target: string };

// An event arriving from untyped JSON:
const raw: unknown = { type: "key", key: "Enter" };

function handleEvent(event: unknown): string {
  if (!isApiEvent(event)) {
    return "rejected: not a known event shape";
  }
  // Now `event` is a real ApiEvent — the union machinery kicks in.
  switch (event.type) {
    case "click":
      return `click at (${event.x}, ${event.y})`;
    case "key":
      return `key pressed: ${event.key}`;
    case "focus":
      return `focus on ${event.target}`;
    default: {
      // Exhaustiveness: if a new event type is added to ApiEvent but
      // not handled here, `event` is `never` and this fails to compile.
      const _exhaustive: never = event;
      throw new Error(`unhandled event: ${JSON.stringify(_exhaustive)}`);
    }
  }
}

/**
 * Runtime validator + type guard. `in` checks work on `unknown`
 * once the value is known to be an object.
 */
function isApiEvent(value: unknown): value is ApiEvent {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  switch (v.type) {
    case "click":
      return typeof v.x === "number" && typeof v.y === "number";
    case "key":
      return typeof v.key === "string";
    case "focus":
      return typeof v.target === "string";
    default:
      return false;
  }
}

console.log(handleEvent(raw));              // -> key pressed: Enter
console.log(handleEvent({ type: "click", x: 1, y: 2 }));
// -> click at (1, 2)
console.log(handleEvent({ bogus: true }));  // -> rejected: not a known event shape

// --- 3. `in` directly on a narrowed object ---------------------------------

function summarize(shape: unknown): string {
  if (typeof shape !== "object" || shape === null) return "not an object";

  // After the object check, `in` is a legitimate type guard.
  if ("radius" in shape) {
    const r = (shape as { radius: number }).radius;
    return `circle r=${r}`;
  }
  if ("width" in shape) {
    const { width, height } = shape as { width: number; height: number };
    return `rectangle ${width}x${height}`;
  }
  return "unknown shape";
}

console.log(summarize({ radius: 2 }));          // -> circle r=2
console.log(summarize({ width: 3, height: 4 })); // -> rectangle 3x4
console.log(summarize("nope"));                 // -> not an object

// --- 4. The discipline, in one paragraph --------------------------------------
//
// Boundaries (JSON.parse, process.argv, API responses) should be
// `unknown`, not `any`. Then:
//   typeof      -> primitives
//   instanceof  -> class instances
//   in          -> object shapes / union members
//   ===         -> literal types
// Every narrowing step is a RUNTIME check that the compiler can
// also verify. `any` skips all of it and hides bugs.

const json = JSON.parse('{"n": 7, "s": "x"}') as unknown;
if (typeof json === "object" && json !== null && "n" in json) {
  const n = (json as { n: number }).n;
  console.log(`parsed n = ${n}`); // -> parsed n = 7
}
