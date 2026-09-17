/**
 * Topic: TypeScript classes - access modifiers, abstract, and #private.
 *
 * TypeScript adds compile-time access control on top of JavaScript classes,
 * plus one runtime-enforced form (#private). Knowing which is which matters:
 * `private` is erased at compile time and can be bypassed; `#private` cannot.
 *
 * Concepts:
 * - public / private / protected, and readonly
 * - Parameter properties: declare and assign a field in the constructor signature
 * - abstract classes: shared behaviour plus a contract subclasses must fill
 * - implements vs extends
 * - Getters and setters, and static members
 * - TS `private` (compile-time) vs JS `#private` (runtime)
 *
 * Validate (Node 22+): node --experimental-transform-types classes_and_access_modifiers.ts
 *
 * Note the flag: --experimental-strip-types refuses this file, because
 * parameter properties emit real assignments rather than just deleting types.
 */

// ---------------------------------------------------------------------------
// 1. Access modifiers and parameter properties
// ---------------------------------------------------------------------------

class BankAccount {
  // A parameter property declares the field AND assigns it, in one place.
  // Without it you would write the field, the constructor parameter, and
  // `this.x = x` -- three lines saying the same thing.
  constructor(
    public readonly id: string,        // visible, but cannot be reassigned
    protected owner: string,           // visible to subclasses only
    private balance: number = 0,       // visible inside this class only
  ) {}

  deposit(amount: number): this {
    if (amount <= 0) throw new RangeError("deposit must be positive");
    this.balance += amount;
    return this;                       // `this` return type enables chaining
  }

  withdraw(amount: number): this {
    if (amount > this.balance) throw new RangeError("insufficient funds");
    this.balance -= amount;
    return this;
  }

  // A getter exposes derived state without exposing the field.
  get formattedBalance(): string {
    return `$${(this.balance / 100).toFixed(2)}`;
  }

  // Static members belong to the class, not to instances.
  static open(owner: string, openingDeposit: number): BankAccount {
    return new BankAccount(`acct_${++BankAccount.count}`, owner, openingDeposit);
  }

  private static count = 0;
}

// ---------------------------------------------------------------------------
// 2. Inheritance: protected is reachable, private is not
// ---------------------------------------------------------------------------

class SavingsAccount extends BankAccount {
  constructor(id: string, owner: string, private rate: number) {
    super(id, owner, 0);               // super() before any use of `this`
  }

  describe(): string {
    // `owner` is protected -> allowed here.
    // `balance` is private to BankAccount -> NOT allowed here, even though
    // this class extends it. Uncommenting the next line fails to compile:
    // return `${this.owner} has ${this.balance}`;
    return `${this.owner} earns ${(this.rate * 100).toFixed(1)}%`;
  }
}

// ---------------------------------------------------------------------------
// 3. abstract: shared behaviour + a contract
// ---------------------------------------------------------------------------

abstract class Shape {
  abstract area(): number;             // no body: subclasses MUST provide one

  // Concrete method shared by every subclass, written once.
  describe(): string {
    return `${this.constructor.name} with area ${this.area().toFixed(2)}`;
  }
}

class Circle extends Shape {
  constructor(private radius: number) { super(); }
  area(): number { return Math.PI * this.radius ** 2; }
}

class Rectangle extends Shape {
  constructor(private width: number, private height: number) { super(); }
  area(): number { return this.width * this.height; }
}

// ---------------------------------------------------------------------------
// 4. implements: a structural contract, with no inherited code
// ---------------------------------------------------------------------------

interface Serialisable {
  toJSON(): Record<string, unknown>;
}

class Settings implements Serialisable {
  // #private is enforced by the JavaScript RUNTIME, not just the compiler.
  #secret: string;

  constructor(public theme: string, secret: string) {
    this.#secret = secret;
  }

  toJSON(): Record<string, unknown> {
    return { theme: this.theme, secret: "***" };   // never leak the real value
  }

  revealLength(): number {
    return this.#secret.length;
  }
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

const account = BankAccount.open("Ada", 5_000);
account.deposit(2_500).withdraw(1_000);        // chaining, thanks to `this`

console.log("id:", account.id);
console.log("balance:", account.formattedBalance);

// account.balance      -> compile error: private
// account.owner        -> compile error: protected
// account.id = "nope"  -> compile error: readonly
console.log("second account gets its own id:", BankAccount.open("Grace", 0).id);

const savings = new SavingsAccount("acct_s1", "Katherine", 0.045);
console.log(savings.describe());

const shapes: Shape[] = [new Circle(2), new Rectangle(3, 4)];
for (const shape of shapes) {
  console.log(shape.describe());
}
// new Shape()  -> compile error: cannot instantiate an abstract class

const settings = new Settings("dark", "hunter2");
console.log("serialised:", JSON.stringify(settings));
console.log("secret length (via a method):", settings.revealLength());

// The runtime difference, demonstrated:
//   TS `private` is erased, so a cast reaches it at runtime.
//   JS `#private` is a real hard-private and throws.
console.log("TS private at runtime:", (account as any).balance, "(still readable!)");
try {
  (settings as any)["#secret"];
  console.log("JS #private is not even a normal property:",
              Object.keys(settings));
} catch {
  console.log("unreachable");
}

/* Expected output:
id: acct_1
balance: $65.00
second account gets its own id: acct_2
Katherine earns 4.5%
Circle with area 12.57
Rectangle with area 12.00
serialised: {"theme":"dark","secret":"***"}
secret length (via a method): 7
TS private at runtime: 6500 (still readable!)
JS #private is not even a normal property: [ 'theme' ]
*/
