// Extension methods add discoverable operations without changing the target type.
using System;

public static class TextExtensions
{
    // The `this` modifier makes the first parameter the receiver.
    public static int WordCount(this string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return 0;
        }

        return text.Split(
            (char[]?)null,
            StringSplitOptions.RemoveEmptyEntries
        ).Length;
    }

    public static string Truncate(this string text, int maximumLength)
    {
        ArgumentNullException.ThrowIfNull(text);
        ArgumentOutOfRangeException.ThrowIfNegative(maximumLength);

        if (text.Length <= maximumLength)
        {
            return text;
        }

        return maximumLength <= 1
            ? text[..maximumLength]
            : text[..(maximumLength - 1)] + "…";
    }
}

public static class Program
{
    public static void Main()
    {
        string message = "Extension methods read like instance methods";

        Console.WriteLine($"Words: {message.WordCount()}");
        Console.WriteLine(message.Truncate(24));

        // Static-call syntax is equivalent and sometimes clarifies the owner.
        Console.WriteLine(TextExtensions.WordCount("  spaced   words  "));
        Console.WriteLine("   ".WordCount());
    }
}
