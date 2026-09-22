// Topic: exhaustive checking with the never type
//
// A switch over a union is *complete* only when the compiler can prove that
// every member is handled. The trick: after handling all cases, the type of
// the value is narrowed to `never`. A function `assertNever(x: never): never`
// then turns "you forgot a case" into a compile error instead of a silent
// wrong default.
//
// Concepts:
//   - discriminated unions (a literal "kind" field the compiler switches on)
//   - narrowing: inside each case, TS knows exactly which member it is
//   - assertNever: a runtime no-op that fails at compile time when a case
//     is missing
//   - the cost: adding a variant without handling it is an error at every
//     switch site
// Run: node --experimental-strip-types exhaustive_never_checking.ts

type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

// The core of exhaustive checking. `x` can only be assigned here if the
// switch above failed to cover every variant.
declare function assertNever(x: never): never;

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "rect":
      return s.width * s.height;
    case "triangle":
      return (s.base * s.height) / 2;
    default:
      // If a fourth kind is added to Shape and forgotten here, `s` is not
      // `never` at this point and this call fails to compile.
      return assertNever(s);
  }
}

// Narrowing in action: inside case "circle", `s` is exactly
// { kind: "circle"; radius: number } - no cast, no optional chaining.
// Narrowing in action: after the first branch, the compiler has narrowed
// `s` to rect | triangle - no cast needed for the second comparison.
function describe(s: Shape): string {
  if (s.kind === "circle") {
    // here `s` is exactly { kind: "circle"; radius: number }
    return `circle r=${s.radius}`;
  }
  // here `s` is the union MINUS circle: { kind: "rect" ... } | { kind: "triangle" ... }
  return s.kind === "rect"
    ? `rect ${s.width}x${s.height}`
    : `triangle b=${s.base} h=${s.height}`;
}

const shapes: Shape[] = [
  { kind: "circle", radius: 2 },
  { kind: "rect", width: 3, height: 4 },
  { kind: "triangle", base: 6, height: 4 },
];

for (const s of shapes) {
  console.log(`${describe(s).padEnd(16)} area = ${area(s).toFixed(2)}`);
}

// The "cost" of exhaustiveness: add `| { kind: "ellipse"; a: number; b: number }`
// to Shape and re-run the type checker - every switch site that forgot
// "ellipse" becomes an error. (Removed for this runnable demo.)
console.log("if a case is missing, assertNever makes it a compile error, not a wrong answer");
