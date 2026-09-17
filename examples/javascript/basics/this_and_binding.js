/**
 * Topic: `this` — how JavaScript decides what it points to.
 *
 * Concepts:
 * - `this` is set by the CALL SITE, not by where a function was written
 * - The four binding rules: default, implicit, explicit, `new`
 * - The classic "lost `this`" bug when a method is passed as a callback
 * - call / apply / bind
 * - Arrow functions capture `this` from the enclosing scope
 *
 * The one question that answers almost every `this` puzzle:
 * "What is to the LEFT of the dot at the moment the function is CALLED?"
 */

'use strict';

// --- Rule 1: implicit binding — the object left of the dot ----------------

const counter = {
  label: 'clicks',
  count: 0,
  describe() {
    return `${this.label}: ${this.count}`;
  },
};

console.log('1. implicit binding:', counter.describe()); // "clicks: 0"

// --- Rule 2: default binding — no dot, no object --------------------------

// Pull the method off the object and `this` is gone. In strict mode it is
// `undefined` (in sloppy mode it would silently become globalThis).
const describe = counter.describe;

try {
  describe();
} catch (err) {
  console.log('2. detached method threw:', err.constructor.name);
}

// This is THE most common `this` bug — it shows up whenever a method is
// handed to something else to call later:
//
//   setTimeout(counter.describe, 100);      // called with no receiver
//   button.addEventListener('click', counter.describe);
//   [1, 2].map(counter.describe);

// --- Rule 3: explicit binding — call, apply, bind -------------------------

const other = { label: 'downloads', count: 42 };

// call: pass arguments one by one.  apply: pass them as an array.
console.log('3. call: ', counter.describe.call(other));
console.log('3. apply:', counter.describe.apply(other, []));

// bind returns a NEW function permanently attached to that receiver.
const describeOther = counter.describe.bind(other);
console.log('3. bind: ', describeOther());

// bind is the fix for the detached-method bug:
const later = counter.describe.bind(counter);
setTimeout(() => console.log('3. bind survives setTimeout:', later()), 0);

// bind also pre-fills leading arguments (partial application):
function tag(level, message) {
  return `[${level}] ${this.label}: ${message}`;
}
const warn = tag.bind(counter, 'WARN');
console.log('3. bind + preset arg:', warn('disk almost full'));

// --- Rule 4: `new` binding — `this` is the fresh object -------------------

function Timer(name) {
  this.name = name;
  this.ticks = 0;
}
Timer.prototype.tick = function tick() {
  this.ticks += 1;
  return `${this.name} -> ${this.ticks}`;
};

const timer = new Timer('build');
console.log('4. new binding:', timer.tick(), timer.tick());

// --- Arrow functions: no `this` of their own ------------------------------

// A regular function callback gets its own `this` (undefined here), so the
// counting below would crash. An arrow closes over the surrounding `this`.
const tracker = {
  label: 'errors',
  entries: ['a', 'b', 'c'],

  brokenReport() {
    // Uncommenting this throws: inner `this` is not `tracker`.
    // return this.entries.map(function (e) { return `${this.label}:${e}`; });
    return null;
  },

  workingReport() {
    return this.entries.map((e) => `${this.label}:${e}`); // arrow keeps `this`
  },
};

console.log('5. arrow keeps `this`:', tracker.workingReport());

// Because arrows have no own `this`, call/apply/bind cannot retarget them:
const arrowDescribe = () => `arrow sees label: ${typeof this}`;
console.log('5. arrow ignores bind:', arrowDescribe.call(other));

// Corollary: never write an object METHOD as an arrow at the top level —
// it captures the module/global scope, not the object.
const wrong = {
  label: 'nope',
  describe: () => `label is ${this && this.label}`, // not the object
};
console.log('5. arrow as method:', wrong.describe()); // "label is undefined"

// --- Classes: methods are not auto-bound ----------------------------------

class Uploader {
  constructor(name) {
    this.name = name;
    // Bind in the constructor when the method will be used as a callback:
    this.boundStatus = this.status.bind(this);
    // Or use a class field holding an arrow: status = () => ...
  }

  status() {
    return `${this.name} ready`;
  }
}

const uploader = new Uploader('avatar');
const detached = uploader.status;
const bound = uploader.boundStatus;

console.log('6. bound field works:', bound());
try {
  detached(); // class bodies are always strict -> `this` is undefined
} catch (err) {
  console.log('6. detached class method threw:', err.constructor.name);
}

/**
 * Precedence when several rules could apply:
 *
 *   new  >  bind/call/apply  >  object.method()  >  plain call
 *
 * Summary:
 * - obj.fn()        -> `this` is obj
 * - fn()            -> undefined (strict) / globalThis (sloppy)
 * - fn.call(o)      -> o
 * - new Fn()        -> the new object
 * - () => {}        -> whatever `this` was where the arrow was written
 */
