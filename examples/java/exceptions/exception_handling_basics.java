/**
 * Topic: Exception handling — checked vs unchecked, try/catch/finally,
 *        and writing your own exception types.
 *
 * Concepts:
 * - Checked exceptions (must declare or handle) vs unchecked (RuntimeException)
 * - try / catch (multiple) / finally: execution order
 * - try-with-resources: auto-closing Closeable objects
 * - Custom exception hierarchy
 * - Rethrowing with cause chaining
 *
 * The mental model: exceptions unwind the stack until a handler
 * matches. `finally` runs on EVERY path (return or throw).
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.NoSuchElementException;

public class ExceptionHandling {

    // --- A custom CHECKED exception (extends Exception) -------------------
    // Checked: callers MUST handle or declare it. Use for
    // *recoverable* conditions the caller can realistically fix.

    static class InsufficientFundsException extends Exception {
        private final double shortfall;

        InsufficientFundsException(double shortfall) {
            super("shortfall of " + shortfall);
            this.shortfall = shortfall;
        }

        double getShortfall() {
            return shortfall;
        }
    }

    // --- A custom UNCHECKED exception (extends RuntimeException) -----------
    // Unchecked: no obligation to catch. Use for *programming errors*
    // that should never happen if the code is correct.

    static class NegativeAmountException extends RuntimeException {
        NegativeAmountException(double amount) {
            super("amount cannot be negative: " + amount);
        }
    }

    /**
     * Withdrawal: validates input (unchecked) then checks balance
     * (checked). Demonstrates cause chaining.
     */
    static double withdraw(double balance, double amount)
            throws InsufficientFundsException {

        if (amount < 0) {
            // Programming error -> unchecked
            throw new NegativeAmountException(amount);
        }
        if (amount > balance) {
            // Recoverable business condition -> checked
            double shortfall = amount - balance;
            throw new InsufficientFundsException(shortfall);
        }
        return balance - amount;
    }

    /**
     * Reads the first line of a StringReader with try-with-resources.
     * The reader is closed automatically — even when an exception
     * is thrown inside the try block.
     */
    static String firstLine(String text) {
        String result = "<no lines>";
        try (BufferedReader reader =
                 new BufferedReader(new StringReader(text))) {
            String line = reader.readLine();
            result = (line == null) ? "<no lines>" : line;
        } catch (IOException e) {
            // StringReader never throws, but the checked signature
            // forces us to decide: wrap it in an unchecked exception,
            // PRESERVING the original cause.
            throw new RuntimeException("read failed", e);
        }
        return result;
    }

    public static void main(String[] args) {
        // --- 1. Happy path ---------------------------------------------------
        try {
            double after = withdraw(100.0, 30.0);
            System.out.println("balance after withdrawal: " + after);
        } catch (InsufficientFundsException e) {
            System.out.println("unexpected: " + e);
        }
        // -> balance after withdrawal: 70.0

        // --- 2. Checked exception: specific catch, finally always runs -------
        try {
            withdraw(50.0, 80.0);
        } catch (InsufficientFundsException e) {
            System.out.println("caught checked: " + e.getMessage()
                    + " (shortfall=" + e.getShortfall() + ")");
        } finally {
            System.out.println("finally ran (auditing the attempt)");
        }
        // -> caught checked: shortfall of 30.0 (shortfall=30.0)
        // -> finally ran (auditing the attempt)

        // --- 3. Unchecked exception: no catch required, catch optional -------
        try {
            withdraw(50.0, -5.0);
        } catch (NegativeAmountException e) {
            System.out.println("caught unchecked: " + e.getMessage());
        }
        // -> caught unchecked: amount cannot be negative: -5.0

        // --- 4. Multiple catch clauses: most specific first -------------------
        try {
            throw new NoSuchElementException("demo");
        } catch (IllegalStateException e) {
            System.out.println("wrong branch: " + e);
        } catch (NoSuchElementException e) {
            System.out.println("caught: " + e.getMessage());
        } catch (RuntimeException e) {
            System.out.println("generic branch: " + e);
        }
        // -> caught: demo
        // (Order matters: a broad catch BEFORE a specific one would
        //  make the specific one unreachable — a compile error.)

        // --- 5. try-with-resources: closed automatically ----------------------
        System.out.println("first line: " + firstLine("hello\nworld"));
        // -> first line: hello
    }
}

/**
 * Expected output:
 *
 * balance after withdrawal: 70.0
 * caught checked: shortfall of 30.0 (shortfall=30.0)
 * finally ran (auditing the attempt)
 * caught unchecked: amount cannot be negative: -5.0
 * caught: demo
 * first line: hello
 */
