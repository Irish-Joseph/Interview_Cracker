// Topic: template literal types - types built by interpolation, like strings
//
// A template literal type takes existing types and "interpolates" them into a
// string shape: `${Method}/${Path}` becomes the union of every combination.
// Combined with distributive conditional types and `infer`, this is how
// libraries type things like API routes and event names so a typo is a
// compile error instead of a runtime 404.
//
// Concepts:
//   - basic interpolation: `${A} ${B}` over unions = cartesian product
//   - distribution: a conditional over a union applies to EACH member
//   - infer in a string position: split "GET /users/:id" into its pieces
//   - the payoff: a request(route, params) whose parameters depend on which
//     route you named - and a few @ts-expect-error lines proving the check
//
// Run: node --experimental-strip-types template_literal_types.ts

type Method = "GET" | "POST" | "DELETE";
type Users = "/users" | "/users/:id" | "/reports";

// 1. Interpolation: every method x every path (9 members).
type Route = `${Method} ${Users}`;
const all: Route[] = ["GET /users", "POST /users", "DELETE /reports"];

// 2. Distribution + infer: split "GET /users/:id" into its pieces.
type Split<R extends string> = R extends `${infer M} ${infer P}`
  ? { method: M; path: P }
  : never;

// 3. The part after the first slash.
type AfterSlash<T extends string> = T extends `${string}/${infer Rest}` ? Rest : T;

// 4. Parameters that depend on the route:
//    routes containing ":id" need an id; GET routes take no body;
//    the rest take a body.
type Params<R extends Route> =
  R extends `${string} /users/:id`
    ? { id: string }
    : R extends `GET ${string}`
      ? Record<string, never>
      : { body: object };

// 5. A typed client: the signature is checked per route.
function request<R extends Route>(route: R, params: Params<R>): { route: R } {
  return { route };
}

// 6. Compile-time assertions (verified by the type checker, not at runtime):
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2
  ? true
  : false;
type Expect<T extends true> = T;
type _checkSplit = Expect<Equal<Split<"GET /users/:id">, { method: "GET"; path: "/users/:id" }>>;
type _checkAfterSlash = Expect<Equal<AfterSlash<"/users/:id">, "users/:id">>;
type _checkParams = Expect<Equal<Params<"DELETE /users/:id">, { id: string }>>;

function main(): void {
  const r1 = request("GET /users", {});
  const r2 = request("GET /users/:id", { id: "42" });
  const r3 = request("POST /users", { body: { name: "ann" } });
  console.log("valid routes accepted:");
  console.log("  " + [r1.route, r2.route, r3.route].join(", "));
  console.log("plus: " + all.length + " more in the Route union (9 total)");

  // The point of the exercise: these three lines each fail to COMPILE.
  // @ts-expect-error - "PUT" is not in Method
  const bad: Route = "PUT /users";
  void bad;
  // @ts-expect-error - GET /users/:id requires { id }
  request("GET /users/:id", {});
  // @ts-expect-error - GET routes take no body
  request("GET /users", { body: {} });
}

main();
