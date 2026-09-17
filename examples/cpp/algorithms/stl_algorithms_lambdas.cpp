/**
 * Topic: STL algorithms combined with lambdas.
 *
 * Concepts:
 * - <algorithm>: sort, min_element, max_element, count_if,
 *   transform, find_if, any_of/all_of/none_of, remove_if
 * - Lambdas: capture by value [&], [x], no capture
 * - The erase-remove idiom
 * - Range-based for loops
 *
 * STL algorithms take iterators/containers and a "behavior"
 * (often a lambda), so you rarely write loops for common tasks.
 * The lambda states WHAT to compare/test; the algorithm handles
 * the HOW (and is often hand-optimized).
 *
 * Compile:  g++ -std=c++17 -Wall -Wextra -o algo_demo stl_algorithms_lambdas.cpp
 *
 * NOTE: validated by inspection (no C++ toolchain on authoring host).
 */

#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

int main() {
    std::vector<int> scores = {72, 95, 61, 88, 40, 77, 95, 53};

    // --- 1. find the min / max ------------------------------------------------
    int lo = *std::min_element(scores.begin(), scores.end());
    int hi = *std::max_element(scores.begin(), scores.end());
    std::cout << "min=" << lo << " max=" << hi << "\n";
    // -> min=40 max=95

    // --- 2. sorting with a custom comparator ------------------------------------
    // Copy first, then sort descending without modifying the original.
    std::vector<int> ranked = scores;
    std::sort(ranked.begin(), ranked.end(), std::greater<int>());
    std::cout << "ranked: ";
    for (int s : ranked) std::cout << s << ' ';
    std::cout << "\n";
    // -> 95 95 88 77 72 61 53 40

    // --- 3. predicates: any_of / all_of / count_if ------------------------------
    bool hasFailing = std::any_of(scores.begin(), scores.end(),
                                  [](int s) { return s < 50; });
    bool allAttempted = std::all_of(scores.begin(), scores.end(),
                                     [](int s) { return s > 0; });
    long highAchievers = std::count_if(scores.begin(), scores.end(),
                                       [](int s) { return s >= 90; });
    std::cout << "any <50: " << std::boolalpha << hasFailing << "\n";
    std::cout << "all >0:  " << allAttempted << "\n";
    std::cout << "count >=90: " << highAchievers << "\n";
    // -> true / true / 2

    // --- 4. transform: map every element with a lambda --------------------------
    std::vector<int> doubled(scores.size());
    std::transform(scores.begin(), scores.end(), doubled.begin(),
                   [](int s) { return s * 2; });
    std::cout << "doubled first three: "
              << doubled[0] << ' ' << doubled[1] << ' ' << doubled[2] << "\n";
    // -> 144 190 122

    // --- 5. find_if: locate the first element matching a condition ---------------
    auto it = std::find_if(scores.begin(), scores.end(),
                           [](int s) { return s >= 90; });
    if (it != scores.end()) {
        std::cout << "first score >=90 is " << *it << "\n";
    }
    // -> 95

    // --- 6. capture: use a variable from the enclosing scope ----------------------
    int threshold = 70;
    std::vector<std::string> words = {"hi", "hello", "hey", "goodbye"};
    std::vector<std::string> longWords;
    std::copy_if(words.begin(), words.end(),
                 std::back_inserter(longWords),
                 [threshold](const std::string& w) {
                     // capture threshold BY VALUE: the lambda keeps its own copy
                     return static_cast<int>(w.size()) >= threshold / 10;
                 });
    std::cout << "words >= " << threshold / 10 << " chars: ";
    for (const auto& w : longWords) std::cout << w << ' ';
    std::cout << "\n";
    // -> hello goodbye

    // --- 7. the erase-remove idiom: delete elements matching a predicate --------
    std::vector<int> nums = {1, 2, 3, 4, 5, 6};
    // remove_if moves non-removed elements forward; erase trims the tail.
    nums.erase(std::remove_if(nums.begin(), nums.end(),
                              [](int n) { return n % 2 == 0; }),
               nums.end());
    std::cout << "odds only: ";
    for (int n : nums) std::cout << n << ' ';
    std::cout << "\n";
    // -> 1 3 5

    return 0;
}
