# ЛР 4 — MergeSort, Counting, Radix, HeapSort (вариант 8)

## Запуск
    python lab04_mergesort_linear_heapsort.py --variant 8

## Реализовано
- MergeSort (стабильный, O(n log n))
- CountingSort (устойчивый, O(n+k))
- RadixSort LSD (устойчивый поразрядный проход)
- HeapSort (in-place, O(n log n))
- QuickSort (рандомизация, перенос из ЛР 3)

## Верификация
- граничные случаи: [], [x], [x,x,x], sorted, reversed;
- 200 случайных тестов на перестановку + сверка с sorted();
- тест стабильности merge на парах (ключ, номер);
- тест корректности radix на классическом [170,45,75,90,802,24,2,66];
- проверка свойства кучи после построения.

## Бенчмарк
Файлы: results/bench_*.png, results/bench_raw.json.
Методика: прогрев + 5 повторов, медиана, time.perf_counter().

## Выводы
(здесь ваши собственные выводы по графикам: например,
"на random_wide counting_sort пропущен — диапазон 10^9;
merge/heap растут как n log n (наклон >1 в log-log);
radix на random_small и radix_small обходит merge_sort по константе...")