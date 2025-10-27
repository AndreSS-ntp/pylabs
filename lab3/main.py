from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional


def parse_int(value: str, name: str, min_value: Optional[int] = None) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: введите целое число.")
    if min_value is not None and ivalue < min_value:
        raise ValueError(f"{name}: число должно быть не меньше {min_value}.")
    return ivalue


def parse_date(value: str, name: str = "Дата") -> datetime.date:
    # DD.MM.YYYY или YYYY-MM-DD
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


# ------------------------------ МОДЕЛЬ ДАННЫХ --------------------------------

@dataclass
class Teacher:
    tab_number: int = field(default=0)                 # табельный номер
    fio: str = field(default="")                       # ФИО
    gender: str = field(default="")                    # М/Ж
    birth_date: Optional[datetime.date] = field(default=None)
    address: str = field(default="")
    phone: str = field(default="")
    discipline: str = field(default="")
    experience_years: int = field(default=0)           # стаж (лет)

    def __post_init__(self):
        if isinstance(self.tab_number, str):
            self.tab_number = parse_int(self.tab_number, "Табельный номер", 1)
        if isinstance(self.experience_years, str):
            self.experience_years = parse_int(self.experience_years, "Стаж (лет)", 0)
        if isinstance(self.birth_date, str):
            self.birth_date = parse_date(self.birth_date, "Дата рождения")
        if self.gender:
            self.gender = normalize_gender(self.gender)
        if self.phone:
            self.phone = normalize_phone(self.phone)

    def short(self) -> str:
        bdate = self.birth_date.strftime("%d.%m.%Y") if self.birth_date else "—"
        return (f"#{self.tab_number} | {self.fio} | {self.gender or '—'} | "
                f"{bdate} | {self.discipline or '—'} | стаж {self.experience_years}")

    def full(self) -> str:
        bdate = self.birth_date.strftime("%d.%m.%Y") if self.birth_date else "—"
        return (
            f"Таб.№: {self.tab_number}\n"
            f"ФИО: {self.fio}\n"
            f"Пол: {self.gender or '—'}\n"
            f"Дата рождения: {bdate}\n"
            f"Адрес: {self.address or '—'}\n"
            f"Телефон: {self.phone or '—'}\n"
            f"Дисциплина: {self.discipline or '—'}\n"
            f"Стаж (лет): {self.experience_years}\n"
        )

    @classmethod
    def from_input(cls) -> "Teacher":
        print("Введите данные преподавателя (оставьте поле пустым, чтобы пропустить):")
        # Обязательные поля:
        tab_number = ask(lambda v: parse_int(v, "Табельный номер", 1), prompt="Табельный номер*: ")
        fio = ask(lambda v: nonempty(v, "ФИО"), prompt="ФИО*: ")
        # Необязательные:
        gender = ask_optional(normalize_gender, "Пол (М/Ж): ")
        birth_date = ask_optional(lambda v: parse_date(v, "Дата рождения"), "Дата рождения (ДД.ММ.ГГГГ): ")
        address = input("Адрес: ").strip()
        phone = ask_optional(normalize_phone, "Телефон: ")
        discipline = input("Дисциплина: ").strip()
        experience_years = ask_optional(lambda v: parse_int(v, "Стаж (лет)", 0), "Стаж (лет): ", default=0)

        return cls(
            tab_number=tab_number,
            fio=fio,
            gender=gender or "",
            birth_date=birth_date,
            address=address,
            phone=phone or "",
            discipline=discipline,
            experience_years=experience_years if experience_years is not None else 0,
        )



def ask(parse_func, prompt: str) -> any:
    while True:
        try:
            return parse_func(input(prompt).strip())
        except ValueError as e:
            print(f"Ошибка: {e}")


def ask_optional(parse_func, prompt: str, default=None):
    while True:
        s = input(prompt).strip()
        if s == "":
            return default
        try:
            return parse_func(s)
        except ValueError as e:
            print(f"Ошибка: {e}")


def print_header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def list_teachers(teachers: List[Teacher]):
    if not teachers:
        print("Список пуст.")
        return
    print_header("Список преподавателей (кратко)")
    print("№ | Краткая информация")
    print("-" * 80)
    for idx, t in enumerate(teachers, 1):
        print(f"{idx:>2}. {t.short()}")


def show_all_full(teachers: List[Teacher]):
    if not teachers:
        print("Список пуст.")
        return
    print_header("Полная информация по всем преподавателям")
    for idx, t in enumerate(teachers, 1):
        print(f"[{idx}]")
        print(t.full())
        print("-" * 80)


def delete_teacher(teachers: List[Teacher]):
    if not teachers:
        print("Список пуст — удалять нечего.")
        return
    list_teachers(teachers)
    idx = ask(lambda v: parse_int(v, "Номер в списке", 1), "Введите № для удаления: ")
    if 1 <= idx <= len(teachers):
        removed = teachers.pop(idx - 1)
        print(f"Удалён: {removed.short()}")
    else:
        print("Нет элемента с таким номером.")


def search_by_discipline(teachers: List[Teacher]):
    query = input("Введите название дисциплины (или её часть): ").strip().lower()
    if not query:
        print("Поисковый запрос пуст.")
        return
    results = [t for t in teachers if query in (t.discipline or '').lower()]
    if not results:
        print("Ничего не найдено.")
        return
    print_header(f"Найдено преподавателей: {len(results)}")
    for t in results:
        print(t.short())



def add_teacher(teachers: List[Teacher]):
    new_teacher = Teacher.from_input()
    if any(t.tab_number == new_teacher.tab_number for t in teachers):
        print(f"Ошибка: преподаватель с табельным номером {new_teacher.tab_number} уже существует.")
        return
    teachers.append(new_teacher)
    print("Преподаватель добавлен.")

def main():
    teachers: List[Teacher] = []

    actions = {
        "1": ("Добавить преподавателя", lambda: add_teacher(teachers)),
        "2": ("Удалить по номеру из списка", lambda: delete_teacher(teachers)),
        "3": ("Показать всех (кратко)", lambda: list_teachers(teachers)),
        "4": ("Показать всех (полно)", lambda: show_all_full(teachers)),
        "5": ("Поиск по дисциплине", lambda: search_by_discipline(teachers)),
        "0": ("Выход", None),
    }

    while True:
        print_header("Меню")
        for k in sorted(actions.keys()):
            print(f"{k}. {actions[k][0]}")
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            print("До свидания!")
            break
        action = actions.get(choice)
        if action is None:
            print("Неизвестный пункт меню.")
            continue
        try:
            action[1]()  # выполнить
        except KeyboardInterrupt:
            print("\nДействие прервано пользователем.")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nВыход.")
