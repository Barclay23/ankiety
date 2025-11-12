import java.util.LinkedList;
import java.util.Arrays;
import java.util.NoSuchElementException;


public class Main {
    public static final int LARGE_CAP = 10_000_000;
    public static final int SMALL_CAP = 100_000;

    public static void main(String[] args) {
        long startTime = System.nanoTime();
        IntLifoQueue lifo = new IntLifoQueue(10000000);


        for (int i = 0; i < 10000000; i++) {
            lifo.push(i);
        }

        for (int i = 0; i < 10000000; i++) {
            lifo.pop();
        }
        long endTime = System.nanoTime();
        System.out.println("Czas: " + (endTime - startTime) / 1_000_000.0 + " ms");
    }

    static class IntLifoQueue {
        private int[] data;
        private int top;

        public IntLifoQueue(int initialCapacity) {
            this.data = new int[initialCapacity];
            this.top = -1;
        }

        public void push(int value) {
            if (top == data.length - 1) {
                resize();
            }
            data[++top] = value;
        }

        public int pop() {
            return data[top--];
        }

        private void resize() {
            int newCapacity = data.length + (data.length >> 1);
            int[] newData = new int[newCapacity];
            System.arraycopy(data, 0, newData, 0, data.length);
            data = newData;
        }
    }
}
