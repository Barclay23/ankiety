import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Main {
    private static final Random RANDOM = new Random();

    public static void main(String[] args) {
        long startTime = System.nanoTime();
        System.out.println("FastIntLifoQueue Performance Test");
        System.out.println("=================================");

        // Test with 100K elements
        testWithSize(100_000, "100K elements");

        // Test with 10M elements
        testWithSize(10_000_000, "10M elements");

        // Test bulk operations
        testBulkOperations();
        long endTime = System.nanoTime();
        System.out.println("Czas: " + (endTime - startTime) / 1_000_000.0 + " ms");
    }

    private static void testWithSize(int size, String description) {
        System.out.println("\nTesting with " + description + ":");

        FastIntLifoQueue stack = new FastIntLifoQueue(size);

        // Test push performance
        long startTime = System.nanoTime();
        for (int i = 0; i < size; i++) {
            stack.push(RANDOM.nextInt());
        }
        long pushTime = System.nanoTime() - startTime;

        // Test pop performance
        startTime = System.nanoTime();
        for (int i = 0; i < size; i++) {
            stack.pop();
        }
        long popTime = System.nanoTime() - startTime;

        System.out.printf("Push time: %,d ms%n", TimeUnit.NANOSECONDS.toMillis(pushTime));
        System.out.printf("Pop time:  %,d ms%n", TimeUnit.NANOSECONDS.toMillis(popTime));
        System.out.printf("Initial capacity: %,d%n", stack.capacity());
    }

    private static void testBulkOperations() {
        System.out.println("\nTesting Bulk Operations:");

        FastIntLifoQueue stack = new FastIntLifoQueue(100_000);
        int[] bulkData = new int[50_000];
        for (int i = 0; i < bulkData.length; i++) {
            bulkData[i] = RANDOM.nextInt();
        }

        // Single push timing
        long startTime = System.nanoTime();
        for (int value : bulkData) {
            stack.push(value);
        }
        long singlePushTime = System.nanoTime() - startTime;

        stack.clear();

        // Bulk push timing
        startTime = System.nanoTime();
        stack.pushAll(bulkData);
        long bulkPushTime = System.nanoTime() - startTime;

        System.out.printf("Single push time: %,d ms%n", TimeUnit.NANOSECONDS.toMillis(singlePushTime));
        System.out.printf("Bulk push time:   %,d ms%n", TimeUnit.NANOSECONDS.toMillis(bulkPushTime));
        System.out.printf("Bulk operations %.1fx faster%n", (double)singlePushTime / bulkPushTime);
    }
}