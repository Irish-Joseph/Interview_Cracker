/**
 * Topic: Destructuring — objects, arrays, defaults and rest.
 *
 * Concepts:
 * - Object destructuring with renaming
 * - Default values for missing properties
 * - Nested destructuring
 * - Array destructuring (including skipping elements)
 * - Rest pattern to collect "everything else"
 *
 * Destructuring pulls values out of objects/arrays into variables
 * in a single statement — less boilerplate, and it makes the
 * *shape* of expected data visible at the call site.
 *
 * Validate: node destructuring_patterns.js
 */

// --- 1. Basic object destructuring + renaming ----------------------------

const user = { name: "Alice", role: "admin", age: 30 };

const { name, role: userRole } = user;   // rename to avoid shadowing
console.log(`${name} is a ${userRole}`);
// -> Alice is a admin

// --- 2. Default values -----------------------------------------------------

// Defaults kick in only for `undefined` values (not for 0 or "").
function makeConfig(options = {}) {
  const {
    host = "localhost",
    port = 3000,
    secure = false,
    timeout = options.timeout ?? 5000, // ?? keeps 0 valid
  } = options;
  return { host, port, secure, timeout };
}

console.log("defaults:     ", makeConfig());
// -> { host: 'localhost', port: 3000, secure: false, timeout: 5000 }
console.log("overridden:   ", makeConfig({ port: 8080, secure: true }));
// -> { host: 'localhost', port: 8080, secure: true, timeout: 5000 }

// --- 3. Nested destructuring ----------------------------------------------

const server = {
  name: "web-1",
  network: { ip: "10.0.0.5", port: 443 },
  owner: { team: "platform", oncall: "Dan" },
};

const {
  network: { ip, port },   // drill straight into the nested object
  owner: { oncall },
} = server;

console.log(`${ip}:${port} oncall=${oncall}`);
// -> 10.0.0.5:443 oncall=Dan

// Guard against a missing nested level with a default intermediate:
const bare = { network: {} };
const { network: { ip: ip2 = "0.0.0.0" } = {} } = bare;
console.log("missing nested default:", ip2);
// -> 0.0.0.0

// --- 4. Array destructuring ------------------------------------------------

const [first, second, ...rest] = [10, 20, 30, 40, 50];
console.log(`first=${first} second=${second} rest=${rest}`);
// -> first=10 second=20 rest=30,40,50

const [, , third] = [10, 20, 30]; // skip the first two elements
console.log("third (skipping two):", third);
// -> 30

// Swap without a temp variable:
let a = 1, b = 2;
[a, b] = [b, a];
console.log(`after swap: a=${a} b=${b}`);
// -> after swap: a=2 b=1

// --- 5. Rest in function parameters ----------------------------------------

function summarize(first, second, ...others) {
  return `first=${first}, second=${second}, ${others.length} more`;
}

console.log(summarize("a", "b", "c", "d", "e"));
// -> first=a, second=b, 3 more

// Rest for objects: pull out what you need, keep the remainder.
const settings = { debug: true, theme: "dark", lang: "en" };
const { theme, ...remaining } = settings;
console.log(`theme=${theme} remaining=${JSON.stringify(remaining)}`);
// -> theme=dark remaining={"debug":true,"lang":"en"}
