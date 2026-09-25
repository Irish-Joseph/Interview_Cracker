// Strict type-level equality: why `Equals<T, U>` is not
// `[T] extends [U] ? [U] extends [T] ? true : false : false`
//
// Concepts:
//   - the "naive" mutual-extends test is true for any/unknown/related unions
//   - strict equality compares types by IDENTITY, via a function-type trick
//   - @ts-expect-error as a compile-time test assertion
//
// Run: node --experimental-strip-types examples/typescript/advanced-types/strict_equals_type.ts
// (strip-types executes the runtime part and proves the file is valid TS;
//  the type assertions below are checked by the TS compiler itself —
//  every @ts-expect-error line WILL error if its claim stops being true.)

// --- 1. The naive test, and why it lies -----------------------------------

type NaiveEq<T, U> = [T] extends [U] ? ([U] extends [T] ? true : false) : false;

// The tuple wrapper blocks DISTRIBUTIVITY (so `boolean` does not get
// split into `true | false`), but mutual extends is still an
// ASSIGNABILITY test, not an identity test. The clean counterexamples
// are the top types, where assignability runs in both directions:
type Naive1 = NaiveEq<any, string>;              // true  <- wrong: any is assignable both ways
type Naive2 = NaiveEq<unknown, any>;             // true  <- wrong: the two top types are "equal"
type Naive3 = NaiveEq<any, { a: 1; b: 2 }>;      // true  <- wrong: any swallows any structure

// A direction the naive test CAN catch, for contrast:
type Naive4 = NaiveEq<string, string | number>;  // false — the union is wider, so one
                                                 //      extends direction fails

// The gap matters in real code: a config layer that validates "is this
// schema actually typed?" with NaiveEq<S, any> passes — but NaiveEq lies
// in the other direction too: anything typed `any` compares equal to
// ANYTHING, silently downgrading guarantees.

// --- 2. The strict test ----------------------------------------------------

// The standard definition (from the `expect-type` package, and used by
// type-challenges): compare two types by feeding them into two
// IDENTICAL-but-substituted function types. Function types are compared
// strictly, so the conditional branches must match *exactly* — which is
// only the case when T and U are the same type.

type Equals<T, U> = (<G>() => G extends T ? 1 : 2) extends (<G>() => G extends U ? 1 : 2)
  ? true
  : false;

// --- 3. Compile-time test harness -------------------------------------------

// A failed assertion is a COMPILE error, not a runtime one.
type Assert<T extends true> = T;

// True cases — must compile:
type T1 = Assert<Equals<string, string>>;
type T2 = Assert<Equals<{ a: 1 }, { a: 1 }>>;
type T3 = Assert<Equals<number[], number[]>>;
type T4 = Assert<Equals<1, 1>>;

// False cases — a strict identity test must reject all of these.
// If Equals ever reported `true` for any line below, @ts-expect-error would
// be "unused" and the compiler would flag THAT as an error.
// @ts-expect-error unions are not identity
type F1 = Assert<Equals<string, string | number>>;
// @ts-expect-error any must not compare equal to a specific type
type F2 = Assert<Equals<any, string>>;
// @ts-expect-error unknown and any are different top types
type F3 = Assert<Equals<unknown, any>>;
// @ts-expect-error extra properties matter
type F4 = Assert<Equals<{ a: 1; b: 2 }, { a: 1 }>>;
// @ts-expect-error optionality matters
type F5 = Assert<Equals<string, string | undefined>>;
// @ts-expect-error literal types are not their supertypes
type F6 = Assert<Equals<"a", string>>;
// @ts-expect-error never is the bottom type, not a supertype
type F7 = Assert<Equals<never, string>>;

// --- 4. Where this actually earns its keep ----------------------------------

// A realistic shape: a codec that refuses to accept a schema that is
// `any` (a classic silent-failure path in config code).
type Decode<S> = Equals<S, any> extends true ? "rejected: schema is any" : { [K in keyof S]: S[K] };

type GoodConfig = Decode<{ host: string; port: number }>;   // the mapped object
type BadConfig = Decode<any>;                                // the error string

// Runtime part (what `node --experimental-strip-types` actually executes):
const demo = {
  good: "mapped object",
  bad: "rejected",
  note: "type assertions above are compiler-checked; strip-types only proves the file is valid TS",
};
console.log("strict Equals demo:", JSON.stringify(demo));

// --- Actual output ------------------------------------------------------------
// strict Equals demo: {"good":"mapped object","bad":"rejected","note":"type assertions above are compiler-checked; strip-types only proves the file is valid TS"}
