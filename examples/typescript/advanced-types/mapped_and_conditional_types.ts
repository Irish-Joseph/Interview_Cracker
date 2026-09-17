/**
 * Topic: Mapped and conditional types — writing types that compute.
 *
 * Concepts:
 * - Mapped types: { [K in keyof T]: ... } and key remapping with `as`
 * - Modifiers: adding/removing `?` and `readonly` with + and -
 * - Conditional types: T extends U ? X : Y
 * - `infer` to extract a type from inside another type
 * - Distribution over unions, and how to switch it off
 * - Template literal types for building string keys
 *
 * This is the machinery the built-in helpers are made of: Partial, Required,
 * Readonly, Exclude, ReturnType and friends are all a line or two of this.
 *
 * Validate (Node 22+): node --experimental-strip-types mapped_and_conditional_types.ts
 * Type-check:          tsc --strict --noEmit mapped_and_conditional_types.ts
 */

interface Product {
  id: number;
  title: string;
  price: number;
  tags: string[];
}

// --- 1. A mapped type: transform every property ---------------------------

// "For each key K of T, produce a property of the same name whose type is
// T[K]" — the identity mapping. Everything else is a variation of this.
type Identity<T> = { [K in keyof T]: T[K] };

// Make everything optional — this is exactly how Partial<T> is defined.
type MyPartial<T> = { [K in keyof T]?: T[K] };

// Modifiers can be REMOVED with a minus sign, which is how Required works.
type MyRequired<T> = { [K in keyof T]-?: T[K] };
type MyMutable<T> = { -readonly [K in keyof T]: T[K] };

// Change the value type instead of the modifier: everything becomes a string.
type Stringified<T> = { [K in keyof T]: string };

const draft: MyPartial<Product> = { title: "Desk lamp" }; // id/price may be absent
const asText: Stringified<Product> = {
  id: "42",
  title: "Desk lamp",
  price: "39.99",
  tags: "lighting,office",
};

console.log("1. partial draft:", draft);
console.log("1. stringified: ", asText);

// --- 2. Key remapping with `as` -------------------------------------------

// Rename keys while mapping. Template literal types build the new names.
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

// Getters<Product> is:
//   { getId(): number; getTitle(): string; getPrice(): number; getTags(): string[] }
const productApi: Getters<Product> = {
  getId: () => 42,
  getTitle: () => "Desk lamp",
  getPrice: () => 39.99,
  getTags: () => ["lighting", "office"],
};

console.log("2. remapped keys:", Object.keys(productApi));
console.log("2. getTitle():   ", productApi.getTitle());

// Returning `never` from the key position DROPS the property — that is how
// filtering types are written.
type OnlyStrings<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

// OnlyStrings<Product> keeps just { title: string }
const labels: OnlyStrings<Product> = { title: "Desk lamp" };
console.log("2. filtered to string props:", labels);

// --- 3. Conditional types: a type-level if/else ---------------------------

type IsArray<T> = T extends unknown[] ? "array" : "not array";

// Resolved at compile time:
//   IsArray<string[]>  ->  "array"
//   IsArray<number>    ->  "not array"
const arrayVerdict: IsArray<string[]> = "array";
const scalarVerdict: IsArray<number> = "not array";
console.log("3. verdicts:", arrayVerdict, "|", scalarVerdict);

// Exclude and Extract are one-liners over a union:
type MyExclude<T, U> = T extends U ? never : T;
type MyExtract<T, U> = T extends U ? T : never;

type Status = "draft" | "review" | "published" | "archived";
type Visible = MyExclude<Status, "draft" | "archived">; // "review" | "published"

const shown: Visible[] = ["review", "published"];
console.log("3. visible statuses:", shown);

// --- 4. Distribution over unions ------------------------------------------

// A NAKED type parameter in a conditional distributes over each union member:
//   MyExclude<"a" | "b", "a">
//     = ("a" extends "a" ? never : "a") | ("b" extends "a" ? never : "b")
//     = never | "b" = "b"
//
// Wrapping both sides in a tuple switches distribution OFF, which matters
// when you want to test the union AS A WHOLE:
type IsUnionOfStrings<T> = [T] extends [string] ? true : false;

const bothStrings: IsUnionOfStrings<"a" | "b"> = true;
const mixed: IsUnionOfStrings<"a" | 1> = false;
console.log("4. non-distributed check:", bothStrings, "|", mixed);

// --- 5. `infer`: pulling a type back out ----------------------------------

// "If T looks like an array of some element type, capture that element type
// and return it." infer declares a type variable inside the pattern.
type ElementOf<T> = T extends (infer E)[] ? E : never;

type Tag = ElementOf<Product["tags"]>; // string

// The same trick recovers a function's return type and parameters:
type MyReturnType<F> = F extends (...args: never[]) => infer R ? R : never;
type FirstParam<F> = F extends (first: infer P, ...rest: never[]) => unknown ? P : never;

function loadProduct(id: number, force: boolean): { id: number; title: string } {
  return { id, title: force ? "reloaded" : "cached" };
}

type Loaded = MyReturnType<typeof loadProduct>; // { id: number; title: string }
type LoadArg = FirstParam<typeof loadProduct>; // number

const loaded: Loaded = loadProduct(7, true);
const argument: LoadArg = 7;
const firstTag: Tag = "lighting";
console.log("5. inferred return:", loaded, "| arg:", argument, "| tag:", firstTag);

// Recursive conditional + infer: unwrap nested promises.
type Awaitable<T> = T extends Promise<infer Inner> ? Awaitable<Inner> : T;
type Resolved = Awaitable<Promise<Promise<string>>>; // string
const resolved: Resolved = "done";
console.log("5. unwrapped promise type holds:", resolved);

// --- 6. Combining them: a practical deep-readonly -------------------------

// Map every property; if the value is itself an object, recurse. Functions
// and arrays need their own branches, which is why the real-world version of
// this type is longer than people expect.
type DeepReadonly<T> = T extends (...args: never[]) => unknown
  ? T
  : T extends (infer E)[]
    ? readonly DeepReadonly<E>[]
    : T extends object
      ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
      : T;

interface Config {
  name: string;
  server: { host: string; ports: number[] };
}

const config: DeepReadonly<Config> = {
  name: "api",
  server: { host: "localhost", ports: [80, 443] },
};

// Every one of these is a compile-time error, at any depth:
//   config.name = "other";
//   config.server.host = "other";
//   config.server.ports.push(8080);
console.log("6. deep readonly value:", config.server.host, config.server.ports);

// --- 7. Compile-time assertions -------------------------------------------

// A common trick: types that only compile when the assertion holds. These
// cost nothing at runtime and act as tests for your type-level code.
type Equals<A, B> = (<T>() => T extends A ? 1 : 2) extends <T>() => T extends B
  ? 1
  : 2
  ? true
  : false;
type Expect<T extends true> = T;

type _1 = Expect<Equals<Visible, "review" | "published">>;
type _2 = Expect<Equals<ElementOf<number[]>, number>>;
type _3 = Expect<Equals<MyReturnType<() => void>, void>>;

console.log("7. type-level assertions compiled");

/**
 * Summary:
 * - Mapped type      { [K in keyof T]: ... }   transform every property
 * - Key remapping    ... as `get${K}`          rename or drop keys (never)
 * - Conditional      T extends U ? X : Y       branch at the type level
 * - infer            T extends (infer E)[]     capture a nested type
 * - [T] extends [U]                            compare a union as a whole
 *
 * Reach for these when a type must stay in lockstep with another type.
 * If a hand-written interface would not drift, just write the interface.
 */
