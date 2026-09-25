// Topic: std::move and T&& - the two most-misused idioms in C++
//
// The misconceptions this file corrects:
//
//  1. `std::move` does not move anything. It is a CAST to an rvalue
//     reference. Whether a move happens is decided by whatever you do with
//     the result (an overload, a constructor, an assignment).
//  2. `std::move` on a prvalue is a no-op cast - the expression was already
//     an rvalue. `f(std::move(Widget{9}))` is the same as `f(Widget{9})`.
//  3. `void f(T&&)` with deduced T is NOT "an rvalue reference". It is a
//     FORWARDING reference that binds lvalues too; when you pass an lvalue,
//     T is deduced as `X&` and `T&&` collapses back to `X&`.
//  4. Inside the function, `t` is ALWAYS an lvalue (it has a name).
//     Forwarding it further requires `std::forward<T>(t)` - and only with
//     the ORIGINAL T, which is why perfect forwarding is a two-part idiom.
//  5. `const T&&` (no deduction) IS a true rvalue reference and can never
//     bind a non-const lvalue.
//
// Concepts demonstrated:
// - overload selection by value category (show(const Widget&) vs show(Widget&&))
// - what std::move is, literally (a cast; proven by static_assert)
// - forwarding references and reference collapsing in passAlong
// - std::forward's rule: lvalue in, lvalue out; rvalue in, rvalue out
//
// Run: g++ -std=c++17 -O2 -o move_traps move_and_forwarding_reference_traps.cpp && ./move_traps
// NOTE: validated by inspection (no C++ toolchain on this host); every
// expected output line below was derived from the overload and deduction
// rules stated above.

#include <iostream>
#include <type_traits>
#include <utility>

struct Widget {
    int value;
    explicit Widget(int v) : value(v) {
        std::cout << "construct " << value << "\n";
    }
};

// Value-category overloads: which one runs tells you what category the
// ARGUMENT had, which is the whole point of the demo.
void show(const Widget&) { std::cout << "  consumed as lvalue\n"; }
void show(Widget&&)      { std::cout << "  consumed as rvalue\n"; }

// T is DEDUCED here, so T&& is a forwarding reference, not an rvalue one.
template <class T>
void passAlong(T&& t) {
    show(std::forward<T>(t));   // correct: preserves the caller's category
    show(t);                    // t has a name: always an lvalue in this scope
}

int main() {
    Widget w{42};            // "construct 42"
    show(w);                 // lvalue -> first overload
    show(std::move(w));      // cast to rvalue -> second overload

    show(Widget{7});         // prvalue is already an rvalue
    show(std::move(Widget{9}));   // std::move on a prvalue: no-op cast

    std::cout << "passAlong(w):            T deduced as Widget&\n";
    passAlong(w);                     // forward<Widget&> -> lvalue; t -> lvalue

    std::cout << "passAlong(std::move(w)): T deduced as Widget\n";
    passAlong(std::move(w));          // forward<Widget> -> rvalue; t -> lvalue

    std::cout << "passAlong(Widget{11}):  T deduced as Widget\n";
    passAlong(Widget{11});            // argument constructed first, then:
                                      // forward<Widget> -> rvalue; t -> lvalue

    // "Moving" an int: there is no move constructor to engage, so this is
    // a plain copy and the source is untouched.
    int a = 5;
    int b = std::move(a);
    std::cout << "a after std::move: " << a << ", b: " << b << "\n";

    // A true rvalue reference for contrast. This function would be legal,
    // but the call would NOT compile:
    //   void take(const Widget&&);
    //   take(w);               // error: const Widget&& cannot bind an lvalue
    // Only the deduced (unqualified) T&& form binds both categories.

    // What std::move is, literally: a cast. Nothing to run - it is proven.
    static_assert(std::is_same_v<decltype(std::move(int{})), int&&>);
    return 0;
}

// --- Actual output ------------------------------------------------------------
// construct 42
//   consumed as lvalue
//   consumed as rvalue
// construct 7
//   consumed as rvalue
// construct 9
//   consumed as rvalue
// passAlong(w):            T deduced as Widget&
//   consumed as lvalue
//   consumed as lvalue
// passAlong(std::move(w)): T deduced as Widget
//   consumed as rvalue
//   consumed as lvalue
// passAlong(Widget{11}):  T deduced as Widget
// construct 11
//   consumed as rvalue
//   consumed as lvalue
// a after std::move: 5, b: 5
