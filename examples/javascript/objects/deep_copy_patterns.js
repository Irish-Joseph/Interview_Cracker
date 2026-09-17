/**
 * Topic: Deep copy in JavaScript — and why the obvious tricks fail.
 *
 * Concepts:
 * - Shallow vs deep copy (and what "shallow" actually copies)
 * - Why spread / Object.assign are NOT deep
 * - Why JSON.parse(JSON.stringify()) is a trap (functions, Dates,
 *   undefined, NaN, cycles, class instances)
 * - structuredClone: the built-in deep copy
 * - Writing a manual recursive deep clone that handles cycles
 *
 * Validate: node deep_copy_patterns.js
 */

// --- 1. Shallow copy: nested objects are still SHARED --------------------

const user = { name: "Alice", address: { city: "Berlin", zip: "10115" } };

const shallow = { ...user };            // looks like a copy...
shallow.address.city = "Hamburg";

console.log("shallow copy corrupted original city:", user.address.city);
// -> Hamburg  (both objects share the SAME address object)

// Object.assign is also shallow:
const shallow2 = Object.assign({}, user);
shallow2.address.zip = "99999";
console.log("Object.assign shares address too:", user.address.zip);
// -> 99999

// --- 2. The JSON round-trip: works for plain data, fails elsewhere -------

function jsonClone(value) {
  return JSON.parse(JSON.stringify(value));
}

const tricky = {
  when: new Date(2026, 8, 8),     // becomes a STRING
  handler: () => {},              // becomes UNDEFINED
  missing: undefined,             // key DISAPPEARS
  notANumber: NaN,                // becomes null
  set: new Set([1, 2]),           // becomes {}
};

const roundTripped = jsonClone(tricky);
console.log("\nJSON round-trip damage:");
console.log("  Date  ->", typeof roundTripped.when, roundTripped.when);
console.log("  fn    ->", roundTripped.handler);
console.log("  undef ->", "missing" in roundTripped);
console.log("  NaN   ->", roundTripped.notANumber);
console.log("  Set   ->", JSON.stringify(roundTripped.set));

// Circular references crash JSON.stringify entirely:
const cycle = { name: "loop" };
cycle.self = cycle;
try {
  jsonClone(cycle);
} catch (err) {
  console.log("  circular -> throws:", err.constructor.name);
}

// --- 3. structuredClone: the modern built-in ------------------------------

const original = {
  name: "Bob",
  address: { city: "Oslo", zip: "0150" },
  when: new Date(2026, 8, 8),
  set: new Set([1, 2]),
  map: new Map([["k", "v"]]),
};

const deep = structuredClone(original);
deep.address.city = "Copenhagen";
console.log("\nstructuredClone:");
console.log("  nested change isolated:", original.address.city);  // Oslo
console.log("  Date preserved:", deep.when instanceof Date);       // true
console.log("  Set preserved:", deep.set instanceof Set);           // true
console.log("  Map preserved:", deep.map instanceof Map);           // true

// It handles cycles too:
const deepCycle = structuredClone(cycle);
console.log("  cycle preserved:", deepCycle.self === deepCycle);   // true

// --- 4. Manual recursive clone (to see the algorithm) ----------------------

function deepClone(value, seen = new Map()) {
  // Primitives are immutable — return as-is.
  if (value === null || typeof value !== "object") return value;

  // Cycle guard: if we've seen this exact object, return the copy
  // we already built for it.
  if (seen.has(value)) return seen.get(value);

  // Arrays and plain objects: build the new container FIRST,
  // register it, THEN fill it (so cycles can point at it).
  const copy = Array.isArray(value) ? [] : {};
  seen.set(value, copy);

  for (const [key, item] of Object.entries(value)) {
    copy[key] = deepClone(item, seen);
  }
  return copy;
}

const manual = deepClone(user);
manual.address.city = "Munich";
console.log("\nmanual clone:");
console.log("  nested change isolated:", user.address.city);  // Hamburg, not Munich
console.log("  top-level change isolated:", manual.name, "/", user.name);

// Cycle safety:
const manualCycle = deepClone(cycle);
console.log("  cycle preserved:", manualCycle.self === manualCycle); // true
