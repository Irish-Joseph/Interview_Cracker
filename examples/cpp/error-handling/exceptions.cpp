/**
 * Topic: C++ exceptions — throw, catch, custom types, rethrow.
 *
 * Concepts:
 * - try / catch (by reference!) / multiple handlers
 * - std::exception hierarchy: runtime_error, invalid_argument, ...
 * - Defining custom exception classes
 * - Re-throwing with `throw;` and catching "everything"
 * - noexcept: promising a function never throws
 * - Exception safety levels (brief note)
 *
 * The golden rule: catch by const REFERENCE (const std::exception&).
 * Catching by value "slices" derived exception types — you lose
 * the subclass and its data.
 *
 * Compile:  g++ -std=c++17 -Wall -Wextra -o exceptions exceptions.cpp
 *
 * NOTE: validated by inspection (no C++ toolchain on authoring host).
 */

#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

// --- A custom exception type ------------------------------------------------

class InsufficientBalanceException : public std::runtime_error {
public:
    InsufficientBalanceException(double have, double wanted)
        : std::runtime_error("balance " + std::to_string(have)
                             + " < withdrawal " + std::to_string(wanted)),
          balance(have),
          amount(wanted) {}

    double balance; // structured data beyond the message
    double amount;
};

// --- A function that throws, and marks itself noexcept where safe -----------

double withdraw(double& balance, double amount) {
    if (amount < 0) {
        // Standard library exception: the right default for bad arguments.
        throw std::invalid_argument("amount must be >= 0");
    }
    if (amount > balance) {
        // Domain exception with extra structured fields.
        throw InsufficientBalanceException(balance, amount);
    }
    balance -= amount;
    return balance;
}

// noexcept: the contract is "this never throws".
// (Violating it calls std::terminate — so only promise it when true.)
int safe_add(int a, int b) noexcept {
    return a + b;
}

int main() {
    double account = 100.0;

    // --- 1. Happy path ----------------------------------------------------------
    std::cout << "after 30: " << withdraw(account, 30.0) << "\n";
    // -> after 30: 70

    // --- 2. Catching a SPECIFIC custom type ---------------------------------------
    try {
        withdraw(account, 80.0); // 80 > 70 -> throws
    } catch (const InsufficientBalanceException& e) {
        // const REFERENCE: preserves the derived type and its fields.
        std::cout << "insufficient: " << e.what() << "\n";
        std::cout << "  (fields: balance=" << e.balance
                  << " amount=" << e.amount << ")\n";
    }
    // -> insufficient: balance 70 < withdrawal 80
    //    (fields: balance=70 amount=80)

    // --- 3. Multiple handlers: most specific first ---------------------------------
    try {
        withdraw(account, -5.0); // invalid_argument
    } catch (const InsufficientBalanceException& e) {
        std::cout << "wrong branch: " << e.what() << "\n";
    } catch (const std::invalid_argument& e) {
        std::cout << "bad argument: " << e.what() << "\n";
        // -> bad argument: amount must be >= 0
    } catch (const std::exception& e) {
        // Catch-all for anything else std-defined.
        std::cout << "std exception: " << e.what() << "\n";
    }

    // --- 4. Rethrow with `throw;` — preserve the ORIGINAL exception ---------------
    // Classic wrapper pattern: add context at each layer, keep the cause.
    try {
        try {
            withdraw(account, 1000.0);
        } catch (const std::exception& e) {
            // We can log/transform here, then rethrow UNCHANGED:
            std::cout << "inner layer saw: " << e.what() << "\n";
            throw; // rethrows the SAME exception (same type, same object)
        }
    } catch (const InsufficientBalanceException& e) {
        // Still the original type — `throw;` did not convert it.
        std::cout << "outer layer caught original type: " << e.what() << "\n";
    }
    // -> inner layer saw: balance 70 < withdrawal 1000
    //    outer layer caught original type: balance 70 < withdrawal 1000

    // --- 5. Catching EVERYTHING ------------------------------------------------------
    // `catch (...)` matches any thrown type (including non-std ones).
    // Rethrow if you don't know how to handle it:
    try {
        throw 42; // even an int can be thrown (bad practice, but legal)
    } catch (...) {
        std::cout << "caught an int with catch(...)\n";
        // throw; // <- uncomment to propagate further
    }
    // -> caught an int with catch(...)

    // --- 6. Ranges and vectors: exceptions unwind cleanly ------------------------------
    // Destruction of automatic objects happens on the unwinding path —
    // this is what makes exceptions "safe" for resource management.
    try {
        std::vector<std::string> items = {"a", "b", "c"};
        for (const auto& item : items) {
            std::cout << item;
            if (item == "b") throw std::logic_error("stop at b");
        }
    } catch (const std::logic_error& e) {
        std::cout << " | unwound: " << e.what() << "\n";
        // -> a b | unwound: stop at b
        // (items is destroyed as the stack unwinds — no leak)
    }

    std::cout << "safe_add(2, 3) = " << safe_add(2, 3) << "\n";
    // -> safe_add(2, 3) = 5
    return 0;
}
