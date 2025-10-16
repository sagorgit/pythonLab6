from __future__ import annotations
from typing import Dict, List, Any


def left_child_variant_14(value: int) -> int:
    """
    Возвращает значение левого потомка для варианта №14.
    
    Правило: left = 2 - (value - 1) = 3 - value.
    """
    return 3 - value


def right_child_variant_14(value: int) -> int:
    """
    Возвращает значение правого потомка для варианта №14.
    
    Правило: right = value * 2.
    """
    return value * 2


def build_tree_recursive(data: Dict[str, Any]) -> List[List[int]]:
    """
    Построение бинарного дерева рекурсивным способом для варианта №14.

    Параметры:
        data: словарь с ключами:
            - "root": значение в корневом узле (int)
            - "height": высота дерева (int), где корень — это уровень 1.

    Возвращает:
        Список уровней дерева (List[List[int]]), где levels[i] — это
        список значений узлов на уровне i (начиная с i=0 для корня).

    Замечания:
        - Здесь дерево представлено как список уровней для наглядности.
        - Для каждого узла вычисляются левый и правый потомки по правилам
          варианта №14.
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    # levels[0] = [root]
    levels: List[List[int]] = [[root]]

    def expand(level_index: int, current_level_nodes: List[int]) -> None:
        # Базовый случай: если достигли требуемой высоты, завершаем.
        # У нас levels[0] — это уровень 1 (корень), значит
        # всего должно быть height уровней -> индекс последнего = height - 1.
        if level_index == height - 1:
            return

        next_level: List[int] = []
        for val in current_level_nodes:
            left = left_child_variant_14(val)
            right = right_child_variant_14(val)
            next_level.extend([left, right])

        levels.append(next_level)
        expand(level_index + 1, next_level)

    expand(0, [root])
    return levels


def build_tree_iterative(data: Dict[str, Any]) -> List[List[int]]:
    """
    Построение бинарного дерева итеративным способом (через цикл) для варианта №14.

    Параметры:
        data: словарь с ключами:
            - "root": значение в корневом узле (int)
            - "height": высота дерева (int), где корень — это уровень 1.

    Возвращает:
        Список уровней дерева (List[List[int]]).

    Идея:
        - Начинаем с уровня [root].
        - Для каждой следующей глубины порождаем новый уровень,
          вычисляя left/right для каждого элемента текущего уровня.
    """
    root: int = int(data["root"])
    height: int = int(data["height"])

    levels: List[List[int]] = [[root]]
    # Если высота 1 — уже есть только корень
    if height <= 1:
        return levels

    current_level: List[int] = [root]
    # Нам нужно построить уровни 2..height
    for _ in range(1, height):
        next_level: List[int] = []
        for val in current_level:
            left = left_child_variant_14(val)
            right = right_child_variant_14(val)
            next_level.extend([left, right])
        levels.append(next_level)
        current_level = next_level

    return levels


def pretty_print_levels(levels: List[List[int]]) -> None:
    """
    Печатает уровни дерева в удобочитаемом виде.
    """
    for i, level in enumerate(levels, start=1):
        print(f"Уровень {i}: {level}")


if __name__ == "__main__":
    # Данные для варианта №14: root=14, height=4
    data_example = {"root": 14, "height": 4}

    print("=== Рекурсивная версия ===")
    levels_rec = build_tree_recursive(data_example)
    pretty_print_levels(levels_rec)

    print("\n=== Итеративная версия ===")
    levels_it = build_tree_iterative(data_example)
    pretty_print_levels(levels_it)
