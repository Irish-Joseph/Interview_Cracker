/* Fixed-capacity circular queue with O(1) enqueue and dequeue operations. */
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

#define CAPACITY 5

typedef struct {
    int items[CAPACITY];
    size_t head;  /* index of the next item to remove */
    size_t tail;  /* index where the next item is inserted */
    size_t count;
} CircularQueue;

void queue_init(CircularQueue *queue) {
    queue->head = 0;
    queue->tail = 0;
    queue->count = 0;
}

bool queue_is_empty(const CircularQueue *queue) {
    return queue->count == 0;
}

bool queue_is_full(const CircularQueue *queue) {
    return queue->count == CAPACITY;
}

bool queue_enqueue(CircularQueue *queue, int value) {
    if (queue_is_full(queue)) {
        return false;
    }

    queue->items[queue->tail] = value;
    queue->tail = (queue->tail + 1) % CAPACITY;
    queue->count++;
    return true;
}

bool queue_dequeue(CircularQueue *queue, int *value) {
    if (queue_is_empty(queue)) {
        return false;
    }

    *value = queue->items[queue->head];
    queue->head = (queue->head + 1) % CAPACITY;
    queue->count--;
    return true;
}

void queue_print(const CircularQueue *queue) {
    printf("queue:");
    for (size_t offset = 0; offset < queue->count; offset++) {
        size_t index = (queue->head + offset) % CAPACITY;
        printf(" %d", queue->items[index]);
    }
    putchar('\n');
}

int main(void) {
    CircularQueue queue;
    queue_init(&queue);

    for (int value = 10; value <= 50; value += 10) {
        queue_enqueue(&queue, value);
    }
    queue_print(&queue);
    printf("enqueue while full: %s\n", queue_enqueue(&queue, 60) ? "ok" : "rejected");

    int removed;
    queue_dequeue(&queue, &removed);
    printf("removed: %d\n", removed);
    queue_dequeue(&queue, &removed);
    printf("removed: %d\n", removed);

    /* These writes wrap from the end of the array back to index zero. */
    queue_enqueue(&queue, 60);
    queue_enqueue(&queue, 70);
    queue_print(&queue);

    return 0;
}
