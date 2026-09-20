// Topic: Range-based for, structured bindings, and std::array.
//
// Concepts:
// - Range-based for: loop over containers without iterator boilerplate
// - `const auto&` to avoid copies; by-value when you need a copy
// - Structured bindings (C++17): [auto a, auto b] = pair / .first/.second
// - std::array: fixed-size array on the stack (unlike C arrays it is
//   a real type with .size(), .at(), and iterable)
// - std::pair / std::tuple decomposition
//
// Validated by inspection (no C++ compiler on the authoring machine).
//
// Expected output:
//   letters: a b c d
//   upper:   A B C D
//   Alice (age 30)
//   Bob (age 25)
//   scores: 88 + 92 + 79 = 259
//   pair: x=3 y=4
//   tuple: red 12 2.5

#include <array>
#include <cctype>
#include <iostream>
#include <string>
#include <tuple>

int main() {
    // --- Range-based for over a std::array -------------------------
    std::array<std::string, 4> letters = {"a", "b", "c", "d"};

    // By value: each `s` is a COPY. Fine for cheap types / read-only use.
    std::cout << "letters:";
    for (const auto& s : letters) {   // const auto& : no copy, read-only
        std::cout << " " << s;
    }
    std::cout << "\n";

    // Uppercase in place: a non-const reference lets us mutate.
    std::cout << "upper:";
    for (auto& s : letters) {
        s[0] = static_cast<char>(std::toupper(static_cast<unsigned char>(s[0])));
        std::cout << " " << s;
    }
    std::cout << "\n";

    // --- Structured bindings: std::pair ----------------------------
    std::array<std::pair<std::string, int>, 2> people = {
        {"Alice", 30},
        {"Bob",   25},
    };
    for (const auto& [name, age] : people) {  // bind name and age directly
        std::cout << name << " (age " << age << ")\n";
    }

    // --- std::tuple structured binding -----------------------------
    // (a tuple is NOT a range — destructure it, don't range-over it)
    auto [s1, s2, s3] = std::make_tuple(88, 92, 79);
    int total = s1 + s2 + s3;
    std::cout << "scores: 88 + 92 + 79 = " << total << "\n";

    auto [x, y] = std::make_pair(3, 4);      // plain structured binding
    std::cout << "pair: x=" << x << " y=" << y << "\n";

    auto [colour, count, price] = std::make_tuple(std::string("red"), 12, 2.5);
    std::cout << "tuple: " << colour << " " << count << " " << price << "\n";

    return 0;
}
