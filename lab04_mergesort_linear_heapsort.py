#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort — вариант 8 (seed = 38).

Реализации написаны вручную (анти-чит КИМ-04). sorted() используется только
как эталон для верификации и в бенчмарке для сравнения.

Запуск: python lab04_mergesort_linear_heapsort.py --variant 8
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # без GUI — сохраняем графики в файлы
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.

    Стабильность: при равенстве ключей берём из left (left был раньше во входе).
    Время O(len(left) + len(right)), память O(len(left) + len(right)).
    """
    merged: list = []
    i = j = 0
    n_left, n_right = len(left), len(right)
    while i < n_left and j < n_right:
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    if i < n_left:
        merged.extend(left[i:])
    if j < n_right:
        merged.extend(right[j:])
    return merged


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список.

    T(n) = 2T(n/2) + O(n)  =>  O(n log n) во всех случаях.
    Память O(n) на слияния.
    """
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из [0, key_max].

    Схема: счётчики -> префиксные суммы -> расстановка с конца (иначе
    теряется устойчивость).
    Время O(n + k), память O(n + k), k = key_max + 1.
    Ограничение: при k >> n память и время доминируются k, а не полезным n.
    """
    n = len(a)
    if n == 0:
        return []
    k = key_max + 1
    counts = [0] * k
    for x in a:
        counts[x] += 1
    for i in range(1, k):
        counts[i] += counts[i - 1]
    out = [0] * n
    for i in range(n - 1, -1, -1):
        x = a[i]
        counts[x] -= 1
        out[counts[x]] = x
    return out


def _counting_sort_by_digit(a: list[int], exp: int) -> list[int]:
    """Устойчивая counting-сортировка по десятичной цифре (a[i] // exp) % 10."""
    n = len(a)
    counts = [0] * 10
    for x in a:
        counts[(x // exp) % 10] += 1
    for i in range(1, 10):
        counts[i] += counts[i - 1]
    out = [0] * n
    for i in range(n - 1, -1, -1):
        d = (a[i] // exp) % 10
        counts[d] -= 1
        out[counts[d]] = a[i]
    return out


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.

    Сложность O(d·(n + 10)) ≈ O(d·n), d = число разрядов max(a).
    Устойчивость внутреннего прохода обязательна: старшие разряды не должны
    «перетирать» порядок, установленный младшими проходами. Без устойчивости
    результат был бы неверным (элементы с одинаковой цифрой текущего разряда
    перемешивались бы случайно).
    """
    if not a:
        return []
    result = list(a)
    max_val = max(result)
    exp = 1
    while max_val // exp > 0:
        result = _counting_sort_by_digit(result, exp)
        exp *= 10
    return result


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в max-куче a[0:n], на месте."""
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place через sift down.

    Построение max-кучи за O(n) (сумма высот поддеревьев),
    затем n извлечений максимума по O(log n) => итого O(n log n).
    Память O(1). Нестабилен: обмен вершины с последним ломает порядок равных.
    """
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort: рандомизация + 3-way partition + итерация в меньшую половину.

    Ключевые решения:
      * рандомизация опоры — защита от «злонамеренно плохих» входов;
      * 3-way partition (Дейкстра) — при дубликатах равные опоре элементы
        сразу оказываются в средней части и не участвуют в рекурсии;
      * рекурсия только в меньшую половину, большая обрабатывается циклом —
        глубина стека гарантированно O(log n) при любом входе, в том числе
        на уже отсортированных массивах.

    Средний/лучший: O(n log n). Худший: O(n²) по числу сравнений,
    но глубина стека O(log n). Память O(log n) (стек).
    Нестабилен.
    """
    arr = list(a)

    def _partition3(lo: int, hi: int) -> tuple[int, int]:
        # рандомизированный выбор опоры
        p = random.randint(lo, hi)
        arr[lo], arr[p] = arr[p], arr[lo]
        pivot = arr[lo]
        lt, i, gt = lo, lo + 1, hi
        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1
        return lt, gt

    def _qs(lo: int, hi: int) -> None:
        while lo < hi:
            lt, gt = _partition3(lo, hi)
            # рекурсия в меньшую часть, цикл — на большую
            if (lt - lo) < (hi - gt):
                _qs(lo, lt - 1)
                lo = gt + 1
            else:
                _qs(gt + 1, hi)
                hi = lt - 1

    _qs(0, len(arr) - 1)
    return arr


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи + случайные тесты + сверка с эталоном sorted()."""
    boundary = [
        [],
        [7],
        [0],
        [5, 5, 5],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [0, 0, 1, 0, 1, 1, 0],
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list),
               f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a),
               f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a),
               f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, номер).

    Эталон sorted() стабилен, поэтому при равных ключах номера обязаны
    идти в исходном порядке.
    """
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок")


def check_radix_correctness() -> None:
    """Radix корректен только при устойчивом поразрядном проходе.

    Классический пример: [170, 45, 75, 90, 802, 24, 2, 66] — на неустойчивом
    проходе результат был бы неверным.
    """
    a = [170, 45, 75, 90, 802, 24, 2, 66]
    expect(radix_sort_lsd(a) == sorted(a),
           f"radix неверен на классическом примере: {radix_sort_lsd(a)}")


def check_radix_stability_preserved() -> None:
    """Устойчивость прохода radix проверяется через равенство эталону sorted()
    на массиве с повторяющимися младшими разрядами."""
    a = [11, 21, 31, 41, 12, 22, 32, 42, 13, 23, 33, 43]
    expect(radix_sort_lsd(a) == sorted(a), "radix нарушил порядок на цифрах")


def check_heap_invariant() -> None:
    """После построения кучи a[i] >= потомков."""
    rng = random.Random(1)
    a = [rng.randint(0, 99) for _ in range(50)]
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for i in range(n // 2):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n:
            expect(a[i] >= a[l], f"свойство кучи нарушено: a[{i}] < a[{l}]")
        if r < n:
            expect(a[i] >= a[r], f"свойство кучи нарушено: a[{i}] < a[{r}]")


def check_quick_sort_robust() -> None:
    """Стресс-тест QuickSort на «плохих» входах — без RecursionError.

    Проверяем случаи, на которых наивная реализация Ломуто падает:
    большой отсортированный массив и массив с большим числом дубликатов.
    """
    n = 50_000
    a = list(range(n))
    expect(quick_sort(a) == a, "quick_sort на отсортированном 50000")
    b = [i % 100 for i in range(n)]
    expect(quick_sort(b) == sorted(b), "quick_sort на 50000 дубликатов")
    c = list(range(n, 0, -1))
    expect(quick_sort(c) == sorted(c), "quick_sort на обратном 50000")


def self_check() -> None:
    """Все проверки; при ошибке замеры не выполняются."""
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks += [
        ("стабильность merge_sort", check_merge_stability),
        ("корректность radix", check_radix_correctness),
        ("устойчивость прохода radix", check_radix_stability_preserved),
        ("свойство кучи", check_heap_invariant),
        ("устойчивость quick_sort к худшим входам", check_quick_sort_robust),
    ]
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


ALGORITHMS = [
    ("merge_sort", merge_sort),
    ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
    ("radix_sort_lsd", radix_sort_lsd),
    ("heap_sort", heap_sort),
    ("quick_sort", quick_sort),
    ("sorted()", sorted),
]


def run_benchmarks(seed: int, results_dir: Path) -> dict:
    rng = random.Random(seed)
    raw: dict[str, dict[str, dict[int, float]]] = {}

    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            raw.setdefault(dist_name, {algo: {} for algo, _ in ALGORITHMS})
            print(f"  распределение {dist_name}:")
            for algo_name, fn in ALGORITHMS:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    print(f"    {algo_name:>18}: пропуск (k ~ 10^9, ~8 ГБ памяти)")
                    continue
                try:
                    t = bench(fn, data)
                except MemoryError:
                    print(f"    {algo_name:>18}: MemoryError")
                    continue
                raw[dist_name][algo_name][n] = t
                print(f"    {algo_name:>18}: t = {t:.6f} c")

    results_dir.mkdir(parents=True, exist_ok=True)
    for dist_name, algo_data in raw.items():
        plt.figure(figsize=(8, 5))
        for algo_name, series in algo_data.items():
            if not series:
                continue
            xs = sorted(series.keys())
            ys = [series[x] for x in xs]
            plt.loglog(xs, ys, marker="o", label=algo_name)
        plt.title(f"Бенчмарк, распределение: {dist_name}")
        plt.xlabel("n (log)")
        plt.ylabel("t, с (log)")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        out = results_dir / f"bench_{dist_name}.png"
        plt.savefig(out, dpi=120)
        plt.close()
        print(f"график: {out}")

    serial = {d: {a: {str(n): t for n, t in s.items()} for a, s in ad.items()}
              for d, ad in raw.items()}
    out_json = results_dir / "bench_raw.json"
    out_json.write_text(json.dumps(serial, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nсырые замеры: {out_json}")
    return raw


# ---------------------------------------------------------------------------
# 4. main
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--results", type=Path, default=Path("results"),
                    help="каталог для графиков/JSON")
    args = ap.parse_args()

    # Запас на случай глубокой рекурсии в merge_sort/heap_sort; для quick_sort
    # глубина гарантированно O(log n) благодаря итерации в меньшую половину.
    sys.setrecursionlimit(1_000_000)

    seed = 30 + args.variant
    random.seed(seed)
    print(f"Вариант {args.variant}, seed = {seed}")

    self_check()
    run_benchmarks(seed, args.results)


if __name__ == "__main__":
    main()