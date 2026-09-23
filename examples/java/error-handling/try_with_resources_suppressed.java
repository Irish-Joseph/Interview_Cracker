/*
Topic: try-with-resources and suppressed exceptions.
Concepts: AutoCloseable, reverse close order, preserving the primary failure.
Run: javac try_with_resources_suppressed.java && java try_with_resources_suppressed
NOTE: validated by inspection (the installed javac launcher fails on this host).
Expected output:
primary: work failed
suppressed: close second
suppressed: close first
*/

class try_with_resources_suppressed {
    static final class Resource implements AutoCloseable {
        private final String name;

        Resource(String name) {
            this.name = name;
        }

        void work() {
            throw new IllegalStateException("work failed");
        }

        @Override
        public void close() {
            throw new IllegalStateException("close " + name);
        }
    }

    public static void main(String[] args) {
        try (Resource first = new Resource("first");
             Resource second = new Resource("second")) {
            first.work();
        } catch (IllegalStateException error) {
            // The work failure stays primary. Close failures are attached in
            // reverse declaration order instead of replacing useful context.
            System.out.println("primary: " + error.getMessage());
            for (Throwable suppressed : error.getSuppressed()) {
                System.out.println("suppressed: " + suppressed.getMessage());
            }

            assert error.getMessage().equals("work failed");
            assert error.getSuppressed().length == 2;
        }
    }
}
