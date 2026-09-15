/**
 * Topic: A minimal event emitter with on, once, off and emit.
 *
 * Concepts:
 * - Event-driven programming: decoupling publishers from subscribers
 * - Storing listeners in a Map keyed by event name
 * - "once" semantics: a listener that removes itself after one call
 * - Removing listeners (off) by reference
 * - Emitting events with payloads
 *
 * Example output:
 *   ready: user 1
 *   ready: user 1      <- the once() listener fires only this time
 *   ready: user 2
 *   (no ready output for user 3: all ready listeners were removed)
 *   done in 0ms
 */

class EventEmitter {
  constructor() {
    this.listeners = new Map(); // event name -> array of listener functions
  }

  on(event, listener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(listener);
    return this; // allows chaining: emitter.on("a", f).on("b", g)
  }

  once(event, listener) {
    // Wrap the listener so it removes itself after its first call.
    const wrapper = (...args) => {
      this.off(event, wrapper);
      listener(...args);
    };
    // Remember the original function so off(event, listener) also works.
    wrapper.listener = listener;
    return this.on(event, wrapper);
  }

  off(event, listener) {
    const list = this.listeners.get(event);
    if (!list) return this;

    const next = list.filter(
      (fn) => fn !== listener && fn.listener !== listener
    );
    if (next.length === 0) {
      this.listeners.delete(event);
    } else {
      this.listeners.set(event, next);
    }
    return this;
  }

  emit(event, ...args) {
    const list = this.listeners.get(event);
    if (!list) return false;

    // Copy first: a listener may add or remove listeners mid-emit.
    for (const fn of [...list]) {
      fn(...args);
    }
    return true;
  }
}

const bus = new EventEmitter();

const onReady = (user) => console.log(`ready: user ${user}`);
bus.on("ready", onReady);
bus.once("ready", (user) => console.log(`ready: user ${user}      <- once`));

bus.on("done", (ms) => console.log(`done in ${ms}ms`));

bus.emit("ready", 1);
bus.emit("ready", 2);

// Remove the regular listener, then emit again:
bus.off("ready", onReady);
bus.emit("ready", 3);

// No listeners for "cancel" -> emit returns false:
console.log("cancel handled?", bus.emit("cancel"));

bus.emit("done", 0);
