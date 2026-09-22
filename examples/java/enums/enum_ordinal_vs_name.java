/**
 * Topic: enum constants, and why ordinal() is a source-order detail, not data
 *
 * Concepts:
 *   - ordinal(): the 0-based position in the source. It is NOT stable:
 *     inserting a constant between two others shifts every later ordinal.
 *     Never persist, serialize to disk, or index arrays by ordinal across
 *     versions - Java's own serialization of enums stores the ordinal and
 *     rejects a mismatch.
 *   - name(): the exact identifier from the source. Stable across versions.
 *   - toString(): defaults to name(), but is overridable per constant -
 *     display text belongs here, identity belongs in name().
 *   - values() / valueOf("NAME") are the safe round-trip.
 *   - switch on an enum: exhaustive, and the compiler warns on missing cases
 *     (with a pattern-matching preview it can require them).
 *
 * NOTE: validated by inspection (no JDK on this host); the expected output
 * below was also computed by simulating the enum semantics in Python.
 *
 * Compile: javac EnumOrdinalVsName.java
 * Run:     java EnumOrdinalVsName
 */
public class EnumOrdinalVsName {

    enum StatusV1 { PENDING, ACTIVE, CLOSED }

    // Version two: ARCHIVED was inserted in the middle. Every constant after
    // it has a different ordinal than in v1. Nothing changed for ACTIVE or
    // CLOSED as far as the compiler or valueOf is concerned - but arrays and
    // databases that stored "1" for ACTIVE now read the wrong row.
    enum StatusV2 { PENDING, ARCHIVED, ACTIVE, CLOSED }

    enum Named {
        FIRST { @Override public String toString() { return "First!"; } },
        SECOND
    }

    public static void main(String[] args) {
        System.out.println("v1 = " + java.util.Arrays.toString(StatusV1.values()));
        System.out.println("v2 = " + java.util.Arrays.toString(StatusV2.values()));
        System.out.println("ACTIVE.ordinal in v1 = " + StatusV1.ACTIVE.ordinal());
        System.out.println("ACTIVE.ordinal in v2 = " + StatusV2.ACTIVE.ordinal());
        System.out.println("valueOf(\"ACTIVE\").name() = " + StatusV2.valueOf("ACTIVE").name());
        System.out.println("Named.FIRST.name()     = " + Named.FIRST.name());
        System.out.println("Named.FIRST.toString() = " + Named.FIRST.toString());

        // The tempting use of ordinal: a parallel array. It works until the
        // next version inserts a constant - the array silently desyncs.
        String[] labels = {"pending", "archived", "active", "closed"};
        System.out.println("labels[ACTIVE.ordinal()] = " + labels[StatusV2.ACTIVE.ordinal()]);

        for (StatusV2 s : StatusV2.values()) {
            switch (s) {
                case PENDING:  System.out.println("switch: " + s + " -> still waiting"); break;
                case ACTIVE:   System.out.println("switch: " + s + " -> running"); break;
                case ARCHIVED: System.out.println("switch: " + s + " -> cold storage"); break;
                case CLOSED:   System.out.println("switch: " + s + " -> done"); break;
            }
        }
    }
}

/*
Expected output:

v1 = [PENDING, ACTIVE, CLOSED]
v2 = [PENDING, ARCHIVED, ACTIVE, CLOSED]
ACTIVE.ordinal in v1 = 1
ACTIVE.ordinal in v2 = 2
valueOf("ACTIVE").name() = ACTIVE
Named.FIRST.name()     = FIRST
Named.FIRST.toString() = First!
labels[ACTIVE.ordinal()] = active
switch: PENDING -> still waiting
switch: ARCHIVED -> cold storage
switch: ACTIVE -> running
switch: CLOSED -> done
*/
