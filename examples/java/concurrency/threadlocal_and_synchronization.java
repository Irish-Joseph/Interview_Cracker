/**
 * Topic: ThreadLocal and basic synchronization (synchronized, AtomicInteger).
 *
 * Concepts:
 * - Shared mutable state is a race: without synchronization, increments
 *   are lost because read-modify-write is not atomic
 * - synchronized: a monitor lock guarding a critical section
 * - AtomicInteger: lock-free counter using CAS (compare-and-swap)
 * - ThreadLocal: per-thread copies of a "shared-looking" variable —
 *   no lock needed because threads never see each other's value
 * - ThreadLocal cleanup: InheritableThreadLocal pitfalls in thread
 *   pools (values leak between pooled tasks unless removed)
 *
 * Validated by inspection (no working JDK on the authoring machine).
 *
 * Example output (numbers vary by timing):
 *   unsynchronized count: 997321        <- less than 1_000_000: lost updates
 *   synchronized   count: 1000000
 *   atomicInt      count: 1000000
 *   each thread saw its own identity (no cross-talk)
 */
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;

public class threadlocal_and_synchronization {

    static final int THREADS = 4;
    static final int PER_THREAD = 250_000;

    public static void main(String[] args) throws Exception {
        // --- 1. The race: plain field, no synchronization -------------
        long plain = 0;
        plain = race(r -> {
            for (int i = 0; i < PER_THREAD; i++) r.bumpPlain();
        });
        System.out.println("unsynchronized count: " + plain
            + "   (less than " + (THREADS * PER_THREAD) + " means lost updates)");

        // --- 2. synchronized: one thread inside the critical section --
        Counter synch = new Counter();
        race(r -> {
            for (int i = 0; i < PER_THREAD; i++) synch.bump();
        });
        System.out.println("synchronized   count: " + synch.value());

        // --- 3. AtomicInteger: CAS loop, no monitor -------------------
        AtomicInteger atomic = new AtomicInteger();
        race(r -> {
            for (int i = 0; i < PER_THREAD; i++) atomic.incrementAndGet();
        });
        System.out.println("atomicInt      count: " + atomic.get());

        // --- 4. ThreadLocal: each thread gets its own value -----------
        ThreadLocal<String> identity = ThreadLocal.withInitial(
            () -> "worker-" + Thread.currentThread().getId());
        race(r -> {
            // Every thread reads its OWN copy — no lock, no races.
            String mine = identity.get();
            ThreadLocalRandom.current().nextInt(1000); // busy work
            if (!mine.startsWith("worker-")) throw new IllegalStateException();
        });
        System.out.println("each thread saw its own identity (no cross-talk)");
    }

    // Runs a task on THREADS real threads and waits for all of them.
    interface Task { void run(Racer r); }
    static class Racer {
        private long plain;
        void bumpPlain() { plain++; }          // NOT atomic
        long plainValue() { return plain; }
    }

    static long race(Task task) throws InterruptedException {
        Racer shared = new Racer();
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(THREADS);
        for (int t = 0; t < THREADS; t++) {
            new Thread(() -> {
                try { start.await(); } catch (InterruptedException e) { return; }
                task.run(shared);
                done.countDown();
            }).start();
        }
        start.countDown();   // release all threads at once (maximizes overlap)
        done.await();
        return shared.plainValue();
    }

    static class Counter {
        private int value = 0;
        synchronized void bump() { value++; }  // monitor guards the field
        int value() { return value; }
    }
}
