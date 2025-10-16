from __future__ import annotations
import timeit
from typing import Dict, List, Any, Tuple


# ---- Правила варианта №14 ----
def left_child_variant_14(value: int) -> int:
    """
    Честно говоря, правило простое, но сначала его сложно запомнить.
    Для варианта №14 левый потомок считается так:
    left = 2 - (value - 1) = 3 - value.
    """
    return 3 - value


def right_child_variant_14(value: int) -> int:
    """
    Правый потомок в варианте №14 получается умножением на два.
    То есть просто: right = value * 2.
    """
    return value * 2


# ---- Рекурсивная версия ----
def build_tree_recursive(data: Dict[str, Any]) -> List[List[int]]:
    """
    Рекурсивное построение уровней бинарного дерева.
    Я сделал представление в виде списка уровней, потому что
    так наглядно видно, что именно получается на каждой глубине.

    Параметры:
        data: ожидаю словарь с ключами:
            - "root": int — значение в корне,
            - "height": int — высота дерева (корень — это уровень 1).

    Возвращает:
        Список уровней, где levels[0] — корень,
        levels[1] — второй уровень и т.д. до заданной высоты.
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    levels: List[List[int]] = [[root]]

    def expand(level_index: int, current_level_nodes: List[int]) -> None:
        # Если уже на последнем уровне, дальше не углубляемся.
        if level_index == height - 1:
            return

        next_level: List[int] = []
        for val in current_level_nodes:
            left = left_child_variant_14(val)
            right = right_child_variant_14(val)
            next_level.extend([left, right])

        levels.append(next_level)
        # Рекурсивный шаг: движемся к следующему уровню
        expand(level_index + 1, next_level)

    expand(0, [root])
    return levels


# ---- Итеративная версия ----
def build_tree_iterative(data: Dict[str, Any]) -> List[List[int]]:
    """
    Построение бинарного дерева через цикл (без рекурсии).
    Логика та же самая, что и в рекурсивной,
    но мы сами управляем текущим и следующим уровнем.

    Параметры:
        data: словарь с "root" и "height".

    Возвращает:
        Список уровней (как в рекурсивной версии).
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    levels: List[List[int]] = [[root]]
    if height <= 1:
        return levels

    current_level: List[int] = [root]
    for _ in range(1, height):
        next_level: List[int] = []
        for val in current_level:
            left = left_child_variant_14(val)
            right = right_child_variant_14(val)
            next_level.extend([left, right])
        levels.append(next_level)
        current_level = next_level

    return levels


# ---- Сервис: аккуратный вывод ----
def pretty_print_levels(levels: List[List[int]]) -> None:
    """
    Просто печатаю уровни один под другим. Удобно для проверки.
    """
    for i, level in enumerate(levels, start=1):
        print(f"Уровень {i}: {level}")


# ---- Бенчмарк с timeit ----
def benchmark_builders(
    root: int,
    heights: List[int],
    repeat: int = 5,
    number: int = 1,
) -> List[Tuple[int, float, float]]:
    """
    Замеряю время работы двух функций на разных высотах дерева.
    Я беру timeit.repeat, чтобы результат был стабильнее (беру min).

    Параметры:
        root: значение в корне (для моего варианта удобно держать 14,
              но для честного сравнения можно пробовать и другие).
        heights: список высот, которые будем измерять.
        repeat: сколько раз повторять серию замеров (берём минимум).
        number: сколько построений на один замер (обычно 1 хватает,
                но если очень быстро — можно увеличить).

    Возвращает:
        Список кортежей (height, t_recursive, t_iterative) в секундах.
    """
    results: List[Tuple[int, float, float]] = []

    for h in heights:
        data = {"root": root, "height": h}

        # Оборачиваем вызываемые функции замыканиями, чтобы timeit их дергал
        def run_rec():
            build_tree_recursive(data)

        def run_it():
            build_tree_iterative(data)

        t_rec = min(timeit.repeat(run_rec, repeat=repeat, number=number))
        t_it = min(timeit.repeat(run_it, repeat=repeat, number=number))

        results.append((h, t_rec, t_it))

    return results


def print_benchmark_table(rows: List[Tuple[int, float, float]]) -> None:
    """
    Рисую простую табличку в консоли, чтобы глазами сравнить.
    """
    print("\n=== Сравнение времени (сек) ===")
    print("{:<8} {:>12} {:>12}".format("height", "recursive", "iterative"))
    print("-" * 34)
    for h, t_rec, t_it in rows:
        print("{:<8} {:>12.6f} {:>12.6f}".format(h, t_rec, t_it))


if __name__ == "__main__":
    # Для варианта №14 исходные данные:
    # root = 14 (фиксированный по условию варианта),
    # но высоту для эксперимента можно менять (в задании просили график по высоте).
    root = 14

    # Набор высот для замера. 2..10 — этого достаточно, чтобы увидеть тренд.
    heights_to_test = list(range(2, 11))

    # Быстрый sanity-check: обе функции дают одинаковые уровни.
    demo_data = {"root": root, "height": 4}
    print("Проверка равенства структур (для height=4):")
    levels_rec = build_tree_recursive(demo_data)
    levels_it = build_tree_iterative(demo_data)
    same = levels_rec == levels_it
    print("Совпадают ли уровни? ->", "Да" if same else "Нет")
    if same:
        pretty_print_levels(levels_rec)

    # Бенчмарк: number=1 чаще всего достаточно, repeat=5 берём минимум
    rows = benchmark_builders(root=root, heights=heights_to_test, repeat=5, number=1)
    print_benchmark_table(rows)

    # Небольшой вывод словами (как я понимаю результаты).
    # Здесь просто подсказка, детальный вывод сделаем после графика.
    print("\nЧерновой вывод:")
    print(
        "По моим замерам видно, что обе функции растут по времени с увеличением высоты, "
        "так как на каждом уровне количество узлов удваивается. "
        "Часто итеративная версия получается немного быстрее из-за отсутствия накладных "
        "расходов на рекурсию (вызовы функций и т.п.), но это надо смотреть на графике."
    )
