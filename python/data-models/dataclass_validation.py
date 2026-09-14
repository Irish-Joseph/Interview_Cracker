"""Dataclasses: generated methods, derived fields, and validation."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Product:
    """An immutable product whose final price is calculated after validation."""

    name: str
    price: float
    discount_percent: float = 0
    final_price: float = field(init=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be blank")
        if self.price < 0:
            raise ValueError("price cannot be negative")
        if not 0 <= self.discount_percent <= 100:
            raise ValueError("discount must be between 0 and 100")

        discounted = self.price * (1 - self.discount_percent / 100)
        # A frozen dataclass needs object.__setattr__ during initialization.
        object.__setattr__(self, "final_price", round(discounted, 2))


def main() -> None:
    keyboard = Product("Mechanical keyboard", 120.00, 15)
    print(keyboard)
    print(f"Final price: ${keyboard.final_price:.2f}")

    try:
        Product("Invalid", 10, 125)
    except ValueError as error:
        print(f"Validation caught: {error}")


if __name__ == "__main__":
    main()

# frozen=True prevents later mutation; slots=True avoids a per-instance __dict__.
