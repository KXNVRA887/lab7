"""Упражнения 1-6."""
from collections import defaultdict

from main import RAW_RECORDS, aggregate, build_registry, ids_where

records, _ = build_registry(RAW_RECORDS)


def aggregate_dd(items, group_field, metric_field):
    groups = defaultdict(list)
    for record in items:
        groups[record[group_field]].append(record[metric_field])
    return {key: {"count": len(v), "sum": sum(v), "min": min(v),
                  "max": max(v), "avg": sum(v) / len(v)}
            for key, v in groups.items()}


print("Упражнение 1")
for step in range(1, 6):
    state = aggregate(records[:step], "field", "debit")
    print(f"  после {records[step - 1]['id']}:",
          {k: (b["count"], round(b["sum"], 1)) for k, b in state.items()})

print("Упражнение 2")
total = sum(b["count"] for b in aggregate(records, "field", "debit").values())
assert total == len(records)
print(f"  сумма count = {total}, записей = {len(records)}")

print("Упражнение 3")
for name, value in [("int", 5), ("str", "SK-101"), ("tuple чисел", (1, 2, 3)),
                    ("tuple со списком", (1, [2, 3])), ("запись dict", records[0])]:
    try:
        {value}
        print(f"  {name}: добавлено")
    except TypeError as error:
        print(f"  {name}: TypeError: {error}")

print("Упражнение 4")
copy = {**RAW_RECORDS[0], "debit": 50.0, "water_cut": 15.0}
valid, errors = build_registry(RAW_RECORDS + [copy])
print(f"  корректных: {len(valid)}; ошибки: {errors}")

print("Упражнение 5")
for group, metric in (("field", "debit"), ("status", "water_cut")):
    same = aggregate(records, group, metric) == aggregate_dd(records, group, metric)
    print(f"  {group}/{metric}: результаты совпадают: {same}")

print("Упражнение 6")
active = ids_where(records, "status", {"в работе"})
print("  без sorted:", list(active))
print("  с sorted:  ", sorted(active))
