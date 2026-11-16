"""Собирает docs/test-cases.md из docs/test-cases.csv."""

import csv
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "test-cases.csv"
MD_PATH = ROOT / "docs" / "test-cases.md"


def load_cases():
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = [row for row in reader]
    required = {"ID", "Модуль", "Название", "Приоритет", "Тип", "Предусловия", "Шаги", "Ожидаемый результат"}
    if not rows:
        raise SystemExit("CSV не содержит тест-кейсов")
    missing = required - set(rows[0])
    if missing:
        raise SystemExit(f"В CSV нет колонок: {', '.join(sorted(missing))}")
    ids = [row["ID"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("В CSV повторяются ID тест-кейсов")
    return rows


def build_markdown(rows):
    modules = OrderedDict()
    for row in rows:
        modules.setdefault(row["Модуль"], []).append(row)

    by_type = Counter(row["Тип"] for row in rows)
    by_priority = Counter(row["Приоритет"] for row in rows)

    lines = [
        "# Тест-кейсы",
        "",
        f"Всего тест-кейсов: **{len(rows)}** (UI — "
        f"{sum(1 for r in rows if r['ID'].startswith('UI'))}, API — "
        f"{sum(1 for r in rows if r['ID'].startswith('API'))}).",
        "",
        "По типам: позитивных — "
        f"{by_type.get('Позитивный', 0)}, негативных — {by_type.get('Негативный', 0)}. "
        "По приоритету: высокий — "
        f"{by_priority.get('Высокий', 0)}, средний — {by_priority.get('Средний', 0)}, "
        f"низкий — {by_priority.get('Низкий', 0)}.",
        "",
        "Исходный файл для импорта в Test IT — [test-cases.csv](test-cases.csv) "
        "(разделитель ;, UTF-8). Шаги в одной ячейке разделены символом |, "
        "при импорте маппятся в Steps. Модуль соответствует папке/сьюту, "
        "Тип и Приоритет — соответствующим полям.",
        "",
    ]

    for module, cases in modules.items():
        lines += [f"## {module}", ""]
        for case in cases:
            steps = "; ".join(
                step.strip().rstrip(".") for step in case["Шаги"].split("|")
            )
            lines.append(
                f"**{case['ID']} {case['Название']}** "
                f"({case['Тип']}, приоритет — {case['Приоритет']}). "
                f"Предусловия: {case['Предусловия']}. Шаги: {steps}. "
                f"Ожидаемый результат: {case['Ожидаемый результат']}."
            )

    return "\n".join(lines)


def main():
    rows = load_cases()
    MD_PATH.write_text(build_markdown(rows), encoding="utf-8")
    print(f"Готово: {MD_PATH.name}, тест-кейсов: {len(rows)}")


if __name__ == "__main__":
    main()
