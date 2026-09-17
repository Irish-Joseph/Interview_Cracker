/**
 * Topic: Function templates — generic code with type deduction.
 *
 * Concepts:
 * - template<typename T> function templates
 * - Template argument deduction (the compiler fills in T)
 * - Multiple type parameters
 * - non-type template parameters (constexpr values as parameters)
 * - Constrained template parameters (static_assert for pre-C++20)
 * - Why templates beat code duplication: one definition, any type
 *
 * A function template is a *recipe*: the compiler generates a
 * specialized function for each concrete type you use it with.
 * Type safety is preserved — wrong types fail at COMPILE time.
 *
 * Compile:  g++ -std=c++17 -Wall -Wextra -o templates_demo function_templates.cpp
 *
 * NOTE: validated by inspection (no C++ toolchain on authoring host).
 */

#include <array>
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

// --- 1. Simple template with deduction -------------------------------------

template <typename T>
const T& pick(const T& a, const T& b, bool condition) {
    // Works for int, double, std::string, your own types — without
    // writing the function four times.
    return condition ? a : b;
}

// --- 2. Multiple type parameters ---------------------------------------------

template <typename K, typename V>
void print_pair(const K& key, const V& value) {
    std::cout << key << " -> " << value << "\n";
}

// --- 3. Template on a container: find first match ------------------------------

template <typename Container>
bool contains(const Container& c, const typename Container::value_type& target) {
    for (const auto& element : c) {
        if (element == target) return true;
    }
    return false;
}

// --- 4. Non-type template parameter: a value, not a type -----------------------

template <std::size_t N>
void print_first_n(const std::vector<int>& values) {
    std::cout << "first " << N << " values: ";
    for (std::size_t i = 0; i < N && i < values.size(); i++) {
        std::cout << values[i] << ' ';
    }
    std::cout << "\n";
}

// --- 5. Compile-time constraints (pre-C++20 style) ------------------------------

template <typename T>
T safe_max(T a, T b) {
    // Enforce a requirement on T at compile time:
    static_assert(std::is_same_v<T, double>
                    || std::is_integral<T>,
                  "safe_max requires a numeric type");
    return a > b ? a : b;
}

int main() {
    // 1. Deduction: no <int> needed — the compiler sees the arguments.
    std::cout << "pick int:    " << pick(10, 20, true) << "\n";
    std::cout << "pick string: " << pick(std::string("tea"), std::string("coffee"), false) << "\n";

    // 2. Two type parameters, both deduced.
    print_pair(1, std::string("one"));
    print_pair("pi", 3.14159);

    // 3. Container template works for vector AND std::array.
    std::vector<std::string> fruits = {"apple", "kiwi", "mango"};
    std::array<int, 3> numbers = {5, 6, 7};
    std::cout << "fruits has kiwi:   " << std::boolalpha << contains(fruits, "kiwi") << "\n";
    std::cout << "fruits has plum:   " << contains(fruits, "plum") << "\n";
    std::cout << "numbers has 6:     " << contains(numbers, 6) << "\n";

    // 4. The count is fixed at COMPILE time — a different function per N.
    std::vector<int> sequence = {10, 20, 30, 40, 50};
    print_first_n<2>(sequence);
    print_first_n<4>(sequence);

    // 5. Constraint in action:
    std::cout << "max(3, 7) = " << safe_max(3, 7) << "\n";
    std::cout << "max(1.5, 2.5) = " << safe_max(1.5, 2.5) << "\n";
    // safe_max(std::string("a"), std::string("b"));  // would NOT compile
}

/**
 * Expected output:
 *
 * pick int:    10
 * pick string: coffee
 * 1 -> one
 * pi -> 3.14159
 * fruits has kiwi:   true
 * fruits has plum:   false
 * numbers has 6:     true
 * first 2 values: 10 20
 * first 4 values: 10 20 30 40
 * max(3, 7) = 7
 * max(1.5, 2.5) = 2.5
 */
