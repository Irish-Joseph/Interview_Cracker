/**
 * Topic: Java String immutability and StringBuilder.
 *
 * Concepts:
 * - Strings are immutable: every "change" makes a NEW object
 * - The hidden cost of string concatenation in loops
 * - StringBuilder for efficient mutation
 * - Common operations: substring, split, replace, trim, case
 * - String pools: why "a" == "a" but new String("a") != "a"
 *
 * Rule of thumb:
 *   read/compare/concat few times  -> String
 *   build up in a loop             -> StringBuilder
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
public class StringImmutability {

    public static void main(String[] args) {
        // --- 1. Immutability: "changes" create new strings ------------------
        String s = "hello";
        String s2 = s + " world";   // s is UNCHANGED; s2 is a new String
        System.out.println("s  = " + s);    // -> hello
        System.out.println("s2 = " + s2);   // -> hello world

        // A method that "modifies" a String cannot actually touch it:
        String original = "abc";
        original = original.toUpperCase();  // reassigns a NEW string
        System.out.println("original = " + original); // -> ABC

        // --- 2. The cost of += in a loop ------------------------------------
        // Each += compiles to a NEW StringBuilder copy internally:
        // O(n^2) total work for n appends. The classic performance bug.
        int n = 20_000;

        long t0 = System.nanoTime();
        String slow = "";
        for (int i = 0; i < n; i++) {
            slow += "x";
        }
        long t1 = System.nanoTime();

        StringBuilder fast = new StringBuilder(n); // pre-size!
        for (int i = 0; i < n; i++) {
            fast.append('x');
        }
        long t2 = System.nanoTime();

        System.out.printf("String  += 20k times: %6d ms%n",
                (t1 - t0) / 1_000_000);
        System.out.printf("StringBuilder:        %6d ms%n",
                (t2 - t1) / 1_000_000);
        // StringBuilder wins by orders of magnitude.

        // --- 3. StringBuilder: the mutation workhorse --------------------------
        StringBuilder sb = new StringBuilder();
        sb.append("a").append(1).append(true);  // mixed types
        sb.insert(0, "A-");                     // insert anywhere
        sb.deleteCharAt(0);                      // delete one char
        sb.replace(1, 2, "B");                   // replace a range
        System.out.println("sb = " + sb);
        // -> sb = AB1true

        // Reverse, a bonus:
        System.out.println("reversed: " + new StringBuilder("abcde").reverse());
        // -> reversed: edcba

        // --- 4. Everyday String operations ----------------------------------------
        String path = "/var/log/app/server.log";
        String name = path.substring(path.lastIndexOf('/') + 1);
        System.out.println("file name: " + name);          // -> server.log

        String csv = "alpha,beta,,gamma";
        String[] parts = csv.split(",");
        System.out.println("parts: " + java.util.Arrays.toString(parts));
        // -> parts: [alpha, beta, , gamma]

        String messy = "  spaced   out  ";
        System.out.println("trimmed: [" + messy.trim() + "]");
        // -> trimmed: [spaced   out]   (outer whitespace only)

        String url = "https://shop.example.com/items?x=1";
        System.out.println(url.replace("http://", "https://"));
        // -> https://shop.example.com/items?x=1 (no change; already https)
        System.out.println("up: " + "MixedCase".toUpperCase());
        System.out.println("down: " + "MixedCase".toLowerCase());

        // --- 5. Equality: == vs equals() ----------------------------------------------
        String a = "java";
        String b = "java";                    // from the string pool
        String c = new String("java");        // a fresh object
        System.out.println("a == b:  " + (a == b));     // true  (same pool object)
        System.out.println("a == c:  " + (a == c));     // false (different objects)
        System.out.println("a.equals(c): " + a.equals(c)); // true  (same content)
        // ALWAYS use .equals() for content comparison of Strings.

        // null-safety helper:
        System.out.println(
                java.util.Objects.equals(null, "x"));   // false, no NPE
    }
}

/**
 * Expected output (timings vary by machine):
 *
 * s  = hello
 * s2 = hello world
 * original = ABC
 * String  += 20k times:  several hundred ms
 * StringBuilder:        1-5 ms
 * sb = AB1true
 * reversed: edcba
 * file name: server.log
 * parts: [alpha, beta, , gamma]
 * trimmed: [spaced   out]
 * https://shop.example.com/items?x=1
 * up: MIXEDCASE
 * down: mixedcase
 * a == b:  true
 * a == c:  false
 * a.equals(c): true
 * false
 */
