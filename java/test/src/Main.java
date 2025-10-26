import java.util.LinkedList;

class LifoQueue<T> {
    private LinkedList<T> list = new LinkedList<>();

    // Push an item onto the stack
    public void push(T item) {
        list.addFirst(item);
        //System.out.println("Pushed: " + item);
    }

    // Pop the most recently added item
    public T pop() {
        if (isEmpty()) {
            //System.out.println("Queue is empty!");
            return null;
        }
        T item = list.removeFirst();
        //System.out.println("Popped: " + item);
        return item;
    }

    // Peek at the top item without removing it
    public T peek() {
        if (isEmpty()) {
            System.out.println("Queue is empty!");
            return null;
        }
        return list.getFirst();
    }

    // Check if the queue is empty
    public boolean isEmpty() {
        return list.isEmpty();
    }

    // Get the size of the queue
    public int size() {
        return list.size();
    }
}

public class Main {
    public static void main(String[] args) {
        long startTime = System.nanoTime();
        LifoQueue<Integer> lifo = new LifoQueue<>();


        for(int i=0; i<10000000; i++){
            lifo.push(i);
        }

        for(int i=0; i<10000000; i++){
            lifo.pop();
        }
        long endTime = System.nanoTime();
        System.out.println("Czas: " + (endTime - startTime) / 1_000_000.0 + " ms");
    }
}
