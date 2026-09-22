// Topic: std::string_view lifetime traps - borrowing text you do not own
//
// A string_view is a (pointer, length) pair with NO ownership. It is
// wonderful for passing text around read-only at zero cost, and dangerous
// the moment the text it points at dies first.
//
// Concepts:
//   - returning a string_view of a LOCAL std::string: dangling (UB to use)
//   - the contrast everyone gets wrong: const std::string& to a temporary
//     is SAFE (lifetime extension), but string_view to a temporary is NOT -
//     string_view is not a reference, so lifetime extension does not apply
//   - the two safe shapes: view into a member the object owns, or copy
//   - string_view is NOT null-terminated - don't hand it to C APIs
//
// Compile: g++ -std=c++17 -O2 -o string_view_lifetime string_view_lifetime.cpp
// NOTE: validated by inspection (no C++ toolchain on this host). The dangling
// case is UB by definition, so its "output" is not a stable literal; the
// program prints a fixed marker for it instead of dereferencing the garbage.

#include <iostream>
#include <string>
#include <string_view>

// UNSAFE: the std::string dies when the function returns. Every character
// this view refers to is gone. Using the result is undefined behaviour.
// (Sanitizers - ASan/UBSan with -fsanitize=address,undefined - catch exactly
// this shape of bug in CI, which is how you find them before users do.)
std::string_view extract_word_unsafe() {
    std::string local = "temporary";   // dies on return
    return local.substr(3, 5);         // "porar" - a view into dead memory
}

// The trap has a decoy: the const-reference version of the SAME idea is fine,
// because binding a const reference to a temporary EXTENDS the temporary's
// lifetime to the reference's. string_view is not a reference - no extension.
const std::string& extract_word_reference() {
    return std::string("temporary").substr(3, 5);   // OK: extended lifetime
}

// SAFE shape 1: the view refers to memory the object owns.
class Catalog {
    std::string title_ = "the quick brown fox";
public:
    std::string_view title() const { return title_; }   // valid as long as *this is
};

// SAFE shape 2: copy when you must outlive the source.
std::string extract_word_safe() {
    std::string local = "temporary";
    return local.substr(3, 5);   // substr on std::string RETURNS A COPY
}

int main() {
    auto by_ref = extract_word_reference();
    std::cout << "const std::string&  : " << by_ref << "   (safe - lifetime extended)\n";

    Catalog catalog;
    std::string_view t = catalog.title();
    std::cout << "member-backed view  : " << t << "   (safe - object outlives it)\n";
    std::cout << "  .size() = " << t.size() << ", .data()[0] = " << t.front() << "\n";
    std::cout << "  null-terminated?  : " << (t[t.size()] == '\0' ? "no - string_view needs no sentinel" : "yes") << "\n";

    std::string copied = extract_word_safe();
    std::cout << "copied std::string  : " << copied << "   (safe - owns its bytes)\n";

    std::cout << "dangling case       : (not printed - extract_word_unsafe() returns a view into a dead string; using it is UB)\n";
    return 0;
}

/*
Expected output:

const std::string&  : porar   (safe - lifetime extended)
member-backed view  : the quick brown fox   (safe - object outlives it)
  .size() = 19, .data()[0] = t
  null-terminated?  : no - string_view needs no sentinel
copied std::string  : porar   (safe - owns its bytes)
dangling case       : (not printed - extract_word_unsafe() returns a view into a dead string; using it is UB)
*/
