// Topic: std::string - the operations you reach for, and the cheap ones.
//
// std::string owns its characters and manages its own memory, which is why it
// replaced char* for almost everything. The companion type std::string_view
// (C++17) is a non-owning window onto existing characters: passing one copies
// nothing, which matters in hot paths.
//
// Concepts:
// - Construction, size, and bounds-checked at() vs unchecked operator[]
// - find / substr / replace / erase / insert, and the npos sentinel
// - Comparison, and why == on std::string is a value comparison (unlike char*)
// - Splitting and joining, which the standard library still does not provide
// - std::string_view: zero-copy views, and the dangling trap
// - Conversions: to_string, stoi/stod, and why stoi throws
//
// Compile: g++ -std=c++20 -Wall -Wextra string_operations.cpp -o demo && ./demo
//
// NOTE: validated by inspection (no C++ compiler on authoring host).

#include <cctype>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// ---------------------------------------------------------------------------
// Splitting: not in the standard library, so everyone writes this once.
// ---------------------------------------------------------------------------
std::vector<std::string> split(const std::string& text, char delimiter) {
    std::vector<std::string> parts;
    std::istringstream stream(text);
    std::string part;
    while (std::getline(stream, part, delimiter)) {
        parts.push_back(part);
    }
    return parts;
}

std::string join(const std::vector<std::string>& parts, const std::string& sep) {
    std::string result;
    for (std::size_t i = 0; i < parts.size(); ++i) {
        if (i > 0) {
            result += sep;
        }
        result += parts[i];
    }
    return result;
}

std::string trim(std::string_view text) {
    const char* whitespace = " \t\n\r";
    const auto first = text.find_first_not_of(whitespace);
    if (first == std::string_view::npos) {
        return "";                       // all whitespace
    }
    const auto last = text.find_last_not_of(whitespace);
    return std::string(text.substr(first, last - first + 1));
}

// Taking a string_view means callers can pass a std::string OR a literal
// with no allocation and no conversion.
std::size_t count_char(std::string_view text, char target) {
    std::size_t total = 0;
    for (char c : text) {
        if (c == target) {
            ++total;
        }
    }
    return total;
}

