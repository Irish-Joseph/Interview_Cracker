// Topic: Associative containers - map, set, and their unordered cousins.
//
// The STL gives you two families for key-based lookup:
//   std::map / std::set             - ordered, balanced tree, O(log n)
//   std::unordered_map / _set       - hashed, O(1) average, no ordering
//
// Choosing between them is a real decision, not a style preference: one keeps
// your keys sorted and supports range queries, the other is faster but gives
// you no ordering at all.
//
// Concepts:
// - Insertion: operator[], insert, emplace, try_emplace, and what each does
//   when the key already exists
// - The operator[] trap: it INSERTS a default-constructed value on a miss
// - Lookup: find / count / contains (C++20), and structured bindings
// - Ordered-only powers: sorted iteration, lower_bound, upper_bound, range
// - Erasing safely while iterating
//
// Compile: g++ -std=c++20 -Wall -Wextra map_and_set_containers.cpp -o demo
//
// NOTE: validated by inspection (no C++ compiler on authoring host).

#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

int main() {
    // -----------------------------------------------------------------------
    // 1. Building a map, four ways
    // -----------------------------------------------------------------------
    std::map<std::string, int> stock{{"apple", 12}, {"pear", 0}};

    stock["plum"] = 3;                          // inserts, or overwrites
    stock.insert({"apple", 999});               // IGNORED: key already present
    stock.emplace("fig", 7);                    // constructs in place
    stock.try_emplace("pear", 42);              // also ignored; no value built

    std::cout << "-- contents (always sorted by key) --\n";
    for (const auto& [name, count] : stock) {   // structured bindings, C++17
        std::cout << "  " << name << " = " << count << '\n';
    }
    std::cout << "  apple is still " << stock.at("apple")
              << " (insert does not overwrite)\n";

    // -----------------------------------------------------------------------
    // 2. The operator[] trap
    // -----------------------------------------------------------------------
    std::cout << "-- operator[] inserts on a miss --\n";
    std::cout << "  size before: " << stock.size() << '\n';
    int missing = stock["durian"];              // creates durian = 0
    std::cout << "  stock[\"durian\"] = " << missing
              << ", size after: " << stock.size() << " (a key appeared!)\n";

    // Safe alternatives that never modify the container:
    //   .at(key)      throws std::out_of_range
    //   .find(key)    returns an iterator, end() on a miss
    //   .contains(key) C++20, returns bool
    //   .count(key)   0 or 1 for a non-multi container
    std::cout << "  contains(\"kiwi\"): " << std::boolalpha
              << stock.contains("kiwi") << '\n';

    if (auto it = stock.find("plum"); it != stock.end()) {
        std::cout << "  found plum = " << it->second << '\n';
    }

    // -----------------------------------------------------------------------
    // 3. Ordered-only: range queries
    // -----------------------------------------------------------------------
    std::map<int, std::string> events{
        {1990, "a"}, {1995, "b"}, {2001, "c"}, {2008, "d"}, {2019, "e"}};

    std::cout << "-- events in [1995, 2008] --\n";
    // lower_bound: first key NOT LESS than the argument.
    // upper_bound: first key GREATER than the argument.
    auto begin = events.lower_bound(1995);
    auto end = events.upper_bound(2008);
    for (auto it = begin; it != end; ++it) {
        std::cout << "  " << it->first << " -> " << it->second << '\n';
    }
    std::cout << "  first event from 2000 onwards: "
              << events.lower_bound(2000)->first << '\n';
    // An unordered_map cannot answer either of those questions at all.

    // -----------------------------------------------------------------------
    // 4. set and unordered_set
    // -----------------------------------------------------------------------
    std::set<std::string> ordered{"pear", "apple", "fig", "apple"};
    std::unordered_set<std::string> hashed{"pear", "apple", "fig", "apple"};

    std::cout << "-- set drops duplicates and sorts --\n  ";
    for (const auto& item : ordered) std::cout << item << ' ';
    std::cout << "\n  sizes: set=" << ordered.size()
              << " unordered_set=" << hashed.size()
              << " (same count, different order guarantees)\n";

    // insert returns {iterator, bool} - the bool says whether it was new.
    auto [position, inserted] = ordered.insert("apple");
    std::cout << "  inserting \"apple\" again: inserted=" << inserted
              << ", still points at \"" << *position << "\"\n";

    // -----------------------------------------------------------------------
    // 5. Erasing while iterating
    // -----------------------------------------------------------------------
    std::cout << "-- erase the zero-stock entries --\n";
    for (auto it = stock.begin(); it != stock.end(); ) {
        // erase() invalidates `it`, so use the iterator it RETURNS.
        // Writing ++it after erasing is undefined behaviour.
        if (it->second == 0) {
            it = stock.erase(it);
        } else {
            ++it;
        }
    }
    for (const auto& [name, count] : stock) {
        std::cout << "  " << name << " = " << count << '\n';
    }

    // C++20 offers a one-liner for exactly this:
    //   std::erase_if(stock, [](const auto& kv) { return kv.second == 0; });

    // -----------------------------------------------------------------------
    // 6. Which should you use?
    // -----------------------------------------------------------------------
    // map/set          : you need sorted iteration, range queries, or a
    //                    guaranteed O(log n) worst case
    // unordered_map/set: you only ever look keys up by exact value and want
    //                    the faster average case
    // A custom key type needs operator< for map/set, or a std::hash
    // specialisation plus operator== for the unordered ones.
    std::unordered_map<std::string, std::vector<int>> readings;
    readings["sensor-a"].push_back(21);   // operator[] default-constructs the
    readings["sensor-a"].push_back(23);   // vector, which is exactly what we want
    std::cout << "-- operator[] is ideal here --\n  sensor-a has "
              << readings["sensor-a"].size() << " readings\n";

    return 0;
}

/* Expected output:
-- contents (always sorted by key) --
  apple = 12
  fig = 7
  pear = 0
  plum = 3
  apple is still 12 (insert does not overwrite)
-- operator[] inserts on a miss --
  size before: 4
  stock["durian"] = 0, size after: 5 (a key appeared!)
  contains("kiwi"): false
  found plum = 3
-- events in [1995, 2008] --
  1995 -> b
  2001 -> c
  2008 -> d
  first event from 2000 onwards: 2001
-- set drops duplicates and sorts --
  apple fig pear
  sizes: set=3 unordered_set=3 (same count, different order guarantees)
  inserting "apple" again: inserted=false, still points at "apple"
-- erase the zero-stock entries --
  apple = 12
  fig = 7
  plum = 3
-- operator[] is ideal here --
  sensor-a has 2 readings
*/
