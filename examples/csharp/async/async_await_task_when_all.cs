// Topic: async/await in C# — Task.WhenAll, error policy and cancellation.
//
// Concepts:
// - async/await methods and the async state machine (conceptually)
// - Task.WhenAll: await a BATCH of tasks in parallel
// - Per-task error policy: WhenAll vs allSettled-style handling
// - Task.WhenAny: race tasks (useful for timeouts)
// - CancellationToken for cooperative shutdown
// - The await keyword never blocks a thread
//
// The practical lesson mirrors every other language's async model:
// fan out independent work, gather results, and decide YOUR error
// policy (fail-fast vs collect-all).
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;

public class AsyncAwaitPatterns
{
    /// Simulates a network call of `ms` milliseconds.
    ///
    /// Task.Delay with the token is a CANCELLABLE sleep — unlike
    /// Thread.Sleep, it respects cancellation while waiting.
    static async Task<string> FetchAsync(int id, int ms, CancellationToken ct = default)
    {
        await Task.Delay(ms, ct);
        return $"item-{id}";
    }

    /// A call that always faults — for the error-policy demo.
    static async Task<string> FailingFetchAsync(int ms)
    {
        await Task.Delay(ms);
        throw new InvalidOperationException("500");
    }

    public static async Task Main()
    {
        // --- 1. Sequential await (SLOW for independent calls) ----------------
        var sw = Stopwatch.StartNew();
        var seq = new List<string>();
        for (int i = 1; i <= 3; i++)
        {
            seq.Add(await FetchAsync(i, 100));   // waits for each one
        }
        sw.Stop();
        Console.WriteLine($"sequential: [{string.Join(", ", seq)}] in {sw.ElapsedMilliseconds} ms");
        // -> ~300 ms

        // --- 2. Task.WhenAll: parallel fan-out, fail-fast policy --------------
        sw.Restart();
        var parallel = await Task.WhenAll(
            FetchAsync(1, 100),
            FetchAsync(2, 100),
            FetchAsync(3, 100));
        sw.Stop();
        Console.WriteLine($"parallel:   [{string.Join(", ", parallel)}] in {sw.ElapsedMilliseconds} ms");
        // -> ~100 ms; results preserve input order

        // --- 3. WhenAll fails fast: ONE bad task rejects the whole batch ------
        try
        {
            await Task.WhenAll(FetchAsync(1, 50), FailingFetchAsync(50));
        }
        catch (InvalidOperationException ex)
        {
            Console.WriteLine($"WhenAll failed fast: {ex.Message}");
            // -> 500
        }

        // --- 4. Collect-all policy: inspect each Task<T> individually ---------
        Task<string>[] mixed =
        {
            FetchAsync(1, 50),
            FailingFetchAsync(50),
            FetchAsync(2, 50),
        };
        // WaitAll blocks until all tasks COMPLETE, but does not throw
        // for faults — exactly what a collect-all policy needs.
        // (await Task.WhenAll(mixed) WOULD throw on the first fault.)
        Task.WaitAll(mixed);

        foreach (var task in mixed)
        {
            try
            {
                Console.WriteLine($"  fulfilled: {task.Result}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  rejected:  {ex.Message}");
            }
        }
        // -> fulfilled: item-1
        //    rejected:  500
        //    fulfilled: item-2

        // --- 5. Task.WhenAny: use a race as a timeout --------------------------
        var work = FetchAsync(1, 300);
        var deadline = Task.Delay(100); // the "timer"

        if (await Task.WhenAny(work, deadline) == work)
        {
            Console.WriteLine($"completed in time: {await work}");
        }
        else
        {
            Console.WriteLine("timed out before completion");
            // -> timed out (work takes 300 ms, deadline 100 ms)
        }

        // --- 6. Cancellation: stop waiting when told ---------------------------
        using var cts = new CancellationTokenSource(50);
        try
        {
            await FetchAsync(1, 300, cts.Token);
        }
        catch (OperationCanceledException)
        {
            Console.WriteLine("canceled: work stopped early");
            // -> canceled
        }
    }
}
