/**
 * Topic: The array methods you actually reach for every day.
 *
 * Knowing which method expresses your intent is most of what separates
 * readable JavaScript from a pile of for-loops. Each one below answers a
 * different question about a collection.
 *
 * Concepts:
 * - Transforming (map), selecting (filter), folding (reduce)
 * - Asking questions: find, findIndex, some, every, includes
 * - Which methods MUTATE and which return a new array
 * - The copying variants: toSorted, toReversed, with (ES2023)
 * - Chaining, and when a single reduce beats a chain
 */

const people = [
  { name: "Ada", age: 36, city: "London", active: true },
  { name: "Grace", age: 45, city: "Arlington", active: false },
  { name: "Alan", age: 41, city: "London", active: true },
  { name: "Katherine", age: 52, city: "Hampton", active: true },
];

// ---------------------------------------------------------------------------
// 1. map - same length, each item transformed
// ---------------------------------------------------------------------------

const names = people.map((person) => person.name);
const summaries = people.map((person, index) => `${index + 1}. ${person.name} (${person.age})`);

// ---------------------------------------------------------------------------
// 2. filter - same items, fewer of them
// ---------------------------------------------------------------------------

const active = people.filter((person) => person.active);
const londoners = people.filter((person) => person.city === "London");

// ---------------------------------------------------------------------------
// 3. reduce - many items in, one value out
// ---------------------------------------------------------------------------

// ALWAYS pass the initial value (the second argument). Without it, reduce
// throws on an empty array and uses element 0 as the seed otherwise.
const totalAge = people.reduce((sum, person) => sum + person.age, 0);

// reduce is not only for numbers - it builds objects and maps too.
const byCity = people.reduce((groups, person) => {
  (groups[person.city] ||= []).push(person.name);
  return groups;
}, {});

// ---------------------------------------------------------------------------
// 4. Asking questions - these SHORT-CIRCUIT and stop early
// ---------------------------------------------------------------------------

const firstOver40 = people.find((person) => person.age > 40);     // the item, or undefined
const indexOver40 = people.findIndex((person) => person.age > 40); // the index, or -1
const anyInactive = people.some((person) => !person.active);       // boolean
const allAdults = people.every((person) => person.age >= 18);      // boolean

// `some` on an empty array is false; `every` on an empty array is TRUE
// (vacuous truth). This surprises people, so it is worth remembering.
const emptySome = [].some(Boolean);
const emptyEvery = [].every(Boolean);

// ---------------------------------------------------------------------------
// 5. Mutating vs non-mutating - the distinction that causes real bugs
// ---------------------------------------------------------------------------

const scores = [3, 1, 2];

// sort and reverse MUTATE the array in place AND return it, so the original
// is changed even though it looks like a pure expression.
const sortedInPlace = [...scores].sort((a, b) => a - b);   // copy first!

// ES2023 added copying versions, which never touch the original.
const sortedCopy = scores.toSorted((a, b) => a - b);
const reversedCopy = scores.toReversed();
const replacedCopy = scores.with(0, 99);

// Default sort compares as STRINGS, which is the classic trap.
const naiveSort = [10, 9, 1].toSorted();            // [1, 10, 9]
const numericSort = [10, 9, 1].toSorted((a, b) => a - b);

// ---------------------------------------------------------------------------
// 6. Chaining, and when to stop chaining
// ---------------------------------------------------------------------------

// Readable, but walks the array three times.
const activeLondonNames = people
  .filter((person) => person.active)
  .filter((person) => person.city === "London")
  .map((person) => person.name);

// One pass. Prefer the chain for clarity; reach for this only when the array
// is large enough for the extra passes to matter, and say why in a comment.
const activeLondonNamesOnePass = people.reduce((acc, person) => {
  if (person.active && person.city === "London") acc.push(person.name);
  return acc;
}, []);

// flatMap = map then flatten one level. Useful when each item yields 0..n items.
const initials = people.flatMap((person) => person.name.split(" ").map((w) => w[0]));

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

console.log("names:", names);
console.log("summaries:", summaries);
console.log("active:", active.map((p) => p.name));
console.log("londoners:", londoners.map((p) => p.name));
console.log("totalAge:", totalAge, "average:", (totalAge / people.length).toFixed(1));
console.log("byCity:", byCity);

console.log("firstOver40:", firstOver40.name, "at index", indexOver40);
console.log("anyInactive:", anyInactive, "| allAdults:", allAdults);
console.log("[].some():", emptySome, "| [].every():", emptyEvery, "(vacuous truth)");

console.log("original scores after copying sort:", scores, "(unchanged)");
console.log("sortedInPlace:", sortedInPlace, "| sortedCopy:", sortedCopy);
console.log("reversedCopy:", reversedCopy, "| replacedCopy:", replacedCopy);
console.log("default sort is lexicographic:", naiveSort, "vs numeric:", numericSort);

console.log("chained:", activeLondonNames);
console.log("one pass:", activeLondonNamesOnePass);
console.log("initials:", initials);

/* Expected output:
names: [ 'Ada', 'Grace', 'Alan', 'Katherine' ]
active: [ 'Ada', 'Alan', 'Katherine' ]
londoners: [ 'Ada', 'Alan' ]
totalAge: 174 average: 43.5
byCity: { London: [ 'Ada', 'Alan' ], Arlington: [ 'Grace' ], Hampton: [ 'Katherine' ] }
firstOver40: Grace at index 1
anyInactive: true | allAdults: true
[].some(): false | [].every(): true (vacuous truth)
original scores after copying sort: [ 3, 1, 2 ] (unchanged)
default sort is lexicographic: [ 1, 10, 9 ] vs numeric: [ 1, 9, 10 ]
chained: [ 'Ada', 'Alan' ]
one pass: [ 'Ada', 'Alan' ]
*/
