/**
 * Topic: Optional chaining (?.) and nullish coalescing (??).
 *
 * Concepts:
 * - `?.` — stop the chain at null/undefined instead of crashing
 * - `?.()` optional method calls, `?.[key]` optional property access
 * - `??` — fallback ONLY for null/undefined (not for 0, "", false)
 * - Chaining `??` together
 * - Why `||` is a different (often wrong) default
 *
 * These two operators replace whole families of defensive
 * `if (x && x.y && x.y.z)` code with readable one-liners.
 *
 * Validate (Node 22+): node --experimental-strip-types optional_chaining.ts
 */

// --- Sample data: some records are complete, some are sparse ----------------

type Address = { city?: string; zip?: string };
type Person = {
  name: string;
  email?: string;      // might be missing
  age?: number;        // might be missing, and 0 is a LEGIT value
  address?: Address;   // might be missing entirely
};

const people: Person[] = [
  { name: "Alice", email: "a@x.y", age: 30, address: { city: "Berlin", zip: "10115" } },
  { name: "Bob", age: 0, address: { city: "Oslo" } },          // age 0!
  { name: "Carol" },                                            // almost nothing
  { name: "Dan", email: "", age: 25, address: {} },            // empty strings/objects
];

// --- 1. Optional chaining: safe deep access ----------------------------------

function describe(p: Person): string {
  // Without ?.: p.address.city would throw when address is missing.
  // With ?.: the whole chain yields undefined at the first gap.
  const city = p.address?.city ?? "unknown city";
  const email = p.email ?? "(no email)";
  return `${p.name}: ${email}, ${city}`;
}

for (const p of people) {
  console.log(describe(p));
}
// -> Alice: a@x.y, Berlin
// -> Bob: (no email), Oslo
// -> Carol: (no email), unknown city
// -> Dan: , unknown city   (empty email is kept by ??)

// --- 2. Optional member access: methods and bracket notation -------------------

type Store = {
  get?: (key: string) => number | undefined;
  data?: Record<string, number>;
};

const fullStore: Store = {
  get: (k) => fullStore.data?.[k],
  data: { hits: 42 },
};
const bareStore: Store = {};

// Optional CALL: store.get?.("hits") — skips the call if get is missing.
console.log("full store hits:", fullStore.get?.("hits"));  // -> 42
console.log("bare store hits:", bareStore.get?.("hits"));  // -> undefined

// Optional BRACKET: data?.[key] for dynamic keys.
const key = "hits";
console.log("bare data lookup:", bareStore.data?.[key]);    // -> undefined

// --- 3. ?? versus || : the critical difference -----------------------------------

function showDefaults(p: Person) {
  // ?? : fallback only for null/undefined.
  const ageNullish = p.age ?? 18;
  // || : fallback for ANY falsy value — 0, "", false, NaN, null, undefined.
  const ageOr = p.age || 18;
  return { ageNullish, ageOr };
}

const zeroAge = showDefaults(people[1]); // Bob has age: 0
console.log("age 0 with ?? :", zeroAge.ageNullish); // -> 0   (kept!)
console.log("age 0 with || :", zeroAge.ageOr);      // -> 18  (replaced — wrong!)

// --- 4. Chaining fallbacks -----------------------------------------------------------

function normalize(p: Person): string {
  // Multiple ?? in a row: first non-nullish wins.
  const contact = p.email ?? p.address?.city ?? "no contact info";
  return contact;
}

for (const p of people) {
  console.log(`${p.name} contact: ${normalize(p)}`);
}
// -> Alice contact: a@x.y
// -> Bob contact: Oslo
// -> Carol contact: no contact info
// -> Dan contact: (empty!)   email is "" — falsy but NOT nullish, so ?? keeps it

// If you want to treat "" as missing too, normalize first:
const nonEmpty = (s: string | undefined) => (s && s.length > 0 ? s : undefined);
console.log("Dan with nonEmpty:", normalize({ ...people[3], email: nonEmpty(people[3].email) }));
// -> Dan with nonEmpty: no contact info
