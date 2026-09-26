/**
 * Topic: User-defined type predicates that validate unknown input.
 * Concepts: `value is T`, unknown-first parsing, Array.every narrowing.
 * Run: node --experimental-strip-types examples/typescript/generics/user_defined_type_predicates.ts
 */

interface User {
  id: number;
  name: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isUser(value: unknown): value is User {
  return (
    isRecord(value) &&
    typeof value.id === "number" &&
    Number.isInteger(value.id) &&
    typeof value.name === "string"
  );
}

function parseUsers(json: string): User[] {
  const value: unknown = JSON.parse(json);
  if (!Array.isArray(value) || !value.every(isUser)) {
    throw new Error("invalid user payload");
  }
  return value;
}

const users = parseUsers('[{"id":1,"name":"Ada"}]');
console.log(users[0].name.toUpperCase());

try {
  parseUsers('[{"id":"1","name":"Ada"}]');
  throw new Error("invalid payload was accepted");
} catch (error) {
  if (!(error instanceof Error) || error.message !== "invalid user payload") throw error;
  console.log("invalid payload rejected");
}
