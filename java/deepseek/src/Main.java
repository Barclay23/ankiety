import java.util.EmptyStackException;

/**
 * Demonstration of the optimized LIFO queue
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== High-Performance LIFO Queue Demo ===\n");

        // Create a non-thread-safe version for maximum speed
        FastLifoQueue<Integer> lifo = new FastLifoQueue<>();

        // Benchmark push operations
        System.out.println("Pushing 1,000,000 items...");
        long startTime = System.nanoTime();

        for (int i = 0; i < 1_000_000; i++) {
            lifo.push(i);
        }

        long pushTime = System.nanoTime() - startTime;
        System.out.printf("Push time: %,d ns%n", pushTime);
        System.out.printf("Queue size: %,d%n", lifo.size());

        // Benchmark pop operations
        System.out.println("\nPopping all items...");
        startTime = System.nanoTime();

        while (!lifo.isEmpty()) {
            lifo.pop();
        }

        long popTime = System.nanoTime() - startTime;
        System.out.printf("Pop time: %,d ns%n", popTime);
        System.out.printf("Queue empty: %b%n", lifo.isEmpty());

        // Demonstration of basic operations
        System.out.println("\n=== Basic Operations Demo ===");

        lifo.push(10);
        lifo.push(20);
        lifo.push(30);

        System.out.println("After pushing 10, 20, 30:");
        System.out.println("Peek: " + lifo.peek()); // Should be 30
        System.out.println("Pop: " + lifo.pop());   // Should be 30
        System.out.println("Pop: " + lifo.pop());   // Should be 20
        System.out.println("Peek: " + lifo.peek()); // Should be 10

        // Thread-safe version demo
        System.out.println("\n=== Thread-Safe Version ===");
        FastLifoQueue<String> threadSafeLifo = new FastLifoQueue<>(true);

        threadSafeLifo.push("First");
        threadSafeLifo.push("Second");
        threadSafeLifo.push("Third");

        System.out.println("Thread-safe LIFO contents:");
        while (!threadSafeLifo.isEmpty()) {
            System.out.println("Popped: " + threadSafeLifo.pop());
        }

        // Error handling demo
        System.out.println("\n=== Error Handling ===");
        try {
            threadSafeLifo.pop();
        } catch (EmptyStackException e) {
            System.out.println("Correctly caught EmptyStackException: " + e.getMessage());
        }
    }
}