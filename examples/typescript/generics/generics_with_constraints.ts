/**
 * Topic: Generic functions with constraints.
 *
 * Concepts:
 * - Type parameters (`<T>`) for reusable, type-safe code
 * - Constraining a type parameter with `extends`
 * - Using the constraint to access members safely
 * - Generic defaults and multiple type parameters
 * - Why generics beat `any` and casting
 *
 * A generic function works with many types while the compiler still
 * checks every use. A constraint (`extends`) says "T can be any type
 * that AT LEAST looks like this".
 *
 * Validate (Node 22+): node --experimental-strip-types generics_constraints.ts
 */

// --- 1. Unconstrained generic: identity ----------------------------------

/** The simplest generic: returns its input unchanged. */
function identity<T>(value: T): T {
  return value;
}

const n: number = identity(42);        // T inferred as number
const s: string = identity("hello");   // T inferred as string

// --- 2. Constrained generic: access members safely -----------------------

// Without a constraint, `item.name` would be an error, because a
// bare `T` tells the compiler nothing about T's shape.

function firstNamed<T extends { name: string }>(items: T[]): T {
  return items[0];
}

const teams = [
  { name: "Alpha", size: 3 },
  { name: "Beta", size: 5 },
];
const lead = firstNamed(teams);
console.log(`lead team: ${lead.name} (size ${lead.size})`);
// The full object type is preserved — no information lost.

// --- 3. Multiple type parameters, one constrained -------------------------

/**
 * Picks `key` from `obj` and returns its value's type.
 * `K extends keyof T` lets us index T safely.
 */
function pick<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: 7, email: "a@b.c", active: true };
const email: string = pick(user, "email");
const active: boolean = pick(user, "active");
// pick(user, "nope") would be a compile-time error.
console.log(`user ${email} active=${active}`);

// --- 4. Constraint + default: flexible but safe ---------------------------

/**
 * Deep-ish "get property" with a default: if no constraint info is
 * needed, callers may omit the second type argument.
 */
function getProperty<T, K extends keyof T = never>(
  obj: T,
  key: K
): T[K] {
  return obj[key];
}

const flags = { debug: false, verbose: true };
console.log("verbose flag:", getProperty(flags, "verbose"));

// --- 5. What the constraint buys us ---------------------------------------

// BAD (no constraint): would have to cast to any to read .name.
// BAD (any): erases all type safety at the call site.
// GOOD (constraint): compiler verifies the shape once, here, and
// every caller keeps precise types for free.

interface Point {
  x: number;
  y: number;
}

function distanceFromOrigin<T extends Point>(p: T): number {
  // p.x and p.y are known to exist because T extends Point.
  return Math.sqrt(p.x ** 2 + p.y ** 2);
}

// A subtype with extra fields still works, and keeps its extra fields.
const p = { x: 3, y: 4, label: "origin-ish" };
console.log(`distance: ${distanceFromOrigin(p)} (${p.label})`);

// Expected output:
// lead team: Alpha (size 3)
// user a@b.c active=true
// verbose flag: true
// distance: 5 (origin-ish)
