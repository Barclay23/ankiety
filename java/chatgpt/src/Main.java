public class Main {

    public static void main(String[] args) {
        long startTime = System.nanoTime();
        LifoQueue queue = new LifoQueue(5);

        // Demo
        queue.push(10);
        queue.push(20);
        queue.push(30);
        System.out.println(queue.pop()); // 30
        System.out.println(queue.pop()); // 20
        queue.push(40);
        queue.push(50);
        queue.push(60);
        queue.push(70); // This will be rejected (full)
        queue.printState();
        long endTime = System.nanoTime();
        System.out.println("Czas: " + (endTime - startTime) / 1_000_000.0 + " ms");
    }
}

/**
 * Ultra-fast bounded LIFO queue for primitive ints.
 * Non-thread-safe, constant-time operations.
 */
final class LifoQueue {

    private final int[] elements;
    private int top = -1;
    private final int capacity;

    public LifoQueue(int capacity) {
        if (capacity <= 0)
            throw new IllegalArgumentException("Capacity must be positive");
        this.capacity = capacity;
        this.elements = new int[capacity];
    }

    /** Pushes a value onto the stack if not full. */
    public boolean push(int value) {
        if (top + 1 >= capacity) {
            // Queue is full
            return false;
        }
        elements[++top] = value;
        return true;
    }

    /** Pops the last pushed value, or throws if empty. */
    public int pop() {
        if (top < 0)
            throw new IllegalStateException("Queue is empty");
        return elements[top--];
    }

    /** Peeks the last pushed value without removing it. */
    public int peek() {
        if (top < 0)
            throw new IllegalStateException("Queue is empty");
        return elements[top];
    }

    /** Returns current size. */
    public int size() {
        return top + 1;
    }

    /** Checks if the queue is empty. */
    public boolean isEmpty() {
        return top < 0;
    }

    /** Checks if the queue is full. */
    public boolean isFull() {
        return top + 1 == capacity;
    }

    /** Prints internal state (for debug). */
    public void printState() {
        System.out.print("LifoQueue [");
        for (int i = 0; i <= top; i++) {
            System.out.print(elements[i]);
            if (i < top) System.out.print(", ");
        }
        System.out.println("]");
    }
}
