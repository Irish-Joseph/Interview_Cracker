// Topic: Smart pointers — unique_ptr and shared_ptr ownership.
//
// Concepts:
// - RAII ownership: the pointer frees the object automatically
// - std::unique_ptr: exclusive ownership, cannot be copied, can be moved
// - std::shared_ptr: shared ownership with a reference count
// - std::make_unique / std::make_shared (exception-safe allocation)
// - The use_count() view of shared ownership
//
// Example output:
//   unique owns: 42
//   moved pointer owns: 42
//   old unique is now null: yes
//   inside block use_count: 2
//   after block use_count: 1
//   two owners: 2
//   ~Widget(value=9)
//   done
//   ~Widget(value=7)
//   ~Widget(value=42)

#include <memory>
#include <iostream>

struct Widget {
    int value;
    ~Widget() {
        std::cout << "~Widget(value=" << value << ")\n";
    }
};

int main() {
    // unique_ptr: exactly ONE owner. make_unique handles allocation
    // and is exception-safe (no leak if the constructor throws).
    auto w = std::make_unique<Widget>(Widget{42});
    std::cout << "unique owns: " << w->value << "\n";

    // unique_ptr cannot be copied, but can be MOVED:
    // ownership transfers and the source becomes null.
    auto w2 = std::move(w);
    std::cout << "moved pointer owns: " << w2->value << "\n";
    std::cout << "old unique is now null: "
              << (w == nullptr ? "yes" : "no") << "\n";

    // shared_ptr: several owners, object destroyed when the LAST
    // shared_ptr goes away. use_count() shows how many remain.
    auto s1 = std::make_shared<Widget>(Widget{7});
    {
        auto s2 = s1; // copy: both point at the same Widget
        std::cout << "inside block use_count: " << s1.use_count() << "\n";
        // s2 dies here at the closing brace
    }
    std::cout << "after block use_count: " << s1.use_count() << "\n";

    {
        // A second independent ownership chain:
        auto a1 = std::make_shared<Widget>(Widget{9});
        auto a2 = a1;
        std::cout << "two owners: " << a1.use_count() << "\n";
    } // a1 and a2 die here; reference count hits 0 -> ~Widget runs
    std::cout << "done\n";
}
