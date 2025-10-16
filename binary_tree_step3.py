from __future__ import annotations
import csv
import timeit
from functools import lru_cache
from typing import Callable, Dict, List, Any, Tuple
import matplotlib.pyplot as plt


# ---------------- Правила варианта №14 ----------------
def left_child_variant_14(value: int) -> int:
    """
    Левый потомок для варианта №14.
    Формула: left = 2 - (value - 1) = 3 - value.
    Я держу её в отдельной функции, чтобы не путаться в формулах по тексту.
    """
    return 3 - value


def right_child_variant_14(value: int) -> int:
    """
    Правый потомок для варианта №14.
    Формула: right = value * 2.
    Тоже отдельно, чтобы код читался проще.
    """
    return value * 2


# Кэшированные версии правил (именно вычисления детей кэшируем).
@lru_cache(maxsize=None)
def left_child_variant_14_cached(value: int) -> int:
    """
    То же самое, что и left_child_variant_14, но обёрнуто в кэш.
    Если одно и то же значение встречается много раз, будет быстрее.
    """
    return 3 - value


@lru_cache(maxsize=None)
def right_child_variant_14_cached(value: int) -> int:
    """
    Аналогично: кэшированная версия вычисления правого потомка.
    """
    return value * 2


# ---------------- Построение дерева ----------------
def build_tree_recursive(
    data: Dict[str, Any],
    left_fn: Callable[[int], int],
    right_fn: Callable[[int], int],
) -> List[List[int]]:
    """
    Рекурсивное построение дерева.
    Я возвращаю список уровней (levels), так нагляднее проверять.

    Параметры:
        data: словарь с "root" и "height".
        left_fn, right_fn: функции, которые считают левого и правого потомков.
                           Я сделал их параметрами, чтобы легко переключаться
                           между кэш/без кэша.

    Возвращает:
        Список уровней, где levels[0] — корень.
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    levels: List[List[int]] = [[root]]

    def expand(level_index: int, current: List[int]) -> None:
        # Если уже на нужной глубине, дальше не идём.
        if level_index == height - 1:
            return

        next_level: List[int] = []
        for v in current:
            next_level.append(left_fn(v))
            next_level.append(right_fn(v))

        levels.append(next_level)
        # Рекурсивный шаг — углубляемся на следующий уровень
        expand(level_index + 1, next_level)

    expand(0, [root])
    return levels


def build_tree_iterative(
    data: Dict[str, Any],
    left_fn: Callable[[int], int],
    right_fn: Callable[[int], int],
) -> List[List[int]]:
    """
    Нерекурсивное построение (через цикл).
    Логику оставил такой же как в рекурсивной — просто без вызовов самой себя.

    Параметры:
        data: словарь с "root" и "height".
        left_fn, right_fn: функции вычисления потомков (кэш/без кэша).

    Возвращает:
        Список уровней, как и в рекурсивной версии.
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    levels: List[List[int]] = [[root]]
    if height <= 1:
        return levels

    current: List[int] = [root]
    for _ in range(1, height):
        nxt: List[int] = []
        for v in current:
            nxt.append(left_fn(v))
            nxt.append(right_fn(v))
        levels.append(nxt)
        current = nxt
    return levels


# ---------------- Утилиты: бенчмарк, CSV, графики ----------------
def time_function(fn: Callable[[], None], repeat: int = 7, number: int = 1) -> float:
    """
    Маленькая обёртка для timeit: беру минимум из нескольких прогона.
    Мне так проще получать стабильные цифры.
    """
    return min(timeit.repeat(fn, repeat=repeat, number=number))


def benchmark_by_heights(
    builder_a: Callable[[Dict[str, Any], Callable[[int], int], Callable[[int], int]], List[List[int]]],
    builder_b: Callable[[Dict[str, Any], Callable[[int], int], Callable[[int], int]], List[List[int]]],
    left_a: Callable[[int], int], right_a: Callable[[int], int],
    left_b: Callable[[int], int], right_b: Callable[[int], int],
    root: int,
    heights: List[int],
    repeat: int = 7,
    number: int = 1,
) -> List[Tuple[int, float, float]]:
    """
    Замер времени двух "реализаций" (builder_a vs builder_b) на наборах высот.

    Я сделал универсально: можно подставить:
      - рекурсивный/итеративный
      - кэш/без кэша
    """
    rows: List[Tuple[int, float, float]] = []
    for h in heights:
        data = {"root": root, "height": h}

        def run_a():
            builder_a(data, left_a, right_a)

        def run_b():
            builder_b(data, left_b, right_b)

        t_a = time_function(run_a, repeat=repeat, number=number)
        t_b = time_function(run_b, repeat=repeat, number=number)
        rows.append((h, t_a, t_b))
    return rows


