/**
 * Topic: Interfaces beyond abstract methods - default, static, functional.
 *
 * Java 8 changed what an interface is. It can now carry implementation
 * (default methods), utility code (static methods), and -- if it declares
 * exactly one abstract method -- it can be implemented by a lambda.
 *
 * Concepts:
 * - default methods, and why they exist (evolving an interface without
 *   breaking every existing implementer)
 * - static methods on an interface, as a home for related helpers
 * - private interface methods (Java 9+) to share code between defaults
 * - Functional interfaces, @FunctionalInterface, and lambdas
 * - The built-in ones: Function, Predicate, Supplier, Consumer, Comparator
 * - The diamond problem, and the compiler rule that resolves it
 * - abstract class vs interface: when to pick which
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

class DefaultAndFunctionalInterfaces {

    // -----------------------------------------------------------------------
    // 1. default and static methods
    // -----------------------------------------------------------------------

    interface Vehicle {
        String name();          // abstract: implementers must provide it
        int wheels();

        // A DEFAULT method has a body. Adding one to a published interface
        // does NOT break existing implementers -- which is exactly why
        // Collection could gain stream() in Java 8 without breaking the world.
        default String describe() {
            return name() + " with " + wheels() + " wheels" + sizeLabel();
        }

        // A PRIVATE method (Java 9+) lets defaults share code without
        // exposing it as part of the interface.
        private String sizeLabel() {
            return wheels() > 4 ? " (large)" : "";
        }

        // A STATIC method belongs to the interface, not to instances.
        // It is NOT inherited by implementers - call it as Vehicle.compare(...).
        static Comparator<Vehicle> byWheels() {
            return Comparator.comparingInt(Vehicle::wheels)
                             .thenComparing(Vehicle::name);
        }
    }

    record Car(String name) implements Vehicle {
        public int wheels() { return 4; }
    }

    record Lorry(String name) implements Vehicle {
        public int wheels() { return 6; }
        // Overriding a default is allowed, and normal.
        @Override
        public String describe() {
            return "HGV " + name() + " (" + wheels() + " wheels)";
        }
    }

    record Bike(String name) implements Vehicle {
        public int wheels() { return 2; }
    }

    // -----------------------------------------------------------------------
    // 2. The diamond problem
    // -----------------------------------------------------------------------

    interface Swimmer {
        default String move() { return "swimming"; }
    }

    interface Runner {
        default String move() { return "running"; }
    }

    // Inheriting two defaults with the same signature is a COMPILE ERROR
    // unless the class resolves it explicitly. Java will not guess.
    static class Triathlete implements Swimmer, Runner {
        @Override
        public String move() {
            // Interface.super.method() picks a specific one.
            return Swimmer.super.move() + " then " + Runner.super.move();
        }
    }

    // -----------------------------------------------------------------------
    // 3. Functional interfaces
    // -----------------------------------------------------------------------

    // Exactly one abstract method => a lambda can implement it.
    // @FunctionalInterface is optional but makes the compiler enforce that,
    // so a later edit cannot silently break every lambda at the call site.
    @FunctionalInterface
    interface Validator<T> {
        String validate(T value);      // returns null when valid

        // Defaults can COMBINE validators - this is how Predicate.and works.
        default Validator<T> and(Validator<T> next) {
            return value -> {
                String problem = this.validate(value);
                return problem != null ? problem : next.validate(value);
            };
        }

        static <T> Validator<T> alwaysValid() {
            return value -> null;
        }
    }

    public static void main(String[] args) {
        List<Vehicle> fleet = new ArrayList<>(List.of(
            new Car("Corolla"), new Lorry("Scania"), new Bike("Brompton")));

        System.out.println("-- default methods --");
        for (Vehicle vehicle : fleet) {
            System.out.println("  " + vehicle.describe());
        }

        System.out.println("-- static method on the interface --");
        fleet.sort(Vehicle.byWheels());
        for (Vehicle vehicle : fleet) {
            System.out.println("  " + vehicle.wheels() + " " + vehicle.name());
        }

        System.out.println("-- diamond resolved explicitly --");
        System.out.println("  " + new Triathlete().move());

        System.out.println("-- lambdas implement functional interfaces --");
        Validator<String> notBlank =
            value -> (value == null || value.isBlank()) ? "must not be blank" : null;
        Validator<String> maxLength =
            value -> value.length() > 10 ? "must be 10 characters or fewer" : null;

        // and() is a DEFAULT method, so combining is free.
        Validator<String> rules = notBlank.and(maxLength);

        for (String candidate : new String[] {"ada", "", "a-very-long-name"}) {
            String problem = rules.validate(candidate);
            System.out.printf("  %-18s -> %s%n",
                "\"" + candidate + "\"",
                problem == null ? "valid" : problem);
        }
        System.out.println("  alwaysValid: " + Validator.alwaysValid().validate("anything"));

        System.out.println("-- the built-in functional interfaces --");
        Function<Integer, Integer> square = n -> n * n;
        Predicate<Integer> isEven = n -> n % 2 == 0;
        Supplier<String> now = () -> "a supplied value";
        Consumer<String> printer = value -> System.out.println("  consumed: " + value);
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;

        System.out.println("  Function  square(7)      = " + square.apply(7));
        System.out.println("  Predicate isEven(7)      = " + isEven.test(7));
        System.out.println("  Predicate negate         = " + isEven.negate().test(7));
        System.out.println("  Supplier  get()          = " + now.get());
        System.out.println("  BiFunction add(3, 4)     = " + add.apply(3, 4));
        printer.accept("hello");

        // Composition, again via default methods on the built-in interfaces.
        Function<Integer, Integer> squareThenDouble = square.andThen(n -> n * 2);
        Function<Integer, Integer> doubleThenSquare = square.compose(n -> n * 2);
        System.out.println("  andThen(5): " + squareThenDouble.apply(5) + "  (square, then double)");
        System.out.println("  compose(5): " + doubleThenSquare.apply(5) + "  (double, then square)");

        System.out.println("-- interface or abstract class? --");
        // Interface       : a CAPABILITY many unrelated types can have, and a
        //                   type may have several. No state.
        // Abstract class  : shared STATE plus partial implementation for a
        //                   family of closely related types. Only one allowed.
        System.out.println("  interface: capability, multiple, no fields");
        System.out.println("  abstract class: shared state, single, constructors");
    }
}

/* Expected output:
-- default methods --
  Corolla with 4 wheels
  HGV Scania (6 wheels)
  Brompton with 2 wheels
-- static method on the interface --
  2 Brompton
  4 Corolla
  6 Scania
-- diamond resolved explicitly --
  swimming then running
-- lambdas implement functional interfaces --
  "ada"              -> valid
  ""                 -> must not be blank
  "a-very-long-name" -> must be 10 characters or fewer
  alwaysValid: null
-- the built-in functional interfaces --
  Function  square(7)      = 49
  Predicate isEven(7)      = false
  Predicate negate         = true
  Supplier  get()          = a supplied value
  BiFunction add(3, 4)     = 7
  consumed: hello
  andThen(5): 50  (square, then double)
  compose(5): 100  (double, then square)
*/
