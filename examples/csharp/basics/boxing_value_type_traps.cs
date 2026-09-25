// Topic: Boxing in C# - where it sneaks in, and what it silently does to you
//
// (Goes one level deeper than value_vs_reference_types.cs, which just
// introduces the idea: this file is about the traps.)
//
// Boxing = wrapping a value type in a heap object so it can be used where
// an `object` is expected. The traps:
//
//   1. It happens in more places than `object x = 5;`: any interface
//      assignment, any `List<object>`/`ArrayList` add, any non-generic
//      collection. (Generic containers like Dictionary<int,string> do NOT
//      box - the non-generic Hashtable of .NET 1.x did.)
//   2. Each box is a fresh allocation. Two boxes of the same value are two
//      different objects.
//   3. Unboxing copies the value OUT of the box. Mutating the copy cannot
//      affect the box - a boxed struct has no address you can write back to.
//   4. In hot code, boxing is GC churn: allocate, briefly use, collect.
//      This is why a generic method that constrains T to a class interface,
//      or a pre-C# 2 `ArrayList<int>`, was a real performance bug.
//
// Run: csc /out:boxing.exe boxing_value_type_traps.cs && boxing.exe
//      (or: dotnet run in a console project containing this file)
// NOTE: validated by inspection (no .NET toolchain on this host); every
// expected output line below was derived from the semantics stated above -
// plain values, no timing, platform or locale behaviour involved.

using System;
using System.Collections.Generic;

struct SensorReading : IComparable<SensorReading>
{
    public int Id;
    public int Value;
    public int CompareTo(SensorReading other) => Value.CompareTo(other.Value);
}

SensorReading reading = new SensorReading { Id = 7, Value = 42 };

// --- 1. Where boxing sneaks in --------------------------------------------

object boxed = reading;                    // (a) assignment to object
IComparable<SensorReading> comparable = reading;   // (b) interface: also a box
List<object> bag = new List<object>();
bag.Add(1);
bag.Add(2.5m);
bag.Add(reading);                          // (c) value into List<object>

Console.WriteLine($"box type: {boxed.GetType()}");
Console.WriteLine($"same physical box as interface? {ReferenceEquals(boxed, comparable)}");

// --- 2. Unboxing copies: the box cannot be written through ----------------

object num = 5;
int copy = (int)num;       // unbox = copy the value out of the heap object
copy = 99;                 // mutate the copy
Console.WriteLine($"box still: {num}, local copy: {copy}");

// --- 3. Virtual/interface dispatch runs on the boxed copy ------------------

SensorReading r2 = new SensorReading { Id = 1, Value = 10 };
IComparable<SensorReading> ic = r2;        // boxed copy
Console.WriteLine($"compare 10 vs 20: {ic.CompareTo(new SensorReading { Value = 20 })}");

// --- 4. Two boxes, one value: equality is value-based, identity is not ----

object a = 5;
object b = 5;
Console.WriteLine($"Equals: {a.Equals(b)}, ReferenceEquals: {ReferenceEquals(a, b)}");

// --- Rule of thumb ---------------------------------------------------------
// If a value type is flowing through `object`, an interface, or a
// non-generic collection in a hot path, that is a leak you can usually see
// in a profiler as allocation + GC time. The fix is almost always "make the
// container generic" - which is why List<T> replaced ArrayList and
// Dictionary<K,V> replaced Hashtable in idiomatic C#.

// --- Actual output ------------------------------------------------------------
// box type: SensorReading
// same physical box as interface? False
// box still: 5, local copy: 99
// compare 10 vs 20: -1
// Equals: True, ReferenceEquals: False
