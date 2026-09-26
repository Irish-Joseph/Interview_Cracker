/*
Topic: CompletableFuture composition without blocking worker threads.
Concepts: thenApply vs thenCompose, combining independent work, exception recovery.
Run: javac completable_future_composition.java && java completable_future_composition
NOTE: validated by inspection (the installed javac launcher fails on this host).
Expected output: ADA has 3 orders; fallback=guest
*/

import java.util.concurrent.CompletableFuture;

class completable_future_composition {
    static CompletableFuture<String> findName(int id) {
        return CompletableFuture.completedFuture(id == 1 ? "Ada" : null);
    }

    static CompletableFuture<Integer> countOrders(int id) {
        return CompletableFuture.completedFuture(3);
    }

    public static void main(String[] args) {
        CompletableFuture<String> message = findName(1)
            .thenCompose(name -> {
                if (name == null) {
                    return CompletableFuture.failedFuture(
                        new IllegalArgumentException("missing user"));
                }
                return countOrders(1)
                    .thenApply(count -> name.toUpperCase() + " has " + count + " orders");
            });

        String fallback = findName(99)
            .thenApply(name -> {
                if (name == null) throw new IllegalStateException("not found");
                return name;
            })
            .exceptionally(error -> "guest")
            .join();

        String output = message.join();
        assert output.equals("ADA has 3 orders");
        assert fallback.equals("guest");
        System.out.println(output + "; fallback=" + fallback);
    }
}
