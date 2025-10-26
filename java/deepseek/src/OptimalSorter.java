import java.util.Arrays;
import java.util.Comparator;
import java.util.Random;

/**
 * Optimal Sorting Algorithms Collection for Java
 * Includes adaptive implementations with performance optimizations
 */
public class OptimalSorter {

    // Dual-Pivot Quicksort (Java's default - highly optimized)
    public static <T extends Comparable<? super T>> void dualPivotQuickSort(T[] array) {
        if (array == null || array.length <= 1) return;
        dualPivotQuickSort(array, 0, array.length - 1);
    }

    private static <T extends Comparable<? super T>> void dualPivotQuickSort(T[] array, int left, int right) {
        // Use insertion sort for small subarrays
        if (right - left < 27) {
            insertionSort(array, left, right);
            return;
        }

        // Choose pivots and partition
        if (array[left].compareTo(array[right]) > 0) {
            swap(array, left, right);
        }

        T pivot1 = array[left];
        T pivot2 = array[right];

        int less = left + 1;
        int great = right - 1;
        int k = less;

        while (k <= great) {
            if (array[k].compareTo(pivot1) < 0) {
                swap(array, k, less++);
            } else if (array[k].compareTo(pivot2) > 0) {
                while (k < great && array[great].compareTo(pivot2) > 0) {
                    great--;
                }
                swap(array, k, great--);

                if (array[k].compareTo(pivot1) < 0) {
                    swap(array, k, less++);
                }
            }
            k++;
        }

        // Swap pivots to final positions
        swap(array, left, less - 1);
        swap(array, right, great + 1);

        // Recursively sort partitions
        dualPivotQuickSort(array, left, less - 2);
        if (pivot1.compareTo(pivot2) < 0) {
            dualPivotQuickSort(array, less, great);
        }
        dualPivotQuickSort(array, great + 2, right);
    }

    // Timsort-inspired merge sort (optimal for real-world data)
    public static <T extends Comparable<? super T>> void timSort(T[] array) {
        if (array == null || array.length <= 1) return;

        int n = array.length;
        int minRun = calculateMinRun(n);

        // Sort individual subarrays of size minRun
        for (int i = 0; i < n; i += minRun) {
            int end = Math.min(i + minRun - 1, n - 1);
            insertionSort(array, i, end);
        }

        // Merge the sorted runs
        for (int size = minRun; size < n; size = 2 * size) {
            for (int left = 0; left < n; left += 2 * size) {
                int mid = left + size - 1;
                int right = Math.min(left + 2 * size - 1, n - 1);

                if (mid < right) {
                    merge(array, left, mid, right);
                }
            }
        }
    }

    // Adaptive insertion sort (optimal for small or nearly sorted arrays)
    public static <T extends Comparable<? super T>> void insertionSort(T[] array) {
        if (array == null || array.length <= 1) return;
        insertionSort(array, 0, array.length - 1);
    }

    private static <T extends Comparable<? super T>> void insertionSort(T[] array, int left, int right) {
        for (int i = left + 1; i <= right; i++) {
            T key = array[i];
            int j = i - 1;

            // Move elements that are greater than key one position ahead
            while (j >= left && array[j].compareTo(key) > 0) {
                array[j + 1] = array[j];
                j--;
            }
            array[j + 1] = key;
        }
    }

    // Heap sort (guaranteed O(n log n), good for worst-case scenarios)
    public static <T extends Comparable<? super T>> void heapSort(T[] array) {
        if (array == null || array.length <= 1) return;

        int n = array.length;

        // Build max heap
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(array, n, i);
        }

        // Extract elements from heap one by one
        for (int i = n - 1; i > 0; i--) {
            swap(array, 0, i);
            heapify(array, i, 0);
        }
    }

    private static <T extends Comparable<? super T>> void heapify(T[] array, int n, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;

        if (left < n && array[left].compareTo(array[largest]) > 0) {
            largest = left;
        }

        if (right < n && array[right].compareTo(array[largest]) > 0) {
            largest = right;
        }

        if (largest != i) {
            swap(array, i, largest);
            heapify(array, n, largest);
        }
    }

    // Utility methods
    private static <T> void swap(T[] array, int i, int j) {
        T temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }

    private static void merge(Comparable[] array, int left, int mid, int right) {
        Comparable[] leftArray = Arrays.copyOfRange(array, left, mid + 1);
        Comparable[] rightArray = Arrays.copyOfRange(array, mid + 1, right + 1);

        int i = 0, j = 0, k = left;

        while (i < leftArray.length && j < rightArray.length) {
            if (leftArray[i].compareTo(rightArray[j]) <= 0) {
                array[k++] = leftArray[i++];
            } else {
                array[k++] = rightArray[j++];
            }
        }

        while (i < leftArray.length) {
            array[k++] = leftArray[i++];
        }

        while (j < rightArray.length) {
            array[k++] = rightArray[j++];
        }
    }

    private static int calculateMinRun(int n) {
        int r = 0;
        while (n >= 64) {
            r |= (n & 1);
            n >>= 1;
        }
        return n + r;
    }

    // Generic version with Comparator
    public static <T> void sortWithComparator(T[] array, Comparator<? super T> comparator) {
        if (array == null || array.length <= 1) return;
        Arrays.sort(array, comparator);
    }

    // Performance benchmark utility
    public static <T extends Comparable<? super T>> void benchmarkSort(T[] originalArray, String algorithmName) {
        T[] array = Arrays.copyOf(originalArray, originalArray.length);
        long startTime = System.nanoTime();

        switch (algorithmName.toLowerCase()) {
            case "quicksort":
                dualPivotQuickSort(array);
                break;
            case "timsort":
                timSort(array);
                break;
            case "heapsort":
                heapSort(array);
                break;
            case "insertionsort":
                insertionSort(array);
                break;
            default:
                Arrays.sort(array);
        }

        long endTime = System.nanoTime();
        double duration = (endTime - startTime) / 1_000_000.0;

        System.out.printf("%s: %.3f ms | Sorted: %s%n",
                algorithmName, duration, isSorted(array) ? "Yes" : "No");
    }

    public static <T extends Comparable<? super T>> boolean isSorted(T[] array) {
        for (int i = 0; i < array.length - 1; i++) {
            if (array[i].compareTo(array[i + 1]) > 0) {
                return false;
            }
        }
        return true;
    }
}