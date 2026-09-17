import java.math.BigDecimal;

/** Java records provide concise, immutable-by-reference data carriers. */
record InvoiceLine(String description, int quantity, BigDecimal unitPrice) {
    // A compact constructor validates parameters before fields are assigned.
    InvoiceLine {
        if (description == null || description.isBlank()) {
            throw new IllegalArgumentException("description cannot be blank");
        }
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be positive");
        }
        if (unitPrice == null || unitPrice.signum() < 0) {
            throw new IllegalArgumentException("unit price cannot be negative");
        }
    }

    BigDecimal subtotal() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
}

class RecordDataCarriers {
    public static void main(String[] args) {
        var first = new InvoiceLine("Notebook", 3, new BigDecimal("4.50"));
        var sameValues = new InvoiceLine("Notebook", 3, new BigDecimal("4.50"));

        // Records generate accessors, equals, hashCode, and toString.
        System.out.println(first);
        System.out.println("Description: " + first.description());
        System.out.println("Subtotal: " + first.subtotal());
        System.out.println("Value equality: " + first.equals(sameValues));

        try {
            new InvoiceLine("Invalid", 0, BigDecimal.TEN);
        } catch (IllegalArgumentException error) {
            System.out.println("Validation caught: " + error.getMessage());
        }
    }
}