def save_csv(rows: List[Tuple[int, float, float]], path: str, header_a: str, header_b: str) -> None:
    """
    Сохраняю результаты в CSV: height, A, B.
    (Мне так удобнее потом вклеивать в отчёт.)
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["height", header_a, header_b])
        for h, a, b in rows:
            w.writerow([h, f"{a:.8f}", f"{b:.8f}"])


def plot_two_series(
    rows: List[Tuple[int, float, float]],
    label_a: str,
    label_b: str,
    title: str,
    path: str,
) -> None:
    """
    Рисую один график с двумя линиями.
    По оси X — высота дерева, по оси Y — секунды.
    """
    heights = [r[0] for r in rows]
    series_a = [r[1] for r in rows]
    series_b = [r[2] for r in rows]

    plt.figure()
    plt.plot(heights, series_a, marker="o", label=label_a)
    plt.plot(heights, series_b, marker="o", label=label_b)
    plt.xlabel("height")
    plt.ylabel("seconds")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    # Если нужно окно — раскомментируйте:
    # plt.show()


def sanity_check_same_structure() -> None:
    """
    Я на всякий случай проверяю, что базовые версии дают одинаковые уровни.
    Это не строгий тест, просто чтобы самому убедиться.
    """
    data = {"root": 14, "height": 4}
    base_rec = build_tree_recursive(data, left_child_variant_14, right_child_variant_14)
    base_it = build_tree_iterative(data, left_child_variant_14, right_child_variant_14)
    print("Совпадают ли уровни (recursive vs iterative, без кэша) при height=4? ->",
          "Да" if base_rec == base_it else "Нет")


# ---------------- Главный сценарий: 4 сравнения и 4 графика ----------------
def main() -> None:
    """
    Здесь я запускаю четыре эксперимента из твоего списка:

    1) Рекурсивный и нерекурсивный (оба без кэша)
    2) Рекурсивный без кэша и рекурсивный с кэшем
    3) Нерекурсивный без кэша и с кэшем
    4) Рекурсивный и нерекурсивный с кэшем

    Для каждого делаю отдельный CSV и отдельный PNG.
    Высоты можно поменять ниже (heights_to_test).
    """
    sanity_check_same_structure()

    root = 14
    heights_to_test = list(range(4, 17))  # 2..12 достаточно, чтобы был тренд
    repeat = 9
    number = 50

    # 1) recursive(no cache) vs iterative(no cache)
    rows1 = benchmark_by_heights(
        build_tree_recursive, build_tree_iterative,
        left_child_variant_14, right_child_variant_14,
        left_child_variant_14, right_child_variant_14,
        root, heights_to_test, repeat, number
    )
    save_csv(rows1, "exp1_rec_vs_it_no_cache.csv", "recursive_nc", "iterative_nc")
    plot_two_series(
        rows1,
        "recursive (no cache)",
        "iterative (no cache)",
        "Сравнение: рекурсивный vs нерекурсивный (без кэша)",
        "exp1_rec_vs_it_no_cache.png",
    )

    # 2) recursive(no cache) vs recursive(cached)
    rows2 = benchmark_by_heights(
        
        build_tree_recursive, build_tree_recursive,
        left_child_variant_14, right_child_variant_14,
        left_child_variant_14_cached, right_child_variant_14_cached,
        root, heights_to_test, repeat, number
    )
    save_csv(rows2, "exp2_rec_nc_vs_rec_cached.csv", "recursive_nc", "recursive_cached")
    plot_two_series(
        rows2,
        "recursive (no cache)",
        "recursive (cached)",
        "Сравнение: рекурсивный без кэша vs рекурсивный с кэшем",
        "exp2_rec_nc_vs_rec_cached.png",
    )

    # 3) iterative(no cache) vs iterative(cached)
    rows3 = benchmark_by_heights(
        build_tree_iterative, build_tree_iterative,
        left_child_variant_14, right_child_variant_14,
        left_child_variant_14_cached, right_child_variant_14_cached,
        root, heights_to_test, repeat, number
    )
    save_csv(rows3, "exp3_it_nc_vs_it_cached.csv", "iterative_nc", "iterative_cached")
    plot_two_series(
        rows3,
        "iterative (no cache)",
        "iterative (cached)",
        "Сравнение: нерекурсивный без кэша vs нерекурсивный с кэшем",
        "exp3_it_nc_vs_it_cached.png",
    )

    # 4) recursive(cached) vs iterative(cached)
    rows4 = benchmark_by_heights(
        build_tree_recursive, build_tree_iterative,
        left_child_variant_14_cached, right_child_variant_14_cached,
        left_child_variant_14_cached, right_child_variant_14_cached,
        root, heights_to_test, repeat, number
    )
    save_csv(rows4, "exp4_rec_cached_vs_it_cached.csv", "recursive_cached", "iterative_cached")
    plot_two_series(
        rows4,
        "recursive (cached)",
        "iterative (cached)",
        "Сравнение: рекурсивный vs нерекурсивный (оба с кэшем)",
        "exp4_rec_cached_vs_it_cached.png",
    )

    print("\nГотово. Сохранены 4 CSV и 4 PNG для всех сравнений.")
    print("Файлы:")
    print(" - exp1_rec_vs_it_no_cache.csv / .png")
    print(" - exp2_rec_nc_vs_rec_cached.csv / .png")
    print(" - exp3_it_nc_vs_it_cached.csv / .png")
    print(" - exp4_rec_cached_vs_it_cached.csv / .png")
    print("\nКороткий комментарий:")
    print(
        "Кэширование ускоряет случаи, где часто повторяются одинаковые входы для функций\n"
        "вычисления потомков. В нашей задаче это может проявляться, когда значения узлов\n"
        "на разных позициях совпадают. Итеративный подход обычно и так немного быстрее,\n"
        "но с кэшем обе версии выигрывают. Точный эффект зависит от высоты и повтора значений."
    )


if __name__ == "__main__":
    main()
