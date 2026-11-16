"""Прогоняет schema.sql, seed.sql и queries.sql на SQLite и проверяет результаты."""

import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"

EXPECTED_ROWS = {
    1: 5,
    2: 6,
    3: 2,
    4: 2,
    5: 5,
    6: 22,
    7: 2,
    8: 16,
    9: 16,
    10: 13,
    11: 4,
    13: 5,
    14: 6,
    15: 3,
    17: 6,
    18: 5,
}

EXPECTED_COUNTS = {
    "clients": 15,
    "accounts": 22,
    "cards": 18,
    "transactions": 60,
}

MARKER = re.compile(r"^-- @(?P<kind>task|indexes|dml-rollback|dml)\s*(?P<title>.*)$")


def split_sections(text):
    sections = []
    current = None
    for line in text.splitlines():
        match = MARKER.match(line)
        if match:
            current = {"kind": match.group("kind"), "title": match.group("title").strip(), "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    for section in sections:
        section["sql"] = "\n".join(section["lines"]).strip()
    return sections


def print_rows(columns, rows, limit=5):
    if columns:
        print("  " + " | ".join(columns))
    for row in rows[:limit]:
        print("  " + " | ".join(str(value) for value in row))
    if len(rows) > limit:
        print(f"  ... ещё {len(rows) - limit} строк")


def main():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    conn.executescript((SQL_DIR / "seed.sql").read_text(encoding="utf-8"))

    print("Данные загружены:")
    for table, expected in EXPECTED_COUNTS.items():
        actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert actual == expected, f"{table}: ожидалось {expected}, получено {actual}"
        print(f"  {table}: {actual}")

    sections = split_sections((SQL_DIR / "queries.sql").read_text(encoding="utf-8"))
    checks = 0
    tasks = 0

    for section in sections:
        kind, title, sql = section["kind"], section["title"], section["sql"]
        if not sql:
            continue
        print(f"\n[{kind}] {title}")

        statement_count = sql.count(";")
        if kind != "task" and statement_count > 1:
            conn.executescript(sql)
            print(f"  выполнено операторов: {statement_count}")
        else:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            columns = [item[0] for item in cursor.description] if cursor.description else []
            print_rows(columns, rows)
            if kind == "task":
                task_number = int(title.split(".")[0])
                expected = EXPECTED_ROWS.get(task_number)
                if expected is not None:
                    assert len(rows) == expected, (
                        f"Задача {task_number}: ожидалось {expected} строк, получено {len(rows)}"
                    )
                    checks += 1
                tasks += 1

        if kind == "dml":
            inserted = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE transaction_id = 999"
            ).fetchone()[0]
            balance = conn.execute(
                "SELECT balance FROM accounts WHERE account_id = 1"
            ).fetchone()[0]
            assert inserted == 1, "INSERT в транзакции не выполнен"
            assert balance == 153543.50, f"Баланс после UPDATE: {balance}"
            checks += 2
        if kind == "dml-rollback":
            inserted = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE transaction_id = 1000"
            ).fetchone()[0]
            balance = conn.execute(
                "SELECT balance FROM accounts WHERE account_id = 1"
            ).fetchone()[0]
            assert inserted == 0, "ROLLBACK не отменил вставку операции 1000"
            assert balance == 153543.50, f"ROLLBACK не восстановил баланс: {balance}"
            checks += 2

    assert tasks == 20, f"Ожидалось 20 задач, найдено {tasks}"
    print(f"\nИтог: {tasks} SQL-задач, {checks} проверок ожидаемых результатов — успешно")


if __name__ == "__main__":
    main()
