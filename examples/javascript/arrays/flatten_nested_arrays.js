/**
 * Topic: Flatten an arbitrarily nested array.
 *
 * Concepts:
 * - Recursion with a base case
 * - Array.isArray to distinguish arrays from plain values
 * - Accumulator pattern (avoiding the built-in flat())
 *
 * Example:
 * Input:  [1, [2, [3, 4]], 5, [[6]]]
 * Output: [1, 2, 3, 4, 5, 6]
 *
 * Time Complexity: O(n)  (each element visited once)
 * Space Complexity: O(n) (result array + recursion stack)
 */

function flatten(nested) {
  const result = [];

  for (const item of nested) {
    if (Array.isArray(item)) {
      // Recurse into the nested array and append its contents.
      result.push(...flatten(item));
    } else {
      result.push(item);
    }
  }

  return result;
}

// --- Demo ---------------------------------------------------------------

const cases = [
  [1, [2, [3, 4]], 5, [[6]]],
  ['a', ['b', ['c']]],
  [1, 2, 3],                 // already flat -> unchanged
  [],                          // empty -> empty
];

for (const input of cases) {
  console.log(JSON.stringify(input), '->', JSON.stringify(flatten(input)));
}

/**
 * A depth-limited variation: stop flattening after `depth` levels.
 * This mirrors the real Array.prototype.flat(depth) semantics.
 */
function flattenDepth(nested, depth) {
  if (depth === 0) {
    return nested; // cannot flatten further
  }

  const result = [];
  for (const item of nested) {
    if (Array.isArray(item)) {
      result.push(...flattenDepth(item, depth - 1));
    } else {
      result.push(item);
    }
  }
  return result;
}

const deep = [1, [2, [3, [4, [5]]]]];
console.log('depth=1:', JSON.stringify(flattenDepth(deep, 1)));
// -> [1, 2, [3, [4, [5]]]]
console.log('depth=2:', JSON.stringify(flattenDepth(deep, 2)));
// -> [1, 2, 3, [4, [5]]]
console.log('depth=Infinity:', JSON.stringify(flattenDepth(deep, Infinity)));
// -> [1, 2, 3, 4, 5]
