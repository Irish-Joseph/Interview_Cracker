/**
 * Topic: Inheritance and polymorphism.
 *
 * Concepts:
 * - extends and the is-a relationship
 * - Method overriding and the @Override annotation
 * - super for reusing parent logic
 * - Dynamic dispatch: a reference's type vs the object's type
 * - A collection of base-type references behaving per subclass
 *
 * Polymorphism means: code written against a base type works with
 * ANY subclass instance, and each object picks its own overridden
 * method at RUN TIME (dynamic dispatch).
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
public class PolymorphicShapes {

    // --- Base class ---------------------------------------------------------

    static abstract class Shape {
        final String name;

        Shape(String name) {
            this.name = name;
        }

        /**
         * Template method: shared structure, pluggable detail.
         * describe() calls area() — which gets dispatched to the
         * subclass override even though we're "in" the base class.
         */
        final String describe() {
            return name + " has area " + String.format("%.2f", area());
        }

        /** Subclasses MUST provide their own area calculation. */
        abstract double area();
    }

    // --- Subclasses ----------------------------------------------------------

    static class Circle extends Shape {
        final double radius;

        Circle(double radius) {
            super("circle");
            this.radius = radius;
        }

        @Override
        double area() {
            return Math.PI * radius * radius;
        }
    }

    static class Rectangle extends Shape {
        final double width, height;

        Rectangle(double width, double height) {
            super("rectangle");
            this.width = width;
            this.height = height;
        }

        @Override
        double area() {
            return width * height;
        }
    }

    /**
     * Shows super: Triangle reuses the parent constructor and adds
     * its own state without duplicating base behavior.
     */
    static class Triangle extends Shape {
        final double base, height;

        Triangle(double base, double height) {
            super("triangle");
            this.base = base;
            this.height = height;
        }

        @Override
        double area() {
            return (base * height) / 2;
        }
    }

    // --- Demo -----------------------------------------------------------------

    public static void main(String[] args) {
        // A list of BASE-TYPE references holding different subclasses.
        java.util.List<Shape> shapes = java.util.List.of(
                new Circle(2.0),
                new Rectangle(3.0, 4.0),
                new Triangle(4.0, 5.0)
        );

        // The SAME loop line works for every shape — dynamic dispatch
        // picks Circle.area / Rectangle.area / Triangle.area at runtime.
        for (Shape s : shapes) {
            System.out.println(s.describe());
        }

        // Reference type vs object type:
        Shape s = new Circle(1.0);
        System.out.println(s instanceof Circle);   // true
        System.out.println(s instanceof Rectangle); // false

        // final on describe(): subclasses cannot override the template,
        // only the abstract piece it calls.
    }
}

/**
 * Expected output:
 *
 * circle has area 12.57
 * rectangle has area 12.00
 * triangle has area 10.00
 * true
 * false
 */
