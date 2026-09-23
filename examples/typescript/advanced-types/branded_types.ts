/**
 * Topic: Branded types for values with identical runtime shapes.
 *
 * Concepts: unique-symbol brands, validated constructors, zero runtime cost.
 * Run: node --experimental-strip-types examples/typescript/advanced-types/branded_types.ts
 * Expected output: loading user usr_42; sending 250 cents
 */

declare const userIdBrand: unique symbol;
declare const centsBrand: unique symbol;

type UserId = string & { readonly [userIdBrand]: "UserId" };
type Cents = number & { readonly [centsBrand]: "Cents" };

function userId(raw: string): UserId {
  if (!/^usr_[0-9]+$/.test(raw)) {
    throw new Error(`invalid user id: ${raw}`);
  }
  return raw as UserId;
}

function cents(raw: number): Cents {
  if (!Number.isSafeInteger(raw) || raw < 0) {
    throw new Error("cents must be a non-negative safe integer");
  }
  return raw as Cents;
}

function loadUser(id: UserId): void {
  console.log(`loading user ${id}`);
}

function sendPayment(amount: Cents): void {
  console.log(`sending ${amount} cents`);
}

const id = userId("usr_42");
const price = cents(250);
loadUser(id);
sendPayment(price);

// These fail at compile time, even though both underlying values are simple:
// loadUser("usr_42");
// sendPayment(id);
