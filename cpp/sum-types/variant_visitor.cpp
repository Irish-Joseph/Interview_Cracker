// std::variant models a value that is exactly one of several known types.
#include <iostream>
#include <string>
#include <type_traits>
#include <variant>
#include <vector>

struct Text {
    std::string value;
};

struct Number {
    double value;
};

struct Toggle {
    bool value;
};

using Setting = std::variant<Text, Number, Toggle>;

// This helper combines lambdas into one overloaded visitor.
template <class... Callables>
struct Overloaded : Callables... {
    using Callables::operator()...;
};

template <class... Callables>
Overloaded(Callables...) -> Overloaded<Callables...>;

std::string display(const Setting& setting) {
    return std::visit(
        Overloaded{
            [](const Text& text) { return text.value; },
            [](const Number& number) { return std::to_string(number.value); },
            [](const Toggle& toggle) {
                return std::string{toggle.value ? "enabled" : "disabled"};
            },
        },
        setting);
}

int main() {
    std::vector<Setting> settings{
        Text{"dark theme"}, Number{1.25}, Toggle{true},
    };

    for (const auto& setting : settings) {
        std::cout << display(setting) << '\n';
    }

    Setting current = Number{42.0};
    if (const auto* number = std::get_if<Number>(&current)) {
        std::cout << "Numeric value: " << number->value << '\n';
    }

    std::cout << "Active alternative index: " << current.index() << '\n';
}

// Adding a new alternative forces visitors to decide how it should be handled.
