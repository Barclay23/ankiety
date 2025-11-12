import java.util.ArrayDeque;
import java.util.Deque;
import java.util.EmptyStackException;
import java.util.concurrent.locks.ReentrantLock;

/**
 * High-performance LIFO (Last-In-First-Out) queue implementation
 * Optimized for execution speed with thread-safe option
 */
public class FastLifoQueue<T> {
    private final Deque<T> deque;
    private final boolean threadSafe;
    private final ReentrantLock lock;

    /**
     * Creates a non-thread-safe LIFO queue (maximum performance)
     */
    public FastLifoQueue() {
        this.deque = new ArrayDeque<>();
        this.threadSafe = false;
        this.lock = null;
    }

    /**
     * Creates a LIFO queue with specified thread safety
     * @param threadSafe if true, uses locking for thread safety (slightly slower)
     */
    public FastLifoQueue(boolean threadSafe) {
        this.deque = new ArrayDeque<>();
        this.threadSafe = threadSafe;
        this.lock = threadSafe ? new ReentrantLock() : null;
    }

    /**
     * Creates a LIFO queue with initial capacity
     * @param initialCapacity initial capacity of the underlying storage
     * @param threadSafe if true, uses locking for thread safety
     */
    public FastLifoQueue(int initialCapacity, boolean threadSafe) {
        this.deque = new ArrayDeque<>(initialCapacity);
        this.threadSafe = threadSafe;
        this.lock = threadSafe ? new ReentrantLock() : null;
    }

    /**
     * Pushes an item onto the top of the LIFO queue
     * @param item the item to push
     * @return the pushed item
     */
    public T push(T item) {
        if (threadSafe) {
            lock.lock();
            try {
                deque.addFirst(item);
            } finally {
                lock.unlock();
            }
        } else {
            deque.addFirst(item);
        }
        return item;
    }

    /**
     * Removes and returns the top item from the LIFO queue
     * @return the top item
     * @throws EmptyStackException if the queue is empty
     */
    public T pop() {
        if (threadSafe) {
            lock.lock();
            try {
                if (deque.isEmpty()) {
                    throw new EmptyStackException();
                }
                return deque.removeFirst();
            } finally {
                lock.unlock();
            }
        } else {
            if (deque.isEmpty()) {
                throw new EmptyStackException();
            }
            return deque.removeFirst();
        }
    }

    /**
     * Returns the top item without removing it
     * @return the top item
     * @throws EmptyStackException if the queue is empty
     */
    public T peek() {
        if (threadSafe) {
            lock.lock();
            try {
                if (deque.isEmpty()) {
                    throw new EmptyStackException();
                }
                return deque.peekFirst();
            } finally {
                lock.unlock();
            }
        } else {
            if (deque.isEmpty()) {
                throw new EmptyStackException();
            }
            return deque.peekFirst();
        }
    }

    /**
     * Checks if the LIFO queue is empty
     * @return true if the queue is empty
     */
    public boolean isEmpty() {
        if (threadSafe) {
            lock.lock();
            try {
                return deque.isEmpty();
            } finally {
                lock.unlock();
            }
        } else {
            return deque.isEmpty();
        }
    }

    /**
     * Returns the number of items in the LIFO queue
     * @return the size of the queue
     */
    public int size() {
        if (threadSafe) {
            lock.lock();
            try {
                return deque.size();
            } finally {
                lock.unlock();
            }
        } else {
            return deque.size();
        }
    }

    /**
     * Removes all items from the LIFO queue
     */
    public void clear() {
        if (threadSafe) {
            lock.lock();
            try {
                deque.clear();
            } finally {
                lock.unlock();
            }
        } else {
            deque.clear();
        }
    }

    /**
     * Java 21: Returns a string representation of the LIFO queue
     * @return string representation from top to bottom
     */
    @Override
    public String toString() {
        if (threadSafe) {
            lock.lock();
            try {
                return "FastLifoQueue" + deque.toString();
            } finally {
                lock.unlock();
            }
        } else {
            return "FastLifoQueue" + deque.toString();
        }
    }
}