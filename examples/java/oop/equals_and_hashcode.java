/**
 * Topic: equals and hashCode - the contract, and what breaks without it.
 *
 * Override one and you must override the other. Get it wrong and hash-based
 * collections fail SILENTLY: the object is in the set, but the set says no.
 *
 * The contract:
 *   1. If a.equals(b) then a.hashCode() == b.hashCode().   (Required.)
 *   2. Equal hash codes do NOT imply equality - that is just a collision.
 *   3. equals must be reflexive, symmetric, transitive and consistent.
 *   4. x.equals(null) must be false, never a NullPointerException.
 *   5. A key's hash must not change while it is inside a collection.
 *
 * Concepts:
 * - Why HashMap.get returns null for an "equal" key with no hashCode override
 * - Objects.equals / Objects.hash for null-safe, concise implementations
 * - Why mutable keys strand entries so even remove() cannot find them
 * - Records generate a correct implementation for you
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

class EqualsAndHashcode {

    /** BROKEN: overrides equals but not hashCode. */
    static final class BadPoint {
        private final int x;
        private final int y;

        BadPoint(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object other) {
            if (this == other) {
                return true;
            }
            if (!(other instanceof BadPoint)) {
                return false;
            }
            BadPoint that = (BadPoint) other;
            return x == that.x && y == that.y;
        }
        // No hashCode() -> inherits Object's identity hash, so two equal
        // BadPoints almost certainly land in DIFFERENT buckets.
    }

    /** CORRECT: equals and hashCode derived from the same fields. */
    static final class Point {
        private final int x;
        private final int y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object other) {
            if (this == other) {
                return true;              // cheap identity short-circuit
            }
            // instanceof handles null too: null instanceof X is always false,
            // which satisfies rule 4 without an explicit null check.
            if (!(other instanceof Point)) {
                return false;
            }
            Point that = (Point) other;
            return x == that.x && y == that.y;
        }

        @Override
        public int hashCode() {
            return Objects.hash(x, y);    // same fields as equals, always
        }

        @Override
        public String toString() {
            return "Point(" + x + ", " + y + ")";
        }
    }

    /** DANGEROUS: a mutable field feeds hashCode. */
    static final class MutableKey {
        String name;

        MutableKey(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof MutableKey
                && Objects.equals(name, ((MutableKey) other).name);
        }

        @Override
        public int hashCode() {
            return Objects.hashCode(name);   // null-safe, unlike name.hashCode()
        }
    }

    /** A record generates equals, hashCode and toString from its components. */
    record Pixel(int x, int y, String colour) {}

    public static void main(String[] args) {
        System.out.println("-- the silent failure --");
        Map<BadPoint, String> broken = new HashMap<>();
        broken.put(new BadPoint(1, 2), "origin-ish");
        BadPoint lookup = new BadPoint(1, 2);
        System.out.println("  equals says:   " + broken.keySet().iterator().next().equals(lookup));
        System.out.println("  HashMap says:  " + broken.get(lookup));
        System.out.println("  containsKey:   " + broken.containsKey(lookup));
        // equals is true, yet the map cannot find it: get() hashes the key to
        // pick a bucket, and the two objects hash to different buckets.

        System.out.println("-- correct implementation --");
        Map<Point, String> working = new HashMap<>();
        working.put(new Point(1, 2), "origin-ish");
        System.out.println("  HashMap says:  " + working.get(new Point(1, 2)));

        Set<Point> points = new HashSet<>();
        points.add(new Point(0, 0));
        points.add(new Point(0, 0));     // duplicate by value
        points.add(new Point(1, 1));
        System.out.println("  set size:      " + points.size() + " (duplicate collapsed)");

        System.out.println("-- the contract, checked --");
        Point a = new Point(3, 4);
        Point b = new Point(3, 4);
        System.out.println("  reflexive:  " + a.equals(a));
        System.out.println("  symmetric:  " + (a.equals(b) == b.equals(a)));
        System.out.println("  hashes match: " + (a.hashCode() == b.hashCode()));
        System.out.println("  null-safe:  " + a.equals(null));
        System.out.println("  other type: " + a.equals("not a point"));

        System.out.println("-- mutating a key strands it --");
        Set<MutableKey> keys = new HashSet<>();
        MutableKey key = new MutableKey("alpha");
        keys.add(key);
        System.out.println("  found before mutation: " + keys.contains(key));
        key.name = "beta";               // the hash changes; the bucket does not
        System.out.println("  found after mutation:  " + keys.contains(key));
        System.out.println("  remove() succeeds:     " + keys.remove(key));
        System.out.println("  but size is still:     " + keys.size() + " (leaked)");

        System.out.println("-- records do it for you --");
        Pixel p1 = new Pixel(1, 2, "red");
        Pixel p2 = new Pixel(1, 2, "red");
        System.out.println("  " + p1);
        System.out.println("  equal:        " + p1.equals(p2));
        System.out.println("  hashes match: " + (p1.hashCode() == p2.hashCode()));
    }
}

/* Expected output:
-- the silent failure --
  equals says:   true
  HashMap says:  null
  containsKey:   false
-- correct implementation --
  HashMap says:  origin-ish
  set size:      2 (duplicate collapsed)
-- the contract, checked --
  reflexive:  true
  symmetric:  true
  hashes match: true
  null-safe:  false
  other type: false
-- mutating a key strands it --
  found before mutation: true
  found after mutation:  false
  remove() succeeds:     false
  but size is still:     1 (leaked)
-- records do it for you --
  Pixel[x=1, y=2, colour=red]
  equal:        true
  hashes match: true
*/
