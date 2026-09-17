/**
 * Topic: Group an array of objects by a property.
 *
 * Concepts:
 * - reduce() as a general "build a new structure" tool
 * - Using object keys as buckets
 * - Function-valued property selectors (string key or accessor)
 * - Optional chaining and ?? for safe defaults
 *
 * Grouping is one of the most common data-shaping tasks:
 * turn a flat list into { key: [items...] }.
 *
 * Example:
 * Input:  [{name, dept}, {name, dept}, ...]
 * Output: { engineering: [...], sales: [...] }
 *
 * Time Complexity: O(n)
 * Space Complexity: O(n)
 *
 * Validate: node group_objects_by_property.js
 */

/**
 * Groups `items` by the value of `getKey(item)`.
 *
 * @param {Array} items
 * @param {(item: any) => PropertyKey} getKey - selector function
 * @returns {Object} map from key -> array of matching items
 */
function groupBy(items, getKey) {
  return items.reduce((groups, item) => {
    const key = getKey(item);

    // Create the bucket on first use; push into it afterwards.
    (groups[key] ??= []).push(item);

    return groups;
  }, {});
}

// A convenience wrapper for the common "group by property name" case.
function groupByProperty(items, property) {
  return groupBy(items, (item) => item[property]);
}

// --- Demo -----------------------------------------------------------------

const employees = [
  { name: "Alice", dept: "engineering", level: 4 },
  { name: "Bob",   dept: "sales",       level: 2 },
  { name: "Carol", dept: "engineering", level: 2 },
  { name: "Dan",   dept: "sales",       level: 4 },
  { name: "Eve",   dept: "engineering", level: 3 },
];

// 1. Group by a property name.
const byDept = groupByProperty(employees, "dept");
console.log("by department:");
for (const [dept, people] of Object.entries(byDept)) {
  console.log(`  ${dept}: ${people.map((p) => p.name).join(", ")}`);
}

// 2. Group by a computed value (level bucket: "junior" / "senior").
const byLevel = groupBy(employees, (e) => (e.level >= 4 ? "senior" : "junior"));
console.log("\nby level bucket:");
for (const [bucket, people] of Object.entries(byLevel)) {
  console.log(`  ${bucket}: ${people.length}`);
}

// 3. Group numbers by parity — items need not be objects.
const numbers = [1, 2, 3, 4, 5, 6];
const byParity = groupBy(numbers, (n) => (n % 2 === 0 ? "even" : "odd"));
console.log("\nnumbers by parity:", JSON.stringify(byParity));

// 4. Counting is a one-line extension: map each bucket to its length.
const counts = Object.fromEntries(
  Object.entries(byDept).map(([dept, people]) => [dept, people.length])
);
console.log("department headcount:", JSON.stringify(counts));

// Expected output:
// by department:
//   engineering: Alice, Carol, Eve
//   sales: Bob, Dan
//
// by level bucket:
//   senior: 2
//   junior: 3
//
// numbers by parity: {"odd":[1,3,5],"even":[2,4,6]}
// department headcount: {"engineering":3,"sales":2}
