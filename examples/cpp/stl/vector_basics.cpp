/**
 * Topic: std::vector — the everyday dynamic array.
 *
 * Concepts:
 * - push_back / pop_back and automatic growth
 * - size vs capacity (amortized O(1) growth)
 * - Range-based for loops and index loops
 * - Initialization styles: {}, {1,2,3}, n copies of value
 * - front()/back() and empty()
 * - Why raw indices can outlive (and break) — a brief note
 *
 * std::vector stores elements in a contiguous heap buffer and
 * resizes itself. It is the default choice in C++ for "a list
 * of things that changes size".
 *
 * Time Complexity: push_back O(1) amortized, front/back O(1)
 *
 * Compile:  g++ -std=c++17 -Wall -Wextra -o vector_demo vector_basics.cpp
 *
 * NOTE: validated by inspection (no C++ toolchain on authoring host).
 */

#include <iostream>
#include <string>
#include <vector>

int main() {
    // --- 1. Initialization styles -------------------------------------------
    std::vector<int> a;                 // empty
    std::vector<int> b{1, 2, 3, 4};     // initializer list
    std::vector<int> c(5, 7);           // five copies of 7
    std::vector<std::string> names = {"Ada", "Linus", "Grace"};

    std::cout << "b = ";
    for (int x : b) std::cout << x << ' ';
    std::cout << "\nc = ";
    for (int x : c) std::cout << x << ' ';
    std::cout << "\n";
    // -> b = 1 2 3 4
    // -> c = 7 7 7 7 7

    // --- 2. push_back / pop_back -----------------------------------------------
    std::vector<int> stack;
    stack.push_back(10);
    stack.push_back(20);
    stack.push_back(30);

    std::cout << "size=" << stack.size()
              << " capacity=" << stack.capacity() << "\n";
    // capacity >= size; the vector pre-allocates to grow cheaply

    std::cout << "back = " << stack.back() << "\n";   // -> 30
    std::cout << "front = " << stack.front() << "\n"; // -> 10

    stack.pop_back();
    std::cout << "after pop_back, size=" << stack.size()
              << " back=" << stack.back() << "\n";
    // -> size=2 back=20

    // --- 3. Iteration: index vs range-for -----------------------------------------
    for (std::size_t i = 0; i < names.size(); i++) {
        std::cout << names[i] << " ";
    }
    std::cout << "\n";
    // -> Ada Linus Grace

    for (const auto& name : names) {  // range-for: cleaner, no indices
        std::cout << name << " ";
    }
    std::cout << "\n";

    // --- 4. empty() before back()/front() — never call them on an empty vector ---
    std::vector<int> empty;
    if (empty.empty()) {
        std::cout << "safe: vector is empty, skip back()\n";
    }

    // --- 5. Modifying elements: operators and assignment ---------------------------
    b[0] = 99;                    // by index
    std::cout << "b[0] now: " << b[0] << "\n";        // -> 99

    // A vector of vectors: a jagged 2D list.
    std::vector<std::vector<int>> rows = {{1, 2}, {3}, {4, 5, 6}};
    std::cout << "row sizes: ";
    for (const auto& row : rows) {
        std::cout << row.size() << ' ';
    }
    std::cout << "\n";
    // -> row sizes: 2 1 3

    // --- 6. Performance note ----------------------------------------------------------
    // push_back amortized O(1): the vector roughly doubles capacity,
    // so n pushes cost O(n) total. reserve() avoids intermediate
    // reallocations when the final size is known:
    std::vector<int> known;
    known.reserve(1000);   // allocate once for up to 1000 elements
    for (int i = 0; i < 1000; i++) known.push_back(i);
    std::cout << "known.size()=" << known.size()
              << " known.capacity()=" << known.capacity() << "\n";
    // -> known.size()=1000 known.capacity()=1000 (no regrowth happened)

    return 0;
}
