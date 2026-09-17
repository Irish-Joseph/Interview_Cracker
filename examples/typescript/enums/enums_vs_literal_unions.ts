/**
 * Topic: enum vs union of string literals vs `as const` object.
 *
 * TypeScript offers three ways to model "one of a fixed set of values".
 * They look interchangeable but behave very differently at runtime, so
 * picking the wrong one leaks JavaScript you did not want or loses the
 * value list you did want.
 *
 * Concepts:
 * - Numeric vs string enums, and the reverse mapping a numeric enum emits
 * - Union of string literals: zero runtime cost, but no value to iterate
 * - `as const` object + derived union: the best of both
 * - Exhaustiveness checking with `never`
 *
 * Validate (Node 22+): node --experimental-transform-types enums_vs_literal_unions.ts
 *
 * Note the flag: --experimental-strip-types refuses this file. Strip-only mode
 * can delete types but cannot emit code, and an enum needs a real object to be
 * generated - which is exactly the difference this example is about.
 */

// ---------------------------------------------------------------------------
// 1. Enums exist at runtime
// ---------------------------------------------------------------------------

enum Direction {
  Up, // 0
  Down, // 1
  Left, // 2
  Right, // 3
}

enum LogLevel {
  Debug = "debug",
  Info = "info",
  Error = "error",
}

// A numeric enum compiles to an object with a *reverse* mapping, so you can
// go both ways. A string enum does not get that reverse mapping.
const directionName: string = Direction[Direction.Left]; // "Left"

// ---------------------------------------------------------------------------
// 2. A union of string literals is erased completely
// ---------------------------------------------------------------------------

type Status = "pending" | "shipped" | "delivered";

// This is purely a compile-time type. There is no `Status` value to import,
// loop over, or validate unknown input against at runtime.
const current: Status = "shipped";

// @ts-expect-error "returned" is not part of the union
const broken: Status = "returned";

// ---------------------------------------------------------------------------
// 3. `as const` object: one declaration, both a value and a type
// ---------------------------------------------------------------------------

const HttpMethod = {
  Get: "GET",
  Post: "POST",
  Delete: "DELETE",
} as const;

// `as const` freezes the literal types, so this is "GET" | "POST" | "DELETE"
// rather than the widened `string`.
type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];

const methods: HttpMethod[] = Object.values(HttpMethod); // iterable at runtime

function isHttpMethod(value: string): value is HttpMethod {
  return methods.includes(value as HttpMethod);
}

// ---------------------------------------------------------------------------
// 4. Exhaustiveness: the compiler catches the case you forgot
// ---------------------------------------------------------------------------

function describe(status: Status): string {
  switch (status) {
    case "pending":
      return "Waiting for the warehouse";
    case "shipped":
      return "On its way";
    case "delivered":
      return "Signed for";
    default: {
      // If a fourth status is added, `status` is no longer `never` here
      // and this line fails to compile - a free reminder to update it.
      const unreachable: never = status;
      return unreachable;
    }
  }
}

function levelPriority(level: LogLevel): number {
  switch (level) {
    case LogLevel.Debug:
      return 10;
    case LogLevel.Info:
      return 20;
    case LogLevel.Error:
      return 30;
  }
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

console.log("Direction.Left =", Direction.Left);
console.log("reverse mapping:", directionName);
console.log("LogLevel.Info =", LogLevel.Info, "priority", levelPriority(LogLevel.Info));

console.log("status:", current, "->", describe(current));

console.log("methods at runtime:", methods);
console.log("isHttpMethod('POST'):", isHttpMethod("POST"));
console.log("isHttpMethod('PATCH'):", isHttpMethod("PATCH"));
console.log("broken (compile error, still runs):", broken);

/* Which one should you use?
 *
 * union of literals  - simplest; use when you never need the list at runtime
 * `as const` object  - use when you need both the type AND an iterable value
 * string enum        - fine in app code; adds a real object to the bundle
 * numeric enum       - avoid unless you need the reverse mapping; the values
 *                      are positional, so reordering members is a breaking
 *                      change for anything already persisted
 * const enum         - inlined at compile time, but unsupported under
 *                      isolatedModules/transpile-only builds; skip it
 *
 * Expected output:
 * Direction.Left = 2
 * reverse mapping: Left
 * LogLevel.Info = info priority 20
 * status: shipped -> On its way
 * methods at runtime: [ 'GET', 'POST', 'DELETE' ]
 * isHttpMethod('POST'): true
 * isHttpMethod('PATCH'): false
 * broken (compile error, still runs): returned
 */
