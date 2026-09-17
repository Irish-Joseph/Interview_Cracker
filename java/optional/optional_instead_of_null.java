/**
 * Topic: Optional<T> - modelling "maybe absent" without returning null.
 *
 * Returning null forces every caller to remember a null check; forgetting one
 * produces a NullPointerException far away from the method that caused it.
 * Optional makes absence part of the return type, so the compiler puts the
 * question in front of the caller.
 *
 * Concepts:
 * - Optional.of / ofNullable / empty, and why of(null) throws
 * - map, flatMap and filter: transform without unwrapping
 * - orElse vs orElseGet vs orElseThrow (and the eager-evaluation trap)
 * - ifPresent / ifPresentOrElse instead of isPresent() + get()
 * - Optional in streams
 * - Where Optional does NOT belong: fields and method parameters
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.util.List;
import java.util.Map;
import java.util.Optional;

class OptionalInsteadOfNull {

    record Address(String city, String postcode) {}

    record User(String name, String email, Address address) {
        // Accessors that may legitimately have nothing to return advertise it.
        Optional<Address> maybeAddress() {
            return Optional.ofNullable(address);
        }
    }

    private static final Map<Integer, User> USERS = Map.of(
        1, new User("Ada", "ada@example.com", new Address("London", "NW1 2DB")),
        2, new User("Grace", null, new Address("Arlington", null)),
        3, new User("Alan", "alan@example.com", null)
    );

    // -----------------------------------------------------------------------
    // 1. Creating an Optional
    // -----------------------------------------------------------------------

    static Optional<User> findUser(int id) {
        // Map.get returns null for a missing key; ofNullable adapts that to
        // an Optional. Optional.of(null) would throw NullPointerException,
        // which is the point: of() means "I know this is present".
        return Optional.ofNullable(USERS.get(id));
    }

    // -----------------------------------------------------------------------
    // 2. map / flatMap / filter - chain without unwrapping
    // -----------------------------------------------------------------------

    /** map applies a function to the value if present, else stays empty. */
    static Optional<String> emailDomain(int id) {
        return findUser(id)
            .map(User::email)              // email may be null -> map yields empty
            .filter(email -> email.contains("@"))
            .map(email -> email.substring(email.indexOf('@') + 1));
    }

    /**
     * flatMap is for functions that already return an Optional. Using map here
     * would produce Optional<Optional<Address>>.
     */
    static Optional<String> cityOf(int id) {
        return findUser(id)
            .flatMap(User::maybeAddress)
            .map(Address::city);
    }

    // -----------------------------------------------------------------------
    // 3. Getting a value out
    // -----------------------------------------------------------------------

    static String displayCity(int id) {
        // orElse's argument is evaluated even when the Optional is present.
        // With a constant that is harmless; with a method call it is a bug.
        return cityOf(id).orElse("unknown");
    }

    static String displayCityLazily(int id) {
        // orElseGet takes a Supplier, so the fallback is only computed when
        // the Optional is actually empty.
        return cityOf(id).orElseGet(OptionalInsteadOfNull::expensiveDefault);
    }

    static String requireEmailDomain(int id) {
        return emailDomain(id)
            .orElseThrow(() -> new IllegalStateException("no usable email for user " + id));
    }

    private static String expensiveDefault() {
        System.out.println("    (computing the fallback...)");
        return "unknown";
    }

    // -----------------------------------------------------------------------
    // 4. Acting on the value: prefer ifPresent over isPresent() + get()
    // -----------------------------------------------------------------------

    static void report(int id) {
        findUser(id).ifPresentOrElse(
            user -> System.out.println("  found " + user.name()),
            () -> System.out.println("  no user with id " + id)
        );
    }

    // -----------------------------------------------------------------------
    // 5. Optional in streams
    // -----------------------------------------------------------------------

    static List<String> allKnownCities(List<Integer> ids) {
        return ids.stream()
            .map(OptionalInsteadOfNull::cityOf)
            .flatMap(Optional::stream)   // Java 9+: drops the empty ones
            .sorted()
            .toList();
    }

    public static void main(String[] args) {
        System.out.println("-- findUser --");
        report(1);
        report(42);

        System.out.println("-- email domains --");
        for (int id : new int[] {1, 2, 3, 42}) {
            System.out.println("  user " + id + ": " + emailDomain(id));
        }

        System.out.println("-- cities --");
        for (int id : new int[] {1, 2, 3, 42}) {
            System.out.println("  user " + id + ": " + displayCity(id));
        }

        System.out.println("-- orElse vs orElseGet --");
        System.out.println("  present, orElseGet: " + displayCityLazily(1));
        System.out.println("  empty,   orElseGet: " + displayCityLazily(3));

        System.out.println("-- orElseThrow --");
        try {
            requireEmailDomain(2);
        } catch (IllegalStateException error) {
            System.out.println("  " + error.getMessage());
        }

        System.out.println("-- stream --");
        System.out.println("  " + allKnownCities(List.of(1, 2, 3, 42)));

        // Guidance: use Optional as a RETURN type for "might not be there".
        // Do not use it for fields (it is not Serializable and adds a wrapper
        // per instance) or for method parameters (callers then have to wrap
        // every argument); an overload or a plain nullable parameter is clearer.
    }
}

/* Expected output:
-- findUser --
  found Ada
  no user with id 42
-- email domains --
  user 1: Optional[example.com]
  user 2: Optional.empty
  user 3: Optional[example.com]
  user 42: Optional.empty
-- cities --
  user 1: London
  user 2: Arlington
  user 3: unknown
  user 42: unknown
-- orElse vs orElseGet --
  present, orElseGet: London
    (computing the fallback...)
  empty,   orElseGet: unknown
-- orElseThrow --
  no usable email for user 2
-- stream --
  [Arlington, London]
*/
