from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from controller import parse_int, parse_date, normalize_phone, normalize_gender

@dataclass
class Teacher:
    tab_number: int = field(default=0)
    fio: str = field(default="")
    gender: str = field(default="")
    birth_date: Optional[datetime.date] = field(default=None)
    address: str = field(default="")
    phone: str = field(default="")
    discipline: str = field(default="")
    experience_years: int = field(default=0)

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
        return f"#{self.tab_number} | {self.fio} | {self.gender or '—'} | {bdate} | {self.discipline or '—'} | стаж {self.experience_years}"

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
    def to_dict(self) -> dict:
        return {
            "tab_number": self.tab_number,
            "fio": self.fio,
            "gender": self.gender,
            "birth_date": self.birth_date.strftime("%Y-%m-%d") if self.birth_date else None,
            "address": self.address,
            "phone": self.phone,
            "discipline": self.discipline,
            "experience_years": self.experience_years,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Teacher":
        return cls(
            tab_number=data.get("tab_number", 0),
            fio=data.get("fio", ""),
            gender=data.get("gender", ""),
            birth_date=data.get("birth_date"),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            discipline=data.get("discipline", ""),
            experience_years=data.get("experience_years", 0),
        )


import json
from typing import List

def save_teachers(path: str, teachers: List[Teacher]) -> None:
    data = [t.to_dict() for t in teachers]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_teachers(path: str) -> List[Teacher]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = [Teacher.from_dict(item) for item in data]
    # ensure uniqueness of tab_number
    seen = set()
    uniq = []
    for t in result:
        if t.tab_number in seen:
            continue
        seen.add(t.tab_number)
        uniq.append(t)
    return uniq
