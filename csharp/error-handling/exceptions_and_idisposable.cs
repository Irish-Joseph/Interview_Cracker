// Topic: Exception handling and deterministic cleanup with IDisposable.
//
// Concepts:
// - try / catch / finally, and catching the most specific type first
// - `when` exception filters vs catch-and-rethrow
// - throw; preserves the stack trace, throw ex; destroys it
// - Custom exceptions carrying context
// - IDisposable + using, so cleanup happens even when an exception unwinds
// - Guard clauses with ArgumentNullException.ThrowIfNull
//
// Run:  dotnet run   (requires .NET 7+ for ObjectDisposedException.ThrowIf)
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

#nullable enable

using System;
using System.Collections.Generic;
using System.Globalization;

namespace Learning.ErrorHandling;

// ---------------------------------------------------------------------------
// 1. A custom exception carries the context a caller needs to react
// ---------------------------------------------------------------------------

public class ConfigurationException : Exception
{
    public ConfigurationException(string key, string message, Exception? inner = null)
        : base(message, inner)   // always pass the inner exception along
    {
        Key = key;
    }

    public string Key { get; }
}

// ---------------------------------------------------------------------------
// 2. IDisposable: cleanup that happens no matter how the block is left
// ---------------------------------------------------------------------------

public sealed class ConnectionScope : IDisposable
{
    private readonly string _name;
    private bool _disposed;

    public ConnectionScope(string name)
    {
        _name = name;
        Console.WriteLine($"  open {_name}");
    }

    public void Run(string statement)
    {
        // Using a disposed object is a bug in the caller, so it throws.
        ObjectDisposedException.ThrowIf(_disposed, this);
        Console.WriteLine($"  run {statement} on {_name}");

        if (statement.Contains("DROP", StringComparison.Ordinal))
        {
            throw new InvalidOperationException($"refusing to run: {statement}");
        }
    }

    // Dispose must be safe to call more than once.
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }
        _disposed = true;
        Console.WriteLine($"  close {_name}");
    }
}

public static class Program
{
    // -----------------------------------------------------------------------
    // 3. Order matters: the first matching catch wins
    // -----------------------------------------------------------------------

    private static int ParsePort(string raw)
    {
        // Guard clauses fail fast, at the boundary, with a clear message.
        ArgumentNullException.ThrowIfNull(raw);

        try
        {
            return int.Parse(raw, CultureInfo.InvariantCulture);
        }
        catch (FormatException error)
        {
            // Wrap, don't swallow: the caller gets a domain-level exception
            // and the original cause is still reachable via InnerException.
            throw new ConfigurationException("port", $"'{raw}' is not a number", error);
        }
        catch (OverflowException error)
        {
            throw new ConfigurationException("port", $"'{raw}' does not fit in an int", error);
        }
        finally
        {
            // Runs on success, on exception, and on early return.
            Console.WriteLine($"  [finally] finished parsing '{raw}'");
        }
    }

    // -----------------------------------------------------------------------
    // 4. Exception filters run BEFORE the stack unwinds
    // -----------------------------------------------------------------------

    private static string Describe(Exception error) => error switch
    {
        ConfigurationException { Key: "port" } config => $"bad port: {config.Message}",
        ConfigurationException config => $"bad config ({config.Key}): {config.Message}",
        _ => $"unexpected: {error.GetType().Name}",
    };

    private static void LoadSettings(IReadOnlyDictionary<string, string> raw)
    {
        try
        {
            var port = ParsePort(raw["port"]);
            Console.WriteLine($"  port = {port}");
        }
        // `when` lets one catch block handle only some instances of a type.
        // Unlike catch-then-rethrow, a non-matching exception never unwinds
        // here at all, so the original throw site stays intact.
        catch (ConfigurationException error) when (error.Key == "port")
        {
            Console.WriteLine($"  handled: {Describe(error)}");
            Console.WriteLine($"  caused by: {error.InnerException?.GetType().Name}");
        }
    }

    // -----------------------------------------------------------------------
    // 5. Rethrowing: `throw;` keeps the stack trace, `throw error;` resets it
    // -----------------------------------------------------------------------

    private static void Retry(Action work, int attempts)
    {
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                work();
                return;
            }
            catch (InvalidOperationException) when (attempt < attempts)
            {
                Console.WriteLine($"  attempt {attempt} failed, retrying");
            }
            // The last attempt is not caught at all: the filter above stops
            // matching, so the exception propagates with its original trace.
        }
    }

    public static void Main()
    {
        Console.WriteLine("-- parse a valid port --");
        LoadSettings(new Dictionary<string, string> { ["port"] = "8080" });

        Console.WriteLine("-- parse an invalid port --");
        LoadSettings(new Dictionary<string, string> { ["port"] = "eighty-eighty" });

        Console.WriteLine("-- using: dispose on the happy path --");
        using (var scope = new ConnectionScope("primary"))
        {
            scope.Run("SELECT 1");
        }

        Console.WriteLine("-- using: dispose while an exception unwinds --");
        try
        {
            using var scope = new ConnectionScope("reporting");
            scope.Run("DROP TABLE users");   // throws
            Console.WriteLine("  never reached");
        }
        catch (InvalidOperationException error)
        {
            // Note the ordering in the output: "close reporting" is printed
            // before this line. Dispose runs as the stack unwinds.
            Console.WriteLine($"  caught: {error.Message}");
        }

        Console.WriteLine("-- retry with an exception filter --");
        var calls = 0;
        Retry(() =>
        {
            calls++;
            if (calls < 3)
            {
                throw new InvalidOperationException("transient");
            }
            Console.WriteLine($"  succeeded on attempt {calls}");
        }, attempts: 4);

        Console.WriteLine("-- guard clause --");
        try
        {
            ParsePort(null!);
        }
        catch (ArgumentNullException error)
        {
            Console.WriteLine($"  {error.GetType().Name}: {error.ParamName}");
        }

        // Guidance: catch an exception only where you can actually do
        // something about it - log with context, translate it into a domain
        // exception, or recover. A `catch (Exception) { }` that swallows
        // everything turns a loud failure into a silent wrong answer.
    }
}

/* Expected output:
-- parse a valid port --
  [finally] finished parsing '8080'
  port = 8080
-- parse an invalid port --
  [finally] finished parsing 'eighty-eighty'
  handled: bad port: 'eighty-eighty' is not a number
  caused by: FormatException
-- using: dispose on the happy path --
  open primary
  run SELECT 1 on primary
  close primary
-- using: dispose while an exception unwinds --
  open reporting
  run DROP TABLE users on reporting
  close reporting
  caught: refusing to run: DROP TABLE users
-- retry with an exception filter --
  attempt 1 failed, retrying
  attempt 2 failed, retrying
  succeeded on attempt 3
-- guard clause --
  ArgumentNullException: raw
*/
