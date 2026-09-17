// Topic: Operator overloading - making a user-defined type behave like a value.
//
// Overloading lets `a + b`, `a == b` and `std::cout << a` work for your own
// class. The goal is not cleverness: it is that a Money or Vec2 should be as
// natural to use as an int, with no surprises about what an operator means.
//
// Concepts:
// - Member vs non-member (free) operators, and why symmetry favours free ones
// - Implementing + in terms of += (do the work once)
// - operator<< for streams must be a free function
// - C++20 operator<=> and == generate the whole comparison family
// - operator[] with const and non-const overloads
// - Conversion operators and why `explicit` matters
//
// Compile: g++ -std=c++20 -Wall -Wextra operator_overloading.cpp -o demo && ./demo
//
// NOTE: validated by inspection (no C++ compiler on authoring host).

#include <compare>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

// ---------------------------------------------------------------------------
// 1. Money: arithmetic, comparison and stream output
// ---------------------------------------------------------------------------

class Money {
public:
    Money() = default;
    // `explicit` stops an accidental Money m = 500; from compiling. Without it
    // every int would silently convert, which hides real bugs.
    explicit Money(std::int64_t cents) : cents_(cents) {}

    std::int64_t cents() const { return cents_; }

    // Compound assignment is the primitive: it mutates and returns *this,
    // so chains like (a += b) += c work the way they do for built-in types.
    Money& operator+=(const Money& other) {
        cents_ += other.cents_;
        return *this;
    }

    Money& operator-=(const Money& other) {
        cents_ -= other.cents_;
        return *this;
    }

    Money& operator*=(int factor) {
        cents_ *= factor;
        return *this;
    }

    // Unary minus: takes no argument, returns a new value.
    Money operator-() const { return Money{-cents_}; }

    // C++20: one defaulted <=> gives <, <=, > and >=; a defaulted == gives
    // == and !=. Before C++20 this was six hand-written functions.
    auto operator<=>(const Money&) const = default;
    bool operator==(const Money&) const = default;

    // A conversion operator, deliberately explicit: `if (wallet)` works
    // because if-conditions use contextual conversion, but a silent
    // Money -> bool in arithmetic would be nonsense.
    explicit operator bool() const { return cents_ != 0; }

private:
    std::int64_t cents_ = 0;
};

// Free functions, because that is what makes `2 * price` possible: a member
// operator* would only ever match when Money is on the LEFT.
Money operator+(Money left, const Money& right) {
    left += right;  // `left` is a by-value copy, so this is the new result
    return left;
}

Money operator-(Money left, const Money& right) {
    left -= right;
    return left;
}

Money operator*(Money value, int factor) {
    value *= factor;
    return value;
}

Money operator*(int factor, Money value) {  // the symmetric overload
    value *= factor;
    return value;
}

// operator<< must be free: the left operand is the stream, not your class.
std::ostream& operator<<(std::ostream& out, const Money& money) {
    const std::int64_t cents = money.cents();
    const char* sign = cents < 0 ? "-" : "";
    const std::int64_t absolute = cents < 0 ? -cents : cents;

    // setfill is *sticky*: it would change every later insertion on this
    // stream. Save and restore it so the operator has no side effects.
    const char previous_fill = out.fill('0');
    out << sign << '$' << absolute / 100 << '.' << std::setw(2) << absolute % 100;
    out.fill(previous_fill);
    return out;
}

// ---------------------------------------------------------------------------
// 2. Matrix row: operator[] in const and non-const flavours
// ---------------------------------------------------------------------------

class Row {
public:
    explicit Row(std::size_t width) : cells_(width, 0.0) {}

    // Non-const overload returns a reference, so `row[2] = 4.5` assigns.
    double& operator[](std::size_t index) { return cells_.at(index); }

    // Const overload returns a copy (or a const reference) for reading only.
    double operator[](std::size_t index) const { return cells_.at(index); }

    std::size_t size() const { return cells_.size(); }

private:
    std::vector<double> cells_;
};

// ---------------------------------------------------------------------------
// 3. A callable object: operator()
// ---------------------------------------------------------------------------

class Between {
public:
    Between(int low, int high) : low_(low), high_(high) {
        if (low > high) {
            throw std::invalid_argument("low must not exceed high");
        }
    }

    // Overloading () turns instances into function objects, usable anywhere
    // a predicate is expected (std::count_if, std::sort, ...).
    bool operator()(int value) const { return value >= low_ && value <= high_; }

private:
    int low_;
    int high_;
};

int main() {
    const Money price{1250};   // $12.50
    const Money shipping{399}; // $3.99

    std::cout << "price:      " << price << '\n';
    std::cout << "shipping:   " << shipping << '\n';
    std::cout << "total:      " << price + shipping << '\n';
    std::cout << "refund:     " << -price << '\n';
    std::cout << "difference: " << price - shipping << '\n';
    std::cout << "three of:   " << 3 * price << '\n';  // needs the free overload

    Money basket{0};
    basket += price;
    basket += shipping;
    std::cout << "basket:     " << basket << '\n';
    std::cout << "basket == total? " << std::boolalpha
              << (basket == price + shipping) << '\n';
    std::cout << "shipping < price? " << (shipping < price) << '\n';

    // explicit operator bool: fine in a condition, rejected in arithmetic.
    std::cout << "empty basket is falsy? " << !static_cast<bool>(Money{0}) << '\n';

    Row row{3};
    row[0] = 1.5;      // non-const operator[]
    row[2] = 4.25;
    const Row& readable = row;
    std::cout << "row: ";
    for (std::size_t i = 0; i < readable.size(); ++i) {
        std::cout << readable[i] << ' ';  // const operator[]
    }
    std::cout << '\n';

    const Between teenager{13, 19};
    std::cout << "17 is a teen age? " << teenager(17) << '\n';
    std::cout << "21 is a teen age? " << teenager(21) << '\n';

    // Guidance: overload an operator only when its conventional meaning is
    // obvious for your type. Do not overload && || or the comma operator -
    // you would silently lose short-circuiting and evaluation order.
}

/* Expected output:
price:      $12.50
shipping:   $3.99
total:      $16.49
refund:     -$12.50
difference: $8.51
three of:   $37.50
basket:     $16.49
basket == total? true
shipping < price? true
empty basket is falsy? true
row: 1.5 0 4.25
17 is a teen age? true
21 is a teen age? false
*/
