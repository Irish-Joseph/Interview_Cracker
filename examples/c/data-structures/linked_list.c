/*
 * Topic: A singly linked list in C — the classic heap-allocated DS.
 *
 * Concepts:
 * - Node struct with a self-referential pointer
 * - Head pointer discipline (insert at head, walk with ->)
 * - Insert (head), delete-by-value, search, print
 * - Double indirection (ListNode **) to replace the caller's head
 * - Freeing the whole list (the no-leaks loop)
 * - Why linked lists: O(1) insert at head, no contiguous memory
 *
 * Compare with arrays: linked lists insert/delete at the front in
 * O(1) but index access is O(n). They also grow one node at a time
 * on the heap — no reallocation, no capacity juggling.
 *
 * Time Complexity: search/print O(n), head insert O(1)
 *
 * Compile:  gcc -Wall -Wextra -std=c99 -o linked_list linked_list.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;   /* self-referential: nodes link to nodes */
} Node;

typedef Node *ListNode;  /* a list is just a pointer to its first node */

/* Create one node. */
static Node *make_node(int data)
{
    Node *n = malloc(sizeof *n);   /* sizeof *n, not sizeof(Node) */
    if (n == NULL) {
        fprintf(stderr, "out of memory\n");
        exit(1);
    }
    n->data = data;
    n->next = NULL;
    return n;
}

/* Insert at the head: O(1), no traversal needed.
 *
 * Note the double pointer: a new head must be written BACK into the
 * caller's variable, so we take its address. */
static void push_front(ListNode *head, int data)
{
    Node *n = make_node(data);
    n->next = *head;   /* new node points at the old first node */
    *head = n;         /* ...and becomes the new first node */
}

/* Delete the FIRST node holding `value`. Returns 1 if deleted. */
static int delete_first(ListNode *head, int value)
{
    /* Classic pattern: track the PREVIOUS node so we can unlink. */
    Node *prev = NULL;
    Node *cur  = *head;

    while (cur != NULL && cur->data != value) {
        prev = cur;
        cur = cur->next;
    }
    if (cur == NULL) {
        return 0;   /* not found */
    }

    if (prev == NULL) {
        *head = cur->next;      /* deleting the head itself */
    } else {
        prev->next = cur->next; /* bypass the node */
    }
    free(cur);
    return 1;
}

/* Search: returns 1 if any node holds `value`. */
static int contains(const ListNode head, int value)
{
    for (Node *cur = head; cur != NULL; cur = cur->next) {
        if (cur->data == value) return 1;
    }
    return 0;
}

/* Print: head -> ... -> tail */
static void print_list(const ListNode head)
{
    for (Node *cur = head; cur != NULL; cur = cur->next) {
        printf("%d", cur->data);
        if (cur->next != NULL) printf(" -> ");
    }
    printf(" -> NULL\n");
}

/* Free everything: the loop that must never leak. */
static void free_list(ListNode *head)
{
    Node *cur = *head;
    while (cur != NULL) {
        Node *next = cur->next;  /* remember next BEFORE freeing */
        free(cur);
        cur = next;
    }
    *head = NULL;
}

int main(void)
{
    ListNode head = NULL;   /* empty list = NULL head */

    /* Build: push_front(1), push_front(2), push_front(3)
     * -> 3 -> 2 -> 1 (LIFO order, as expected for head inserts) */
    push_front(&head, 1);
    push_front(&head, 2);
    push_front(&head, 3);
    print_list(head);
    /* -> 3 -> 2 -> 1 -> NULL */

    printf("contains 2: %d\n", contains(head, 2));  /* -> 1 */
    printf("contains 9: %d\n", contains(head, 9));  /* -> 0 */

    /* Delete the middle value. */
    int removed = delete_first(&head, 2);
    printf("removed 2: %d\n", removed);             /* -> 1 */
    print_list(head);
    /* -> 3 -> 1 -> NULL */

    /* Delete the HEAD value. */
    delete_first(&head, 3);
    print_list(head);
    /* -> 1 -> NULL */

    /* Deleting a missing value is a safe no-op. */
    printf("remove 99: %d\n", delete_first(&head, 99));  /* -> 0 */

    free_list(&head);
    printf("after free: head = %p\n", (void *)head);     // -> NULL
    return 0;
}

/* Expected output:
 *
 * 3 -> 2 -> 1 -> NULL
 * contains 2: 1
 * contains 9: 0
 * removed 2: 1
 * 3 -> 1 -> NULL
 * 1 -> NULL
 * remove 99: 0
 * after free: head = (nil)
 */
