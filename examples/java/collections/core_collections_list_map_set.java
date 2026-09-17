/**
 * Topic: Java core collections — List, Map and Set in practice.
 *
 * Concepts:
 * - List: ordering, List.of immutables, for-each
 * - Map: put/get, getOrDefault, merging with computeIfPresent
 * - Set: uniqueness (HashSet)
 * - Choosing the right collection for the job
 * - Common idioms: countBy, invert, top-N
 *
 * The decision guide:
 *   ordered, duplicates ok   -> ArrayList
 *   unique elements          -> HashSet
 *   key -> value             -> HashMap
 *   ordered key -> value     -> TreeMap
 *
 * Time Complexity: get/add O(1) average for the hash-based ones.
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class CoreCollections {

    record Order(String customer, String product, int units) {}

    public static void main(String[] args) {
        List<Order> orders = new ArrayList<>(List.of(
                new Order("Acme", "Keyboard", 2),
                new Order("Globex", "Mouse", 5),
                new Order("Acme", "Monitor", 1),
                new Order("Initech", "Mouse", 3)
        ));

        // --- 1. Map: total units per customer --------------------------------
        Map<String, Integer> unitsByCustomer = new HashMap<>();
        for (Order o : orders) {
            // merge: add to existing value, or start at this value.
            unitsByCustomer.merge(o.customer(), o.units(), Integer::sum);
        }
        System.out.println("units by customer: " + unitsByCustomer);
        // -> e.g. {Acme=3, Globex=5, Initech=3}
        // (HashMap print order is unspecified; use TreeMap to sort)

        // getOrDefault: safe read with a fallback (no NPE on missing keys).
        int umbrellas = unitsByCustomer.getOrDefault("Umbrella", 0);
        System.out.println("Umbrella units: " + umbrellas); // -> 0

        // --- 2. Set: unique products, in sorted order -------------------------
        Set<String> products = new java.util.TreeSet<>();
        for (Order o : orders) {
            products.add(o.product());   // duplicates are ignored silently
        }
        System.out.println("distinct products (sorted): " + products);
        // -> [Keyboard, Monitor, Mouse]

        // --- 3. Invert a map: value -> set of keys -----------------------------
        // product -> customers who bought it
        Map<String, Set<String>> customersByProduct = new HashMap<>();
        for (Order o : orders) {
            customersByProduct
                    .computeIfAbsent(o.product(), k -> new java.util.TreeSet<>())
                    .add(o.customer());
        }
        System.out.println("customers by product: " + customersByProduct);
        // -> {Keyboard=[Acme], Mouse=[Globex, Initech], Monitor=[Acme]}

        // --- 4. TreeMap: ordered entries for reporting ---------------------------
        Map<String, Integer> sortedUnits = new TreeMap<>(unitsByCustomer);
        System.out.println("sorted: " + sortedUnits);
        // -> {Acme=3, Globex=5, Initech=3}

        // --- 5. Immutability: List.of / Map.of reject modifications ---------------
        List<String> frozen = List.of("a", "b", "c");
        // frozen.add("d");      // would throw UnsupportedOperationException
        // frozen.set(0, "z");   // same
        System.out.println("frozen list: " + frozen);

        // A safe pattern: wrap a mutable list in an unmodifiable view.
        List<String> mutable = new ArrayList<>(List.of("x", "y"));
        List<String> view = List.copyOf(mutable); // defensive copy, immutable
        System.out.println("copyOf: " + view);

        // --- 6. contains / membership ---------------------------------------------
        System.out.println("has Globex: " + unitsByCustomer.containsKey("Globex"));
        System.out.println("has Umbrella: " + unitsByCustomer.containsKey("Umbrella"));
        // -> true / false
    }
}

/**
 * Expected output:
 *
 * units by customer: {Acme=3, Globex=5, Initech=3}
 * Umbrella units: 0
 * distinct products (sorted): [Keyboard, Monitor, Mouse]
 * customers by product: {Keyboard=[Acme], Mouse=[Globex, Initech], Monitor=[Acme]}
 * sorted: {Acme=3, Globex=5, Initech=3}
 * frozen list: [a, b, c]
 * copyOf: [x, y]
 * has Globex: true
 * has Umbrella: false
 */
