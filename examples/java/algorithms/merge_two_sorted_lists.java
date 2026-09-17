/**
 * Topic: Merge two sorted lists into one sorted list.
 *
 * Concepts:
 * - The two-pointer technique
 * - Linear-time merging (the "merge" step of merge sort)
 * - Linked lists (node-by-node construction)
 *
 * Example:
 * list1 = 1 -> 3 -> 5
 * list2 = 2 -> 3 -> 4
 * result = 1 -> 2 -> 3 -> 3 -> 4 -> 5
 *
 * Time Complexity: O(n + m)
 * Space Complexity: O(1) extra (new nodes aside)
 */
public class MergeTwoSortedLists {

    /** A minimal singly linked list node. */
    static class ListNode {
        int value;
        ListNode next;

        ListNode(int value) {
            this.value = value;
            this.next = null;
        }
    }

    /**
     * Merges two sorted linked lists into a new sorted list
     * using one pointer per input list.
     */
    static ListNode merge(ListNode a, ListNode b) {
        // A dummy head avoids special-casing the first node.
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;

        while (a != null && b != null) {
            if (a.value <= b.value) {
                tail.next = a;
                a = a.next;
            } else {
                tail.next = b;
                b = b.next;
            }
            tail = tail.next;
        }

        // Attach whatever is left over (already sorted).
        tail.next = (a != null) ? a : b;

        return dummy.next;
    }

    // --- Small helpers for the demo ------------------------------------

    static ListNode fromArray(int[] values) {
        ListNode head = null, tail = null;
        for (int v : values) {
            ListNode node = new ListNode(v);
            if (head == null) {
                head = tail = node;
            } else {
                tail.next = node;
                tail = node;
            }
        }
        return head;
    }

    static String toString(ListNode node) {
        StringBuilder sb = new StringBuilder();
        while (node != null) {
            if (!sb.isEmpty()) sb.append(" -> ");
            sb.append(node.value);
            node = node.next;
        }
        return sb.isEmpty() ? "(empty)" : sb.toString();
    }

    // --- Demo -----------------------------------------------------------

    public static void main(String[] args) {
        System.out.println(toString(merge(
                fromArray(new int[]{1, 3, 5}),
                fromArray(new int[]{2, 3, 4}))));
        // -> 1 -> 2 -> 3 -> 3 -> 4 -> 5

        System.out.println(toString(merge(
                fromArray(new int[]{}),
                fromArray(new int[]{7, 8}))));
        // -> 7 -> 8

        System.out.println(toString(merge(
                fromArray(new int[]{}),
                fromArray(new int[]{}))));
        // -> (empty)
    }
}
