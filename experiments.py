"""Вариант Б: хешируемость, Counter, пара ключей, индекс."""
from collections import Counter, defaultdict
from random import Random
from time import perf_counter

from main import RAW_RECORDS, build_registry

SIZES = (100, 1000, 10000, 100000)


def make_rows(n, rng):
    return [{"id": f"SK-{i:06d}", "debit": rng.random() * 100} for i in range(n)]


def find_by_scan(rows, target):
    for row in rows:
        if row["id"] == target:
            return row
    return None


def measure(action, passes=1, repeats=3):
    """Три замера; возвращает (среднее, минимум, максимум) одного прохода, мс."""
    times = []
    for _ in range(repeats):
        start = perf_counter()
        for _ in range(passes):
            action()
        times.append((perf_counter() - start) / passes * 1000)
    return sum(times) / len(times), min(times), max(times)


def benchmark():
    rng = Random(42)
    print("5) Поиск 1000 id: среднее трёх замеров (min-max), мс")
    print("N;scan;scan_min;scan_max;index;index_min;index_max;speedup;build")
    for n in SIZES:
        rows = make_rows(n, rng)
        index = {row["id"]: row for row in rows}
        queries = [rows[rng.randrange(n)]["id"] for _ in range(1000)]

        def scan():
            for target in queries:
                find_by_scan(rows, target)

        def lookup():
            for target in queries:
                index[target]

        def build():
            {row["id"]: row for row in rows}

        s = measure(scan)
        d = measure(lookup, passes=50)
        b = measure(build, passes=5)
        print(f"{n};{s[0]:.3f};{s[1]:.3f};{s[2]:.3f};{d[0]:.4f};{d[1]:.4f};"
              f"{d[2]:.4f};{s[0] / d[0]:.0f};{b[0]:.4f}", flush=True)


def main():
    records, _ = build_registry(RAW_RECORDS)
    try:
        {records[0]}
    except TypeError as error:
        print("1) set(запись) ->", type(error).__name__ + ":", error)

    print("2) tuple(items):", len({tuple(r.items()) for r in records}))
    print("   frozenset(items):", len({frozenset(r.items()) for r in records}))

    print("3) Counter:", dict(sorted(Counter(r["field"] for r in records).items())))
    groups = defaultdict(list)
    for record in records:
        groups[record["status"]].append(record["id"])
    print("   defaultdict:", {k: sorted(v) for k, v in sorted(groups.items())})

    pairs = defaultdict(float)
    for record in records:
        pairs[(record["field"], record["status"])] += record["debit"]
    print("4) Сумма дебита по парам (месторождение, статус):")
    for (field, status), total in sorted(pairs.items()):
        print(f"   {field:<10} {status:<14} {total:>6.1f}")
    total = sum(r["debit"] for r in records)
    assert abs(sum(pairs.values()) - total) < 1e-9
    print(f"   по парам: {sum(pairs.values()):.1f}; общая: {total:.1f}")
    benchmark()


if __name__ == "__main__":
    main()
