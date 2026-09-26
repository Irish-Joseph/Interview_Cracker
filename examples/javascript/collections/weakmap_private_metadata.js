/**
 * Topic: WeakMap for object-keyed private metadata.
 * Concepts: object-only keys, non-enumerable state, garbage-collection friendliness.
 * Run: node examples/javascript/collections/weakmap_private_metadata.js
 * Expected output is asserted below.
 */

const metadata = new WeakMap();

class Session {
  constructor(user) {
    metadata.set(this, { user, touches: 0 });
  }

  touch() {
    metadata.get(this).touches += 1;
  }

  summary() {
    const { user, touches } = metadata.get(this);
    return `${user}:${touches}`;
  }
}

const session = new Session("ada");
session.touch();
session.touch();

if (session.summary() !== "ada:2") throw new Error("wrong metadata");
if (Object.keys(session).length !== 0) throw new Error("metadata leaked");
if (JSON.stringify(session) !== "{}") throw new Error("metadata serialized");

console.log(session.summary());
console.log("enumerable keys:", Object.keys(session).length);

// Unlike Map, WeakMap is intentionally not iterable. Once `session` becomes
// unreachable, this metadata does not keep it alive merely to preserve a key.
