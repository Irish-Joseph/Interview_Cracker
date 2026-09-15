/**
 * Topic: Custom sorting with Comparator and thenComparing chains.
 *
 * Concepts:
 * - Comparator<T> as the way to define sort order for any type
 * - Comparator.comparing(...) to extract a sort key
 * - thenComparing(...) to build multi-level sort criteria
 * - Descending order via .reversed()
 * - Natural ordering vs explicit comparators
 *
 * Example output (sorted players):
 *   Alice     goals= 8  assists= 3   (highest goals first)
 *   Dana      goals= 8  assists= 1   (same goals -> more assists first)
 *   Chris     goals= 5  assists= 6
 *   Bob       goals= 2  assists= 4
 */
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ComparatorCustomSorting {

    record Player(String name, int goals, int assists) {}

    public static void main(String[] args) {
        List<Player> players = new ArrayList<>(List.of(
            new Player("Bob",   2, 4),
            new Player("Alice", 8, 3),
            new Player("Dana",  8, 1),
            new Player("Chris", 5, 6)
        ));

        // Multi-level sort: goals descending, then assists descending,
        // then name ascending as a deterministic tiebreaker.
        Comparator<Player> standings =
            Comparator.comparingInt(Player::goals).reversed()
                .thenComparing(Comparator.comparingInt(Player::assists).reversed())
                .thenComparing(Player::name);

        List<Player> sorted = new ArrayList<>(players);
        sorted.sort(standings);

        System.out.println("Sorted players:");
        for (Player p : sorted) {
            System.out.printf("  %-8s goals=%d assists=%d%n",
                p.name(), p.goals(), p.assists());
        }

        // Note: comparingInt/comparingLong use int/long keys; for other
        // Comparable keys use comparing(...). Example:
        //   Comparator.<Player>comparing(Player::name)  // alphabetical
        System.out.println(
            players.stream()
                .sorted(Comparator.comparing(Player::name))
                .map(Player::name)
                .toList()
        );
    }
}
