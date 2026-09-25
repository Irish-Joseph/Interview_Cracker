// Object.freeze is SHALLOW: it locks the top level only
//
// Concepts:
//   - freeze prevents adding/removing/renaming top-level properties
//   - nested objects are still fully mutable
//   - freeze is not deep, and not "sealed plus" — check Object.isFrozen vs sealed
//   - the practical fixes: Object.assign spread, structuredClone, or a deep-freeze helper
//
// Run: node examples/javascript/objects/object_freeze_is_shallow.js
// Expected output: at the bottom of this file.

"use strict"; // freeze only really bites in strict mode; sloppy mode fails silently

const config = {
  app: "demo",
  limits: { connections: 10, timeout: 30 },
  features: ["a", "b"],
};

Object.freeze(config);

// 1. Top level is locked. In strict mode the write throws;
//    in sloppy mode it fails SILENTLY — the failure mode that made
//    "use strict" exist. Both shown:
console.log("Object.isFrozen(config):", Object.isFrozen(config));

let threw = false;
try { config.newProp = "added"; } catch { threw = true; }
console.log("strict-mode write threw:", threw);

// (0, eval) = indirect eval: runs in the global scope, so the module's
// "use strict" does NOT leak in — this really is sloppy mode.
const sloppy = (0, eval)('(function () { var o = Object.freeze({}); o.x = 1; return o.x; })()');
console.log("same write in sloppy mode threw but: " + sloppy + " (silently dropped)");

// 2. But the contents are not frozen at all.
config.limits.connections = 999;   // works — nested object is untouched
config.features.push("c");          // works — arrays are objects too
console.log("nested after 'frozen' writes:");
console.log("  limits:", config.limits);
console.log("  features:", config.features);

// 3. Spreading copies the SAME references — same trap as shallow copy.
const frozen = Object.freeze({ name: "x", opts: { verbose: false } });
const draft = { ...frozen };              // top level copied, opts shared
draft.opts.verbose = true;                // no error: opts was never frozen
console.log("spread did not protect nested state, frozen.opts:", frozen.opts);

// Rebinding the top-level key IS allowed, because freeze only locks
// the top-level property table of the object it was called on:
const renamed = { ...frozen, opts: { verbose: true } };
console.log("rebind via spread is fine, renamed.opts:", renamed.opts);

// 4. The two idiomatic fixes.
// a) structuredClone: a real deep copy, nothing frozen.
const clone = structuredClone(config);
clone.limits.connections = 42;
console.log("structuredClone is independent:", clone.limits.connections === 42, "original intact:", config.limits.connections === 999);

// b) a deep freeze, if you want immutability all the way down.
function deepFreeze(value, seen = new WeakSet()) {
  if (value === null || typeof value !== "object" || seen.has(value)) return value;
  seen.add(value);                    // cycles cannot hang the recursion
  for (const key of Reflect.ownKeys(value)) deepFreeze(value[key], seen);
  return Object.freeze(value);
}

const locked = deepFreeze({ a: { b: [1, 2] } });
let deepThrew = false;
try { locked.a.b.push(3); } catch { deepThrew = true; }   // TypeError in strict mode
console.log("deepFreeze works; inner push threw:", deepThrew,
  "top frozen:", Object.isFrozen(locked),
  "nested frozen:", Object.isFrozen(locked.a),
  "array frozen:", Object.isFrozen(locked.a.b));

// Rule of thumb: freeze documents "this object is stable", not "this
// structure is immutable". For the latter, deepFreeze — or don't mutate
// at all and use spread/clone instead.

// --- Actual output --------------------------------------------------------
// Object.isFrozen(config): true
// strict-mode write threw: true
// same write in sloppy mode threw but: undefined (silently dropped)
// nested after 'frozen' writes:
//   limits: { connections: 999, timeout: 30 }
//   features: [ 'a', 'b', 'c' ]
// spread did not protect nested state, frozen.opts: { verbose: true }
// rebind via spread is fine, renamed.opts: { verbose: true }
// structuredClone is independent: true original intact: true
// deepFreeze works; inner push threw: true top frozen: true nested frozen: true array frozen: true
