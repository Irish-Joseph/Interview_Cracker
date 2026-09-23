/*
Topic: Copy-and-swap assignment for strong exception safety.
Concepts: pass-by-value assignment, swap, self-assignment, RAII.
Run: c++ -std=c++17 -Wall -Wextra copy_and_swap_assignment.cpp -o demo
NOTE: validated by inspection (no C++ toolchain on this host).
Expected output: alpha -> beta; self: beta
*/

#include <algorithm>
#include <cassert>
#include <cstring>
#include <iostream>
#include <utility>

class Text {
public:
    explicit Text(const char* value = "")
        : size_(std::strlen(value)), data_(new char[size_ + 1]) {
        std::copy_n(value, size_ + 1, data_);
    }

    Text(const Text& other) : Text(other.data_) {}

    Text(Text&& other) noexcept : Text() {
        swap(*this, other);
    }

    ~Text() { delete[] data_; }

    // The copy or move into `other` finishes before this body. If copying
    // throws, *this is unchanged; swapping itself cannot throw.
    Text& operator=(Text other) noexcept {
        swap(*this, other);
        return *this;
    }

    friend void swap(Text& left, Text& right) noexcept {
        using std::swap;
        swap(left.size_, right.size_);
        swap(left.data_, right.data_);
    }

    const char* c_str() const noexcept { return data_; }

private:
    std::size_t size_;
    char* data_;
};

int main() {
    Text first("alpha");
    Text second("beta");
    std::cout << first.c_str() << " -> " << second.c_str() << '\n';

    first = second;
    assert(std::strcmp(first.c_str(), "beta") == 0);
    first = first; // Safe, though it performs a copy.
    std::cout << "self: " << first.c_str() << '\n';
}
