/**
 * Topic: Java generics — type parameters, bounds and wildcards.
 *
 * Concepts:
 * - Generic classes and generic methods (<T> before the return type)
 * - Bounded type parameters: <T extends Comparable<T>>
 * - Wildcards: ? extends T (producer) and ? super T (consumer)
 * - PECS: Producer Extends, Consumer Super
 * - Why List<String> is NOT a List<Object> (generics are invariant)
 * - Type erasure and what it costs you at runtime
 *
 * Generics move type errors from run time to compile time and delete the
 * casts that used to litter pre-2004 Java. The compiler checks them, then
 * ERASES them: at run time a List<String> is just a List.
 *
 * Run (Java 11+, single-file source launcher):
 *     java generic_methods_and_wildcards.java
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

public class GenericMethodsAndWildcards {

    // --- 1. A generic class ------------------------------------------------

    /** A typed box. Without <T> this would hold Object and need casts. */
    static class Box<T> {
        private T value;

        Box(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        void set(T value) {
            this.value = value;
        }

        /** A generic METHOD inside a generic class: R is independent of T. */
        <R> Box<R> map(java.util.function.Function<? super T, ? extends R> fn) {
            return new Box<>(fn.apply(value));
        }

        @Override
        public String toString() {
            return "Box(" + value + ")";
        }
    }

    // --- 2. Generic methods and bounds --------------------------------------

    /**
     * The <T> before the return type declares a method-level type parameter.
     * `extends Comparable<T>` is a BOUND: it promises T can be compared, so
     * compareTo is available inside the method.
     */
    static <T extends Comparable<T>> T maxOf(List<T> items) {
        if (items.isEmpty()) {
            throw new IllegalArgumentException("empty list has no maximum");
        }
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }

    /** Multiple bounds: T must be both a Number and Comparable. */
    static <T extends Number & Comparable<T>> T clamp(T value, T low, T high) {
        if (value.compareTo(low) < 0) {
            return low;
        }
        return value.compareTo(high) > 0 ? high : value;
    }

    // --- 3. PECS: producer extends -----------------------------------------

    /**
     * `? extends Number` means "some unknown subtype of Number". The list
     * PRODUCES numbers we can read, so sum() accepts List<Integer>,
     * List<Double>, List<Number> — anything Number-ish.
     *
     * The trade-off: you cannot ADD to a `? extends` collection (except
     * null), because the compiler does not know which subtype it holds.
     */
    static double sum(Collection<? extends Number> numbers) {
        double total = 0;
        for (Number n : numbers) {
            total += n.doubleValue();
        }
        return total;
    }

    // --- 4. PECS: consumer super -------------------------------------------

    /**
     * `? super Integer` means "Integer or any supertype". The list CONSUMES
     * the integers we write into it, so a List<Number> or List<Object> is
     * a valid destination.
     *
     * The trade-off: reading gives you Object, since the element type could
     * be anything above Integer.
     */
    static void addSquares(List<? super Integer> destination, int upTo) {
        for (int i = 1; i <= upTo; i++) {
            destination.add(i * i);
        }
    }

    /** Both wildcards at once — exactly how Collections.copy is declared. */
    static <T> void copyAll(List<? extends T> source, List<? super T> destination) {
        for (T item : source) {
            destination.add(item);
        }
    }

    public static void main(String[] args) {
        // --- Generic class ---
        Box<String> nameBox = new Box<>("ada");
        Box<Integer> lengthBox = nameBox.map(String::length);
        System.out.println("1. box:        " + nameBox + " -> " + lengthBox);
        // nameBox.set(42);            // compile error: 42 is not a String
        String name = nameBox.get();   // no cast needed
        System.out.println("1. no cast:    " + name.toUpperCase());

        // --- Bounded generic methods ---
        List<String> words = Arrays.asList("delta", "alpha", "omega");
        List<Integer> scores = Arrays.asList(42, 17, 93, 8);
        System.out.println("2. max word:   " + maxOf(words));    // omega
        System.out.println("2. max score:  " + maxOf(scores));   // 93
        System.out.println("2. clamp 120:  " + clamp(120, 0, 100));
        System.out.println("2. clamp -5:   " + clamp(-5, 0, 100));
        // maxOf(Arrays.asList(new Object(), new Object()));
        //   compile error: Object does not implement Comparable

        // --- Producer: ? extends ---
        List<Integer> ints = Arrays.asList(1, 2, 3);
        List<Double> doubles = Arrays.asList(0.5, 1.5);
        System.out.println("3. sum ints:   " + sum(ints));
        System.out.println("3. sum doubles:" + sum(doubles));
        // Without the wildcard, sum(Collection<Number>) would reject BOTH
        // calls: generics are invariant, so List<Integer> is not a
        // List<Number> even though Integer IS a Number.

        // --- Consumer: ? super ---
        List<Number> numbers = new ArrayList<>(List.of(0));
        addSquares(numbers, 4);
        System.out.println("4. squares in a List<Number>: " + numbers);

        List<Object> anything = new ArrayList<>();
        copyAll(words, anything);      // List<String> -> List<Object>
        System.out.println("4. copied into List<Object>:  " + anything);

        // --- Invariance, demonstrated ---
        // List<Object> broken = words;   // compile error, and for good reason:
        //   broken.add(42);              // would smuggle an Integer into
        //   String s = words.get(0);     // a List<String>
        System.out.println("5. invariance keeps List<String> honest");

        // --- Erasure ---
        // At run time both lists have the SAME class: the type argument is
        // gone. That is why you cannot write `new T[]`, call
        // `list instanceof List<String>`, or overload on List<String> vs
        // List<Integer>.
        System.out.println("6. words.getClass():  " + words.getClass().getName());
        System.out.println("6. scores.getClass(): " + scores.getClass().getName());
        System.out.println("6. same class at run time: "
                + words.getClass().equals(scores.getClass()));

        /*
         * Rules of thumb:
         * - Use a type PARAMETER <T> when the same type appears more than once
         *   in the signature; use a WILDCARD when it appears only once.
         * - PECS: read from `? extends`, write to `? super`.
         * - Bound with `extends` whenever the method calls methods on T.
         * - Never mix raw types (List) with generics; they disable checking.
         */
    }
}
