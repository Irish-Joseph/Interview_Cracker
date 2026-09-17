/**
 * Topic: TypeScript utility types (Pick, Omit, Partial, Required,
 *        Record, Readonly).
 *
 * Concepts:
 * - Building new types from existing interfaces
 * - keyof T and indexed access types
 * - Why utility types beat copy-pasted duplicate interfaces
 * - How the compiler keeps them in sync automatically
 *
 * Utility types are "type-level functions": you pass a type in,
 * you get a transformed type out. No code runs — this is purely
 * a compile-time technique.
 *
 * Validate (Node 22+): node --experimental-strip-types utility_types.ts
 */

interface User {
  id: number;
  name: string;
  email: string;
  age?: number; // optional
}

// --- Pick: keep only some properties --------------------------------------
type AdminSummary = Pick<User, "id" | "name">;
const summary: AdminSummary = { id: 1, name: "Alice" };
// summary.age        -> compile error (not part of the type)
// summary = { id: 1 } -> compile error (name is required)

// --- Omit: the opposite — drop some properties ----------------------------
type UserWithoutEmail = Omit<User, "email">;
const noEmail: UserWithoutEmail = { id: 2, name: "Bob" };

// Classic use: an "update" type where every field is optional.
type UserUpdate = Partial<User>;
const patch: UserUpdate = { age: 31 }; // all other fields may be absent

// --- Required: strip optionality ------------------------------------------
type FullUser = Required<User>; // age is no longer optional
const full: FullUser = { id: 3, name: "Carol", email: "c@x.y", age: 25 };

// --- Record: map keys to a value type --------------------------------------
// "For each of these known keys, a number."
type Counters = Record<"views" | "likes" | "shares", number>;
const stats: Counters = { views: 10, likes: 3, shares: 1 };

// --- Readonly: prevent mutation --------------------------------------------
type FrozenUser = Readonly<User>;
const frozen: FrozenUser = { id: 4, name: "Dan", email: "d@x.y" };
// frozen.name = "Eve" -> compile error: read-only

// --- keyof + indexed access: the machinery underneath ----------------------
// Pick/Omit are *defined* with these, so seeing them here closes the loop:
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
type MyPartial<T> = { [K in keyof T]?: T[K] };

// Sanity check: my versions are interchangeable with the built-ins.
const a: MyPick<User, "id"> = { id: 9 };
const b: MyPartial<User> = { email: "only@this.com" };

// --- Demo ------------------------------------------------------------------

const users: User[] = [
  { id: 1, name: "Alice", email: "a@x.y", age: 30 },
  { id: 2, name: "Bob", email: "b@x.y" }, // no age
];

// A function typed with the utility type works for every User.
function summarize(user: Pick<User, "id" | "name">): string {
  return `#${user.id} ${user.name}`;
}

console.log(users.map(summarize).join(", "));
// -> #1 Alice, #2 Bob

console.log(`summary:    ${JSON.stringify(summary)}`);
console.log(`noEmail:    ${JSON.stringify(noEmail)}`);
console.log(`patch:      ${JSON.stringify(patch)}`);
console.log(`full:       ${JSON.stringify(full)}`);
console.log(`stats:      ${JSON.stringify(stats)}`);
console.log(`frozen:     ${JSON.stringify(frozen)}`);
console.log(`MyPick:     ${JSON.stringify(a)}`);
console.log(`MyPartial:  ${JSON.stringify(b)}`);
