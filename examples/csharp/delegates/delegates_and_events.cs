// Topic: Delegates and events in C# — the foundation of callbacks.
//
// Concepts:
// - Delegates: type-safe function pointers
// - Built-in delegate types: Action / Func / Predicate
// - Method groups and lambdas as delegate values
// - Multicast delegates (+, -=)
// - Events: restricted delegates (subscribe from outside,
//   invoke from inside)
// - The publisher/subscriber pattern
//
// Delegates generalize "passing a function"; events add access
// control on top: others may SUBSCRIBE, only the owner may FIRE.
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;

// --- 1. A custom delegate type (rare today — Action/Func cover most) ----------

// A validator: takes a string, returns a bool.
public delegate bool Validator(string input);

public static class Validators
{
    public static bool IsNonEmpty(string s) => !string.IsNullOrWhiteSpace(s);
    public static bool IsEmailish(string s) => s.Contains('@') && s.Contains('.');
    public static bool Max20Chars(string s) => s.Length <= 20;
}

// --- 2. A publisher: the Counter that raises an event --------------------------

public class Counter
{
    private int _value;
    public int Value => _value;

    // Event declaration: a delegate type others can subscribe to.
    // Subscribers receive the sender and the new value.
    public event EventHandler<int>? ValueChanged;

    // Subscribers can ALSO hear about milestones:
    public event Action<int>? MilestoneReached;

    public void Increment()
    {
        _value++;
        // NULL-CHECK before invoking: nobody may be subscribed.
        ValueChanged?.Invoke(this, _value);

        if (_value % 5 == 0)
        {
            MilestoneReached?.Invoke(_value);
        }
    }
}

public class DelegatesAndEvents
{
    public static void Main()
    {
        // --- 3. Delegates: method groups, lambdas, composition -----------------
        Validator v1 = Validators.IsNonEmpty;          // method group
        Validator v2 = s => s.StartsWith("admin");     // lambda
        Validator combined = s => v1(s) && v2(s);      // composed

        Console.WriteLine($"\"admin@x.y\" passes combined: {combined("admin@x.y")}");
        // -> true
        Console.WriteLine($"\"guest\" passes combined: {combined("guest")}");
        // -> false

        // Func<T, R> and Predicate<T> are the built-ins:
        Func<int, int, int> add = (a, b) => a + b;
        Predicate<string> hasAt = s => s.Contains('@');
        Console.WriteLine($"add(2,3)={add(2, 3)}, \"a@b\" hasAt: {hasAt("a@b")}");
        // -> add(2,3)=5, "a@b" hasAt: True

        // Multicast: += wires several handlers, all invoked in order.
        Action shout = () => Console.Write("[1] ");
        shout += () => Console.Write("[2] ");
        shout();
        Console.WriteLine();
        // -> [1] [2]
        shout -= () => Console.Write("[2] "); // note: can't remove a LAMBDA
        // (a new lambda is a different delegate; remove by named handler)

        // --- 4. Events: publisher / subscriber -----------------------------------
        var counter = new Counter();

        // Subscribe with named methods (so we can unsubscribe later).
        counter.ValueChanged += OnValueChanged;
        counter.MilestoneReached += OnMilestone;

        // A local lambda subscriber — fine for one-shot listeners.
        counter.ValueChanged += (_, v) =>
            Console.WriteLine($"  (lambda heard value {v})");

        for (int i = 0; i < 6; i++)
        {
            counter.Increment();
        }

        // Unsubscribe: prevents leaks (the publisher otherwise keeps
        // a reference to the subscriber forever).
        counter.ValueChanged -= OnValueChanged;
        counter.MilestoneReached -= OnMilestone;

        counter.Increment(); // only the lambda hears now
    }

    // Subscribers — in another class, like real-world consumers.
    private static void OnValueChanged(object? sender, int value)
    {
        Console.WriteLine($"  (logger) counter is now {value}");
    }

    private static void OnMilestone(int milestone)
    {
        Console.WriteLine($"  (alarms) MILESTONE: {milestone}!");
    }
}

/**
 * Expected output:
 *
 * "admin@x.y" passes combined: True
 * "guest" passes combined: False
 * add(2,3)=5, "a@b" hasAt: True
 * [1] [2]
 *   (logger) counter is now 1
 *   (lambda heard value 1)
 *   (logger) counter is now 2
 *   (lambda heard value 2)
 *   (logger) counter is now 3
 *   (lambda heard value 3)
 *   (logger) counter is now 4
 *   (lambda heard value 4)
 *   (logger) counter is now 5
 *   (lambda heard value 5)
 *   (alarms) MILESTONE: 5!
 *   (logger) counter is now 6
 *   (lambda heard value 6)
 *   (lambda heard value 7)
 */
