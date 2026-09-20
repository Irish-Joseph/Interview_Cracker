/**
 * Topic: String methods — padding, case, locale-aware comparison, template literals.
 *
 * Concepts:
 * - padStart / padEnd for fixed-width formatting
 * - Case conversion: toUpperCase, toLowerCase, toLocaleLowerCase
 * - localeCompare for human (locale-aware) ordering vs < / > on strings
 * - Template literals with expressions and tagged templates
 * - includes / startsWith / endsWith / repeat
 *
 * Example output:
 *   id    name            score
 *   00007 Ada Lovelace    91
 *   00012 Grace Hopper    88
 *   code-unit order:  Anders, Björn, anna
 *   locale order:     [ Anders, anna, Björn ]
 *   shout: WORLD!
 *   repeated: ---***---
 *   is a log? true
 */

const rows = [
  { id: 7, name: "Ada Lovelace", score: 91 },
  { id: 12, name: "Grace Hopper", score: 88 },
];

// padStart keeps numbers aligned without printf-style formatting.
console.log("id    name            score");
for (const r of rows) {
  const id = String(r.id).padStart(5, "0");
  const name = r.name.padEnd(15).trimEnd();
  console.log(`${id}  ${name}   ${r.score}`);
}

// < / > on strings compares UTF-16 code units: all uppercase sorts
// before all lowercase. localeCompare knows locale rules (case is a
// tie-breaker, accents fold, etc.) — what humans expect in a list.
const names = ["anna", "Anders", "Björn"];
console.log("code-unit order: ", [...names].sort().join(", "));
console.log("locale order:    [ " + [...names].sort((a, b) => a.localeCompare(b, "de")).join(", ") + " ]");

// Template literals: expressions inline, multi-line without \n.
const who = "world";
console.log(`shout: ${who.toUpperCase()}!`);   // shout: WORLD!
console.log("repeated:", "-".repeat(3) + "*".repeat(3) + "-".repeat(3));

// Membership tests.
const path = "/var/log/app/server.log";
console.log("is a log?", path.endsWith(".log") && path.includes("/log/"));
