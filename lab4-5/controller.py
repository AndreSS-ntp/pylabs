from datetime import datetime
from typing import Optional

def parse_int(value: str, name: str, min_value: Optional[int] = None) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: введите целое число.")
    if min_value is not None and ivalue < min_value:
        raise ValueError(f"{name}: число должно быть не меньше {min_value}.")
    return ivalue


def parse_date(value: str, name: str = "Дата") -> datetime.date:
    if not value:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"{name}: неверный формат. Используйте DD.MM.YYYY или YYYY-MM-DD.")


def normalize_gender(value: str) -> str:
    v = (value or "").strip().lower()
    mapping = {"м": "М", "муж": "М", "мужской": "М", "m": "М",
               "ж": "Ж", "жен": "Ж", "женский": "Ж", "f": "Ж"}
    if v in mapping:
        return mapping[v]
    raise ValueError("Пол: укажите М/Ж.")


def normalize_phone(value: str) -> str:
    if not value:
        return ""
    allowed = "".join(ch for ch in value if ch.isdigit() or ch == "+")
    digits = "".join(ch for ch in allowed if ch.isdigit())
    if not (10 <= len(digits) <= 15):
        raise ValueError("Телефон: введите номер из 10–15 цифр (можно с +, пробелами и скобками).")
    if allowed.startswith("+"):
        return "+" + digits
    return digits


def nonempty(value: str, name: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValueError(f"{name}: поле не должно быть пустым.")
    return v