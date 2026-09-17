// Topic: Value types vs reference types in C#.
//
// Concepts:
// - struct (value type) vs class (reference type)
// - Copy semantics: value types copy the DATA, reference types
//   copy the HANDLE (two variables, one object)
// - Nullability: structs are non-nullable (except Nullable<T>),
//   classes can be null
// - Boxing: wrapping a value type in object
// - When to use which: small immutable data -> struct; identity,
//   inheritance, large objects -> class
//
// The one-paragraph version:
//   int, Point (struct)  => the variable IS the data (on the stack)
//   List<int>, PointDto (class) => the variable is a pointer to
//                                  data elsewhere (on the heap)
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;

// A value type: plain data, copied by value.
public struct Point
{
    public int X;
    public int Y;

    public Point(int x, int y)
    {
        X = x;
        Y = y;
    }

    public void Move(int dx, int dy)
    {
        X += dx;
        Y += dy;
    }

    public override string ToString() => $"({X}, {Y})";
}

// A reference type: an object on the heap, shared by all references.
public class BankAccount
{
    public string Owner { get; }
    public double Balance { get; private set; }

    public BankAccount(string owner, double balance)
    {
        Owner = owner;
        Balance = balance;
    }

    public void Deposit(double amount) => Balance += amount;
}

public class ValueVsReference
{
    public static void Main()
    {
        // --- 1. Value types: assignment copies the data -----------------------
        Point a = new Point(1, 2);
        Point b = a;        // b is an independent COPY
        b.Move(10, 0);
        Console.WriteLine($"a = {a}");  // (1, 2)  unchanged
        Console.WriteLine($"b = {b}");  // (11, 2) only b moved

        // --- 2. Reference types: assignment copies the reference --------------
        BankAccount account1 = new BankAccount("Alice", 100);
        BankAccount account2 = account1;  // SAME object, two names
        account2.Deposit(50);
        Console.WriteLine($"account1.Balance = {account1.Balance}");
        // -> 150 (both names see the one object)
        Console.WriteLine($"same object: {ReferenceEquals(account1, account2)}");
        // -> True

        // --- 3. null: legal for classes, impossible for plain structs ---------
        BankAccount nobody = null;
        Console.WriteLine($"nobody is null: {nobody is null}");
        // -> True
        // Point p = null;   // would NOT compile (structs can't be null)

        // Nullable<T> is the escape hatch for "maybe no value":
        Point? maybePoint = null;
        Console.WriteLine($"maybePoint is null: {maybePoint is null}");
        // -> True

        // --- 4. Boxing: a value type can masquerade as an object --------------
        object boxed = 42;                 // int is boxed into a heap object
        object unboxed = boxed;            // reference to that box
        Console.WriteLine($"boxed value: {unboxed}");
        // -> 42
        // Beware: boxing/unboxing has an allocation cost, and a boxed
        // value cannot be modified through the box.

        // --- 5. Arrays hold values: mutating an element mutates the array ------
        Point[] grid = { new Point(0, 0), new Point(1, 1) };
        grid[0] = grid[1];        // copies the Point VALUE into slot 0
        grid[1].Move(5, 5);       // modifies the array's slot 1
        Console.WriteLine($"grid[0] = {grid[0]}");  // (1, 1)
        Console.WriteLine($"grid[1] = {grid[1]}");  // (6, 6)

        // --- 6. Rule of thumb ---------------------------------------------------
        // struct: small, immutable-ish data (points, ranges, RGB colors);
        //         no inheritance; avoid for objects that need identity.
        // class:  identity matters, inheritance needed, large/mutable
        //         state, or interfaces with shared instances.
    }
}

/**
 * Expected output:
 *
 * a = (1, 2)
 * b = (11, 2)
 * account1.Balance = 150
 * same object: True
 * nobody is null: True
 * maybePoint is null: True
 * boxed value: 42
 * grid[0] = (1, 1)
 * grid[1] = (6, 6)
 */