int main() {
    // -----------------------------------------------------------------------
    // 1. Basics
    // -----------------------------------------------------------------------
    std::string greeting = "Hello";
    greeting += ", world";
    greeting.append("!");

    std::cout << "-- basics --\n";
    std::cout << "  value : " << greeting << '\n';
    std::cout << "  size  : " << greeting.size() << " (length() is the same)\n";
    std::cout << "  empty : " << std::boolalpha << greeting.empty() << '\n';
    std::cout << "  front/back: " << greeting.front() << greeting.back() << '\n';

    // at() is bounds-checked and throws; operator[] is not.
    try {
        (void) greeting.at(999);
    } catch (const std::out_of_range&) {
        std::cout << "  at(999) threw std::out_of_range (operator[] would not)\n";
    }

    // -----------------------------------------------------------------------
    // 2. Searching
    // -----------------------------------------------------------------------
    std::cout << "-- searching --\n";
    const std::string path = "/var/log/app/server.log";

    // find returns npos, NOT -1, when there is no match. Comparing against
    // -1 happens to work only because npos is (size_t)-1; write npos.
    const auto slash = path.find_last_of('/');
    const auto dot = path.rfind('.');

    std::cout << "  find(\"log\")     = " << path.find("log") << '\n';
    std::cout << "  find(\"missing\") = "
              << (path.find("missing") == std::string::npos ? "npos" : "found") << '\n';
    std::cout << "  filename        = " << path.substr(slash + 1) << '\n';
    std::cout << "  stem            = " << path.substr(slash + 1, dot - slash - 1) << '\n';
    std::cout << "  extension       = " << path.substr(dot) << '\n';
    std::cout << "  starts_with     = " << path.starts_with("/var") << " (C++20)\n";
    std::cout << "  ends_with       = " << path.ends_with(".log") << " (C++20)\n";

    // -----------------------------------------------------------------------
    // 3. Modifying
    // -----------------------------------------------------------------------
    std::cout << "-- modifying --\n";
    const std::string sentence = "the quick brown fox";

    std::string upper = sentence;
    for (char& c : upper) {
        // toupper takes an int and misbehaves on negative char values, so
        // cast through unsigned char first. This is a real portability bug.
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    }
    std::cout << "  upper   : " << upper << '\n';

    std::string replaced = sentence;
    replaced.replace(replaced.find("quick"), 5, "slow");
    std::cout << "  replaced: " << replaced << '\n';

    std::string erased = sentence;
    erased.erase(0, 4);                  // drop "the "
    std::cout << "  erased  : " << erased << '\n';

    std::string inserted = sentence;
    inserted.insert(4, "very ");
    std::cout << "  inserted: " << inserted << '\n';

    // -----------------------------------------------------------------------
    // 4. Comparison
    // -----------------------------------------------------------------------
    std::cout << "-- comparison --\n";
    const std::string a = "apple";
    const std::string b = "apple";
    // == compares VALUES. With char* this would compare POINTERS instead,
    // which is the single most common C-string bug.
    std::cout << "  a == b            : " << (a == b) << '\n';
    std::cout << "  \"apple\" < \"banana\": " << (a < "banana") << '\n';
    std::cout << "  compare() sign    : negative means a sorts first\n";

    // -----------------------------------------------------------------------
    // 5. Splitting, joining, trimming
    // -----------------------------------------------------------------------
    std::cout << "-- split / join / trim --\n";
    const auto fields = split("id,name,email,active", ',');
    std::cout << "  " << fields.size() << " fields:";
    for (const auto& field : fields) {
        std::cout << " [" << field << ']';
    }
    std::cout << '\n';
    std::cout << "  joined : " << join(fields, " | ") << '\n';
    std::cout << "  trimmed: [" << trim("   padded\t\n") << "]\n";

    // -----------------------------------------------------------------------
    // 6. string_view
    // -----------------------------------------------------------------------
    std::cout << "-- string_view --\n";
    const std::string owned = "counting characters";
    std::cout << "  count 'n' in std::string : " << count_char(owned, 'n') << '\n';
    std::cout << "  count 'n' in a literal   : " << count_char("no allocation here", 'n') << '\n';

    // THE TRAP: a view owns nothing. Never return a view of a temporary, and
    // never let a view outlive the string it points into.
    //   std::string_view bad = std::string("temporary");   // dangles at once
    std::cout << "  a view is a pointer + length, so it must not outlive its owner\n";

    // -----------------------------------------------------------------------
    // 7. Conversions
    // -----------------------------------------------------------------------
    std::cout << "-- conversions --\n";
    std::cout << "  to_string(42) : " << std::to_string(42) << '\n';
    std::cout << "  stoi(\"123\")   : " << std::stoi("123") << '\n';
    std::cout << "  stod(\"3.5\")   : " << std::stod("3.5") << '\n';
    std::cout << "  stoi(\"12abc\") : " << std::stoi("12abc") << " (stops at the first non-digit)\n";
    try {
        (void) std::stoi("abc");
    } catch (const std::invalid_argument&) {
        std::cout << "  stoi(\"abc\")   : threw std::invalid_argument\n";
    }

    return 0;
}

/* Expected output:
-- basics --
  value : Hello, world!
  size  : 13 (length() is the same)
  empty : false
  front/back: H!
  at(999) threw std::out_of_range (operator[] would not)
-- searching --
  find("log")     = 5
  find("missing") = npos
  filename        = server.log
  stem            = server
  extension       = .log
  starts_with     = true (C++20)
  ends_with       = true (C++20)
-- modifying --
  upper   : THE QUICK BROWN FOX
  replaced: the slow brown fox
  erased  : quick brown fox
  inserted: the very quick brown fox
-- comparison --
  a == b            : true
  "apple" < "banana": true
  compare() sign    : negative means a sorts first
-- split / join / trim --
  4 fields: [id] [name] [email] [active]
  joined : id | name | email | active
  trimmed: [padded]
-- string_view --
  count 'n' in std::string : 2
  count 'n' in a literal   : 2
-- conversions --
  to_string(42) : 42
  stoi("123")   : 123
  stod("3.5")   : 3.5
  stoi("12abc") : 12 (stops at the first non-digit)
  stoi("abc")   : threw std::invalid_argument
*/
