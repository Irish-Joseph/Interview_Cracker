/**
 * Topic: interface vs type — when to use which in TypeScript.
 *
 * Concepts:
 * - Object shapes: interface and type aliases are near-identical here
 * - Declaration merging (interfaces only)
 * - Extending: interface extends vs intersection types (&)
 * - Implementing interfaces with classes
 * - Practical decision rules
 *
 * For plain object shapes, both work. The differences show up in
 * specific features — this file demonstrates each one concretely.
 *
 * Validate (Node 22+): node --experimental-strip-types interface_vs_type.ts
 */

// --- 1. Defining shapes: both spellings work -------------------------------

interface User {
  id: number;
  name: string;
  email: string;
}

type Product = {
  sku: string;
  price: number;
  inStock: boolean;
};

const user: User = { id: 1, name: "Alice", email: "a@x.y" };
const product: Product = { sku: "AB-1", price: 9.99, inStock: true };

console.log(`${user.name} wants ${product.sku}`);

// --- 2. Declaration merging: interfaces MERGE, types do not ----------------
//
// Declaring the same interface twice ADDS members (used heavily for
// module augmentation). A duplicate type alias is a compile error.

interface Config {
  host: string;
}

interface Config {
  port: number; // merged into the same interface
}

const cfg: Config = { host: "localhost", port: 8080 };
console.log(`config: ${cfg.host}:${cfg.port}`);

// (This would NOT compile: `type Config2 = {...}; type Config2 = {...}`)

// --- 3. Extending shapes -----------------------------------------------------

// interface extends interface:
interface Admin extends User {
  role: "admin" | "superadmin";
}

const admin: Admin = { id: 2, name: "Bob", email: "b@x.y", role: "admin" };
console.log(`admin: ${admin.name} (${admin.role})`);

// type extends via intersection (&):
type Owned = { ownerId: number };
type SharedProduct = Product & Owned;

const shared: SharedProduct = {
  sku: "CD-2",
  price: 19.99,
  inStock: false,
  ownerId: admin.id,
};
console.log(`shared product ${shared.sku} owned by user ${shared.ownerId}`);

// --- 4. Classes implement interfaces -----------------------------------------

interface Serializable {
  serialize(): string;
}

interface Validatable {
  validate(): boolean;
}

class Account implements Serializable, Validatable {
  private balance: number;

  constructor(balance: number) {
    this.balance = balance;
  }

  serialize(): string {
    return `Account(balance=${this.balance})`;
  }

  validate(): boolean {
    return this.balance >= 0;
  }
}

const account = new Account(120);
console.log(account.serialize(), "valid:", account.validate());
// -> Account(balance=120) valid: true

// --- 5. Decision rules (summary) ---------------------------------------------
//
// Use an `interface` when:
//   - describing an object's public API / contract
//   - a class will implement it
//   - you want declaration merging (libraries, plugins)
//
// Use a `type` when:
//   - unions / intersections / tuples / mapped types are involved
//     (e.g. `type Status = "ok" | "err"`, `type Pair = [string, number]`)
//   - you want a simple alias for something computed
//
// For plain object shapes, follow your codebase's existing style.

type Status = "ok" | "error";        // union: type alias territory
type Pair = [label: string, value: number]; // tuple: type alias territory

const status: Status = "ok";
const pair: Pair = ["version", 42];
console.log(`${status}: ${pair[0]} = ${pair[1]}`);
// -> ok: version = 42
