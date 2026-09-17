/**
 * Topic: Narrowing union types with type guards.
 *
 * Concepts:
 * - Discriminated unions (a literal "kind" field)
 * - Type narrowing via `switch` / `if` on the discriminant
 * - Custom type guards (`x is T` predicates)
 * - Exhaustiveness checking with `never`
 *
 * This is the standard, safe way to model "a shape that can be one of
 * several things" in TypeScript — instead of using `any` or optional
 * fields that might all be undefined.
 *
 * Validate (Node 22+): node --experimental-strip-types shape_operations.ts
 */

// --- The union: each variant has a unique `kind` literal ----------------
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

/**
 * Computes area from a Shape.
 *
 * The `switch` on `shape.kind` narrows the type in each branch:
 * inside `case "circle"` the compiler knows `shape` has `radius`.
 */
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return (shape.base * shape.height) / 2;

    // Exhaustiveness check: if a new variant is added to `Shape` but
    // not handled here, `shape` is `never` and this line fails to
    // compile — a compile-time reminder, not a runtime bug.
    default: {
      const _exhaustive: never = shape;
      throw new Error(`Unknown shape: ${JSON.stringify(_exhaustive)}`);
    }
  }
}

/**
 * A custom type guard: a function returning `x is T` tells the
 * compiler how to narrow a value when the guard returns true.
 *
 * Useful when the discriminant is buried or the check is complex.
 */
function isRectangle(maybe: Shape): maybe is Extract<Shape, { kind: "rectangle" }> {
  return maybe.kind === "rectangle" && maybe.width > 0 && maybe.height > 0;
}

/** Demonstrates narrowing with a custom guard outside a switch. */
function describe(shape: Shape): string {
  if (isRectangle(shape)) {
    // Here `shape` is narrowed to the rectangle variant.
    return `rectangle ${shape.width}x${shape.height}`;
  }
  return `a ${shape.kind}`;
}

// --- Demo ----------------------------------------------------------------

const shapes: Shape[] = [
  { kind: "circle", radius: 2 },
  { kind: "rectangle", width: 4, height: 5 },
  { kind: "triangle", base: 6, height: 3 },
];

for (const shape of shapes) {
  // Both calls work on the raw union — no casts, no `any`.
  console.log(
    `${describe(shape).padEnd(28)} area=${area(shape).toFixed(2)}`
  );
}

// Expected output:
// a circle                    area=12.57
// rectangle 4x5               area=20.00
// a triangle                  area=9.00
