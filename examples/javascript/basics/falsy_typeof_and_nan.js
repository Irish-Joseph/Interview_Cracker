// Topic: the seven falsy values, typeof's lies, and NaN !== NaN
//
// Concepts:
//   - exactly seven falsy values: false, 0, -0, 0n, "", null, undefined, NaN
//   - "0 is falsy" but "0.0 is the same 0"; empty objects/arrays are TRUTHY
//   - typeof null === "object" is a 30-year-old bug kept for compatibility
//   - typeof on an undeclared name is "undefined" (no ReferenceError)
//   - NaN is the only value not equal to itself; Number.isNaN and
//     Number.isFinite are the reliable guards (global isNaN COERCES!)
// Run: node falsy_typeof_nan.js

const values = [false, 0, -0, 0n, "", null, undefined, NaN,
                "0", "false", [], {}, 0.1, new Boolean(false)];

function label(v) {
  if (Object.is(v, -0)) return "-0";
  if (v === 0) return "0";
  if (Object.is(v, 0n)) return "0n";
  if (v === "") return '""  (empty string)';
  if (v === null) return "null";
  if (v === undefined) return "undefined";
  if (v === false) return "false";
  if (v instanceof Boolean) return "new Boolean(false)  <- truthy: it is an object";
  if (Array.isArray(v)) return "[]  <- truthy: an empty array is an object";
  if (typeof v === "object") return "{}  <- truthy: an empty object is an object";
  return String(v);
}

console.log("== truthy/falsy ==");
for (const v of values) {
  console.log(`${v ? "truthy" : "falsy "} : ${label(v)}`);
}

console.log("\n== typeof ==");
console.log("typeof null             :", typeof null);
console.log("typeof {}                :", typeof {});
console.log("typeof []                :", typeof []);
console.log("typeof 'hi'             :", typeof "hi");
console.log("typeof 42                :", typeof 42);
console.log("typeof Symbol()         :", typeof Symbol());
console.log("typeof function() {}     :", typeof (function () {}));
console.log("typeof undeclaredName   :", typeof undeclaredName, "(no error!)");
console.log("typeof (deleted)        :", typeof (void 0));

console.log("\n== NaN and the number guards ==");
const x = Number("not a number");
console.log("Number('not a number')  :", x);
console.log("x === x                 :", x === x, "(NaN is the only value that fails this)");
console.log("global isNaN(x)         :", isNaN(x), "(true)");
console.log("global isNaN('')        :", isNaN(""), "(false - it COERCES '' to 0, which is a number)");
console.log("Number.isNaN(x)         :", Number.isNaN(x));
console.log("Number.isNaN('')        :", Number.isNaN(""), "(no coercion)");
console.log("Number.isFinite(1e308)  :", Number.isFinite(1e308));
console.log("Number.isFinite(1e309)  :", Number.isFinite(1e309), "(that is Infinity)");
console.log("Number.isFinite('42')   :", Number.isFinite("42"), "(no coercion - interview favourite)");

console.log("\n== the practical rules ==");
console.log("check absence   : v === undefined (or v == null for null+undefined)");
console.log("check nullish   : v == null  (loose on purpose - the one sanctioned use)");
console.log("check empty str : s === ''   (not if (s) - '' and 0 both fail it)");
console.log("check real num  : Number.isFinite(v)");
