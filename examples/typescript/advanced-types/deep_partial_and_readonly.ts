/**
 * Topic: DeepPartial and DeepReadonly with recursive conditional types.
 *
 * Concepts:
 * - Built-in Partial<T> only goes ONE level deep
 * - Recursion in types: a conditional type applied to T's own properties
 * - Mapped types + key remapping is not needed here — plain mapped types recurse
 * - `unknown` guards against recursing into non-objects
 *
 * Example output:
 *   partial accepted:  { name: "api", limits: { cpu: 2 } }
 *   readonly deep check: the assignment below is a COMPILE error:
 *     settings.limits.cpu = 8   // Error: readonly
 *   runtime copy is independent: 5
 */

// Built-in Partial makes every top-level property optional —
// but nested objects stay required:
//   Partial<{ limits: { cpu: number; mem: number } }>
//   is { limits?: { cpu: number; mem: number } } — limits.cpu is still required!

// DeepPartial recurses into object values. Arrays are usually left
// alone (partially filling a list of items rarely makes sense).
type DeepPartial<T> = T extends readonly unknown[]
  ? T                                   // arrays: keep as-is
  : T extends object
    ? { [K in keyof T]?: DeepPartial<T[K]> }  // objects: recurse
    : T;                                // primitives: keep as-is

// DeepReadonly mirrors it: every nested property becomes readonly.
type DeepReadonly<T> = T extends readonly unknown[]
  ? readonly DeepReadonly<T[number]>[]
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;

interface Limits {
  cpu: number;
  mem: number;
}

interface ServiceConfig {
  name: string;
  limits: Limits;
  tags: string[];
}

// --- DeepPartial: fill in a config incrementally, any depth. ---
const partial: DeepPartial<ServiceConfig> = {
  name: "api",
  limits: { cpu: 2 },  // `mem` is optional now — this is the point
};
// partial.limits.cpu === 2, partial.limits.mem === undefined
console.log("partial accepted:  { name: \"api\", limits: { cpu: 2 } }");

// Type-level self-test: these lines COMPILE (proving recursion works):
const alsoOk: DeepPartial<Limits> = { cpu: 1 };      // mem optional
const shallowDiffer: DeepPartial<ServiceConfig> = {
  limits: { mem: 512 },                               // cpu optional
};
// And this would NOT compile — DeepPartial can't create new keys:
//   const bad: DeepPartial<Limits> = { gpus: 1 };    // Error: 'gpus' doesn't exist

// --- DeepReadonly: freeze an entire tree, not just the top level. ---
const settings: DeepReadonly<ServiceConfig> = {
  name: "worker",
  limits: { cpu: 4, mem: 1024 },
  tags: ["prod", "eu"],
};
// settings.limits.cpu = 8;      // COMPILE ERROR: 'cpu' is readonly
// settings.name = "other";      // COMPILE ERROR: 'name' is readonly
// settings.tags[0] = "staging"; // COMPILE ERROR: tuple element readonly

// Type-level self-test: reads still work and are fully typed:
const cpu: number = settings.limits.cpu;
const tag: string = settings.tags[0];

// Runtime note: "readonly" is enforced at COMPILE time only. A plain
// JS mutation through `any` would still happen at runtime — if you need
// a runtime freeze, use Object.freeze (shallow) recursively.
const mutableClone = { ...settings, limits: { ...settings.limits } };
mutableClone.limits.cpu = 5;
console.log("runtime copy is independent:", mutableClone.limits.cpu);
