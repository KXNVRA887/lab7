"""Реестр фонда скважин на словарях и множествах."""

REQUIRED = ("id", "field", "type", "status", "debit", "water_cut")
ALLOWED_STATUSES = {"в работе", "в простое", "в консервации"}


def make(well_id, field, kind, status, debit, water_cut):
    return {"id": well_id, "field": field, "type": kind, "status": status,
            "debit": debit, "water_cut": water_cut}


RAW_RECORDS = [
    make("SK-101", "Северное", "добывающая", "в работе", 48.5, 12.0),
    make("SK-102", "Северное", "добывающая", "в простое", 0.0, 0.0),
    make("SK-103", "Северное", "нагнетательная", "в работе", 0.0, 0.0),
    make("SK-201", "Южное", "добывающая", "в работе", 96.2, 35.5),
    make("SK-202", "Южное", "добывающая", "в работе", 72.4, 58.0),
    make("SK-203", "Южное", "добывающая", "в консервации", 0.0, 0.0),
    make("SK-301", "Западное", "добывающая", "в работе", 120.0, 61.4),
    make("SK-302", "Западное", "наблюдательная", "в простое", 0.0, 0.0),
    # Две некорректные записи: дебит строкой и отсутствует поле debit
    make("SK-104", "Северное", "добывающая", "в работе", "55", 8.0),
    {"id": "SK-204", "field": "Южное", "type": "добывающая",
     "status": "в работе", "water_cut": 44.0},
]


def is_number(value):
    """True для int и float, но не для bool."""
    return type(value) in (int, float)


def validate_record(record):
    """Возвращает None для корректной записи либо код ошибки."""
    if type(record) is not dict:
        return "NOT_DICT"
    for key in REQUIRED:
        if key not in record:
            return "MISSING"
    if type(record["id"]) is not str or not record["id"].strip():
        return "BAD_ID"
    if record["status"] not in ALLOWED_STATUSES:
        return "BAD_STATUS"
    if not is_number(record["debit"]) or record["debit"] < 0:
        return "BAD_DEBIT"
    if not is_number(record["water_cut"]):
        return "BAD_WATER_CUT"
    if not 0 <= record["water_cut"] <= 100:
        return "BAD_WATER_CUT"
    return None


def build_registry(raw):
    """Возвращает (корректные записи, список ошибок (номер строки, код))."""
    records, errors, seen = [], [], set()
    for index, record in enumerate(raw):
        code = validate_record(record)
        if code is None and record["id"] in seen:
            code = "DUPLICATE"
        if code is not None:
            errors.append((index, code))
            continue
        seen.add(record["id"])
        records.append(record)
    return records, errors


def aggregate(records, group_field, metric_field):
    """Группирует записи по group_field и считает статистику metric_field."""
    result = {}
    for record in records:
        key = record[group_field]
        value = record[metric_field]
        bucket = result.get(key)
        if bucket is None:
            bucket = {"count": 0, "sum": 0.0, "min": value, "max": value}
            result[key] = bucket
        bucket["count"] += 1
        bucket["sum"] += value
        bucket["min"] = min(bucket["min"], value)
        bucket["max"] = max(bucket["max"], value)
    for bucket in result.values():
        bucket["avg"] = bucket["sum"] / bucket["count"]
    return result


def unique_values(records, field):
    """Множество уникальных значений поля."""
    return {record[field] for record in records}


def ids_where(records, field, allowed):
    """Множество id записей, у которых значение поля входит в allowed."""
    return {record["id"] for record in records if record[field] in allowed}


def ids_in_range(records, field, low, high):
    """Множество id записей, у которых значение поля в [low; high]."""
    return {record["id"] for record in records if low <= record[field] <= high}


def print_aggregate(title, data):
    print(title)
    for key in sorted(data):
        b = data[key]
        print(f"  {key:<14} count={b['count']} sum={b['sum']:.1f} "
              f"avg={b['avg']:.2f} min={b['min']:.1f} max={b['max']:.1f}")


def check_invalid():
    """Проверка четырёх видов некорректных записей."""
    good = RAW_RECORDS[0]
    missing = {k: v for k, v in good.items() if k != "debit"}
    cases = [("пропущенное поле", [missing]),
             ("неверный тип", [{**good, "debit": "48.5"}]),
             ("отрицательный дебит", [{**good, "debit": -1}]),
             ("повтор id", [good, dict(good)])]
    for name, raw in cases:
        print(f"  {name}: {build_registry(raw)[1]}")


def main():
    records, errors = build_registry(RAW_RECORDS)
    print("Записей во входных данных:", len(RAW_RECORDS))
    print("Корректных записей:", len(records))
    print("Отклонённых записей:", len(errors))
    for index, code in errors:
        print(f"  индекс {index}: {code}")
    print("Проверка некорректных записей:")
    check_invalid()

    by_field = aggregate(records, "field", "debit")
    assert sum(b["count"] for b in by_field.values()) == len(records)
    print_aggregate("Агрегация по месторождению (debit):", by_field)
    print_aggregate("Агрегация по статусу (water_cut):",
                    aggregate(records, "status", "water_cut"))

    print("Месторождения:", sorted(unique_values(records, "field")))
    print("Пар (месторождение, статус):",
          len({(r["field"], r["status"]) for r in records}))
    active = ids_where(records, "status", {"в работе"})
    wet = ids_in_range(records, "water_cut", 60, 100)
    print("В работе:", sorted(active))
    print("Обводнённость 60-100 %:", sorted(wet))
    print("active & wet:", sorted(active & wet))
    print("active | wet:", sorted(active | wet))
    print("active - wet:", sorted(active - wet))
    print("active ^ wet:", sorted(active ^ wet))
    print("wet <= active:", wet <= active)


if __name__ == "__main__":
    main()
