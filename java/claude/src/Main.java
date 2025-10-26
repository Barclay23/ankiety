import java.util.LinkedList;

class LIFOQueue<T> {
    private LinkedList<T> queue;

    public LIFOQueue() {
        queue = new LinkedList<>();
    }

    public void enqueue(T item) {
        queue.addFirst(item);
    }

    public T dequeue() {
        if (isEmpty()) {
            throw new IllegalStateException("Queue is empty");
        }
        return queue.removeFirst();
    }

    public T peek() {
        if (isEmpty()) {
            throw new IllegalStateException("Queue is empty");
        }
        return queue.getFirst();
    }

    public boolean isEmpty() {
        return queue.isEmpty();
    }

    public int size() {
        return queue.size();
    }

    @Override
    public String toString() {
        return queue.toString();
    }
}

public class Main {
    public static void main(String[] args) {
        long startTime = System.nanoTime();

        LIFOQueue<Integer> lifoQueue = new LIFOQueue<>();

        System.out.println("Enqueueing elements: 1, 2, 3, 4, 5");
        lifoQueue.enqueue(1);
        lifoQueue.enqueue(2);
        lifoQueue.enqueue(3);
        lifoQueue.enqueue(4);
        lifoQueue.enqueue(5);

        System.out.println("Queue contents: " + lifoQueue);
        System.out.println("Size: " + lifoQueue.size());

        System.out.println("\nPeek (without removing): " + lifoQueue.peek());

        System.out.println("\nDequeuing elements:");
        while (!lifoQueue.isEmpty()) {
            System.out.println("Dequeued: " + lifoQueue.dequeue());
        }

        System.out.println("\nQueue is now empty: " + lifoQueue.isEmpty());
        long endTime = System.nanoTime();
        System.out.println("Czas: " + (endTime - startTime) / 1_000_000.0 + " ms");
    }
}