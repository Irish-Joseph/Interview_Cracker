/**
 * Topic: Java Streams — filter, map, group and collect.
 *
 * Concepts:
 * - Stream pipelines (intermediate vs terminal operations)
 * - method references (String::length)
 * - Collectors: toList, groupingBy, counting, summarizingInt
 * - Immutable-friendly data shaping without index loops
 *
 * A stream is a sequence of operations over data that produces a
 * result. Intermediate operations (filter, map) are LAZY; nothing
 * happens until a terminal operation (collect, forEach, count) runs.
 *
 * Time Complexity: O(n) per full pipeline pass
 *
 * NOTE: validated by inspection (no working JDK on authoring host).
 */
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.stream.Collectors;
import java.util.stream.IntSummaryStatistics;

public class StreamGrouping {

    record Employee(String name, String dept, int salary) {}

    public static void main(String[] args) {
        List<Employee> team = List.of(
                new Employee("Alice", "engineering", 95_000),
                new Employee("Bob",   "sales",       60_000),
                new Employee("Carol", "engineering", 110_000),
                new Employee("Dan",   "sales",       55_000),
                new Employee("Eve",   "engineering", 88_000)
        );

        // --- 1. filter + map: names of senior engineers -----------------
        List<String> seniorEngineers = team.stream()
                .filter(e -> e.dept().equals("engineering"))
                .filter(e -> e.salary() >= 90_000)
                .map(Employee::name)
                .sorted()
                .toList();
        System.out.println("senior engineers: " + seniorEngineers);
        // -> [Alice, Carol]

        // --- 2. groupingBy: employees per department ----------------------
        Map<String, List<String>> namesByDept = team.stream()
                .collect(Collectors.groupingBy(
                        Employee::dept,
                        Collectors.mapping(Employee::name, Collectors.toList())
                ));
        System.out.println("by dept: " + namesByDept);
        // -> {engineering=[Alice, Carol, Eve], sales=[Bob, Dan]}

        // --- 3. groupingBy + counting: headcount per department -----------
        Map<String, Long> headcount = team.stream()
                .collect(Collectors.groupingBy(Employee::dept,
                                               Collectors.counting()));
        System.out.println("headcount: " + headcount);
        // -> {engineering=3, sales=2}

        // --- 4. summarizingInt: salary stats per department ---------------
        Map<String, IntSummaryStatistics> salaryStats = team.stream()
                .collect(Collectors.groupingBy(
                        Employee::dept,
                        Collectors.summarizingInt(Employee::salary)
                ));
        salaryStats.forEach((dept, stats) -> System.out.printf(
                "%s: count=%d avg=%.0f min=%d max=%d%n",
                dept, stats.getCount(), stats.getAverage(),
                stats.getMin(), stats.getMax()));
        // engineering: count=3 avg=97667 min=88000 max=110000
        // sales:       count=2 avg=57500 min=55000 max=60000

        // --- 5. Optional: max by a comparator (safe empty handling) -------
        OptionalInt highest = team.stream()
                .mapToInt(Employee::salary)
                .max();
        System.out.println("highest salary: " + highest.orElse(-1));
        // -> 110000

        // --- 6. toList() vs collect(Collectors.toList()) -------------------
        // Both produce a List; toList() (Java 16+) returns an
        // unmodifiable list, which is usually what you want.
    }
}
