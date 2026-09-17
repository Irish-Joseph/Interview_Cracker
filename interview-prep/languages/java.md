# Java Interview Questions

---

### 🟢 Q. What is the difference between JDK, JRE and JVM?

**Answer.** **JVM** executes bytecode and is the thing that makes Java portable —
one `.class` file runs anywhere a JVM exists. **JRE** is the JVM plus the standard
class libraries: enough to *run* Java. **JDK** is the JRE plus development tools
(`javac`, `jdb`, `jar`): enough to *build* Java.

"Write once, run anywhere" is a property of bytecode plus a per-platform JVM, not
of the source language.

---

### 🟢 Q. Primitive vs reference types?

**Answer.** Primitives (`int`, `double`, `boolean`, `char`, …) hold values
directly, live on the stack when local, cannot be null, and have no methods.
Reference types hold a pointer to a heap object, can be null, and carry methods.

The consequence that produces bugs:

```java
String a = new String("hi");
String b = new String("hi");
a == b        // false — different objects
a.equals(b)   // true  — same characters
```

`==` compares references for objects, values for primitives. **Always use
`.equals()` for objects.**

Autoboxing makes this worse:

```java
Integer x = 127, y = 127;
x == y;                 // true  — cached (-128..127)
Integer p = 128, q = 128;
p == q;                 // false — outside the cache
```

Same code, different answer depending on the value. Never compare boxed types
with `==`.

---

### 🔴 Q. Explain the equals/hashCode contract.

**Answer.** If `a.equals(b)` then `a.hashCode() == b.hashCode()`, **always**. The
reverse is not required — equal hash codes with unequal objects is just a
collision.

Override one and you must override the other. Break it and hash-based collections
fail silently:

```java
Map<Point, String> map = new HashMap<>();
map.put(new Point(1, 2), "origin-ish");
map.get(new Point(1, 2));   // null, if hashCode() was not overridden
```

The lookup hashes to a different bucket and never finds the entry.

The second half of the contract: **a key's hash must not change while it is in a
collection.** Mutating a field used by `hashCode` strands the entry — present but
unreachable, and `remove()` will not find it either. Prefer immutable keys;
`record` types give you correct `equals`/`hashCode` for free.

---

### 🟡 Q. Compare the collections.

**Answer.**

| Interface | Implementation | Ordering | Notes |
|---|---|---|---|
| `List` | `ArrayList` | insertion | O(1) index, O(n) middle insert. **The default.** |
| | `LinkedList` | insertion | O(1) ends, poor locality — rarely the right choice |
| `Set` | `HashSet` | none | O(1) average |
| | `LinkedHashSet` | insertion | O(1), remembers order |
| | `TreeSet` | **sorted** | O(log n), needs `Comparable`/`Comparator` |
| `Map` | `HashMap` | none | O(1) average; chains become trees past 8 entries |
| | `LinkedHashMap` | insertion or access | access-order mode gives you an LRU cache |
| | `TreeMap` | **sorted** | O(log n), range queries |

`ArrayList` unless you need ordering or sorting. `LinkedList` is almost never the
answer despite what its Big-O table suggests — cache locality wins.

---

### 🟡 Q. Checked vs unchecked exceptions?

**Answer.** **Checked** (extend `Exception`) must be declared or caught — the
compiler enforces it. Intended for recoverable conditions: `IOException`,
`SQLException`.

**Unchecked** (extend `RuntimeException`) need no declaration. Intended for
programming errors: `NullPointerException`, `IllegalArgumentException`,
`IndexOutOfBoundsException`.

`Error` (e.g. `OutOfMemoryError`, `StackOverflowError`) signals a JVM-level
problem you should not catch.

The design debate is worth knowing: checked exceptions were meant to force
handling, but in practice they encourage `catch (Exception e) {}` and leak
implementation details through signatures. Later languages (C#, Kotlin, Scala)
deliberately omitted them. Worked example:
[`examples/java/exceptions/exception_handling_basics.java`](../../examples/java/exceptions/exception_handling_basics.java).

---

### 🔴 Q. What is type erasure?

**Answer.** Generics are a **compile-time** feature. The compiler checks types,
then erases them — `List<String>` becomes plain `List` in the bytecode, with
casts inserted automatically. This was done for backwards compatibility with
pre-generics code.

The consequences you can be asked to explain:

```java
List<String> a = new ArrayList<>();
List<Integer> b = new ArrayList<>();
a.getClass() == b.getClass();      // true — both are just ArrayList

// Illegal, because the type is not available at runtime:
// if (obj instanceof List<String>) { }
// T[] array = new T[10];
```

You also cannot overload on `List<String>` vs `List<Integer>` — after erasure
both methods have identical signatures. Contrast with C#, where generics are
reified and the runtime does know the type argument.

---

### 🟡 Q. How does garbage collection work?

**Answer.** The JVM reclaims objects no longer **reachable** from GC roots (stack
references, statics, JNI references). Note it is reachability, not reference
counting — so cycles are collected correctly.

The design rests on the **generational hypothesis**: most objects die young. So
the heap is split:

- **Young generation** (Eden + two survivor spaces) — collected frequently with
  cheap *minor* GCs that copy the few survivors out.
- **Old generation** — objects that survived several collections; collected
  rarely by an expensive *major* GC.

Modern collectors (G1, ZGC, Shenandoah) do most work concurrently to keep pause
times low — ZGC targets sub-millisecond pauses on large heaps.

`System.gc()` is a *suggestion* the JVM may ignore. You cannot force collection,
and calling it is almost always a mistake. Memory leaks in Java are real but take
a different form: objects still referenced but never used — a static collection
that only ever grows, an unremoved listener, an unclosed resource.

---

### 🟡 Q. What does the Stream API give you?

**Answer.** A declarative pipeline over a sequence, with lazy intermediate
operations and one terminal operation that triggers execution.

```java
List<String> names = people.stream()
    .filter(p -> p.age() >= 18)          // intermediate, lazy
    .map(Person::name)                   // intermediate, lazy
    .sorted()
    .toList();                           // terminal, runs the pipeline
```

Nothing executes until the terminal operation, which allows fusion and
short-circuiting (`findFirst` stops early).

Two cautions worth raising unprompted: a stream is **single-use** — reusing one
throws `IllegalStateException`; and `parallelStream()` is not free speed. It uses
the common ForkJoinPool, so it helps only for large datasets with CPU-bound,
independent, side-effect-free work, and can be slower otherwise. Worked example:
[`examples/java/streams/group_and_collect_with_streams.java`](../../examples/java/streams/group_and_collect_with_streams.java).

---

### 🟡 Q. `String`, `StringBuilder`, `StringBuffer`?

**Answer.** `String` is **immutable** — every concatenation allocates a new
object, so building in a loop is O(n²). `StringBuilder` is a mutable buffer, not
thread-safe, and is what you want. `StringBuffer` is the synchronised version:
slower, and almost never needed since a builder is normally local to one thread.

Note the compiler rewrites simple `+` concatenation into builder calls, so
`"a" + b + "c"` is fine — it is concatenation **inside a loop** that is the
problem. Worked example:
[`examples/java/strings/string_immutability_and_stringbuilder.java`](../../examples/java/strings/string_immutability_and_stringbuilder.java).
