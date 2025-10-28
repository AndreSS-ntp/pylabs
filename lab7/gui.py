import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

import db  # наш модуль db.py


# ---- простые валидаторы (переиспользуем идею из прошлых лаб) ----

def parse_int(value: str, name: str, min_value: Optional[int] = None) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: введите целое число.")
    if min_value is not None and ivalue < min_value:
        raise ValueError(f"{name}: число должно быть не меньше {min_value}.")
    return ivalue


def parse_date(value: str, name: str = "Дата") -> Optional[datetime.date]:
    if not value.strip():
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"{name}: неверный формат. Используйте DD.MM.YYYY или YYYY-MM-DD.")


def normalize_gender(value: str) -> str:
    v = (value or "").strip().lower()
    mapping = {
        "м": "М",
        "муж": "М",
        "мужской": "М",
        "m": "М",
        "ж": "Ж",
        "жен": "Ж",
        "женский": "Ж",
        "f": "Ж",
    }
    if v in mapping:
        return mapping[v]
    raise ValueError("Пол: укажите М или Ж.")


def nonempty(value: str, name: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValueError(f"{name}: поле не должно быть пустым.")
    return v


def normalize_phone(value: str) -> str:
    if not value:
        return ""
    allowed = "".join(ch for ch in value if ch.isdigit() or ch == "+")
    digits = "".join(ch for ch in allowed if ch.isdigit())
    if not (10 <= len(digits) <= 15):
        raise ValueError("Телефон: введите номер из 10–15 цифр (можно с +).")
    if allowed.startswith("+"):
        return "+" + digits
    return digits


# ---- само приложение ----

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЛР7 — Преподаватели и база данных (PostgreSQL)")
        self.geometry("1100x600")
        self.minsize(1000, 560)

        # инициализируем базу (create table if not exists и т.д.)
        db.init_db()

        # кэш списков для комбобоксов
        self.departments = db.list_departments()   # [(id, name), ...]
        self.subjects = db.list_subjects()         # [(id, name), ...]

        # кэш преподавателей (для удаления)
        self.teachers_cache = []  # список dict из db.list_teachers()

        # сетка окна
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # левая панель: список преподавателей
        self._build_list_panel()

        # правая панель: форма добавления
        self._build_form_panel()

        # заполнить список первый раз
        self.refresh_teachers()

    # ---------------- UI блоки ----------------

    def _build_list_panel(self):
        frame = ttk.Frame(self, padding=8)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Список преподавателей").grid(row=0, column=0, sticky="w")

        self.listbox = tk.Listbox(frame, exportselection=False)
        self.listbox.grid(row=1, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns")

        btnbar = ttk.Frame(frame)
        btnbar.grid(row=2, column=0, sticky="ew", pady=(8,0))
        btnbar.columnconfigure(0, weight=1)
        btnbar.columnconfigure(1, weight=1)

        ttk.Button(btnbar, text="Обновить список", command=self.refresh_teachers)\
            .grid(row=0, column=0, sticky="ew", padx=(0,4))

        ttk.Button(btnbar, text="Удалить выделенного", command=self.delete_selected)\
            .grid(row=0, column=1, sticky="ew", padx=(4,0))

    def _build_form_panel(self):
        frame = ttk.Frame(self, padding=8)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        # все поля формы будут храниться здесь
        self.vars = {
            "tab_number": tk.StringVar(),
            "fio": tk.StringVar(),
            "gender": tk.StringVar(value="М"),
            "birth_date": tk.StringVar(),
            "phone": tk.StringVar(),
            "experience_years": tk.StringVar(value="0"),
            "department": tk.StringVar(),
            "subject": tk.StringVar(),
        }

        row = 0
        def add_row(label, widget):
            nonlocal row
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0,8))
            widget.grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

        add_row("Табельный номер*", ttk.Entry(frame, textvariable=self.vars["tab_number"]))
        add_row("ФИО*", ttk.Entry(frame, textvariable=self.vars["fio"]))

        # радиокнопки для пола
        gframe = ttk.Frame(frame)
        ttk.Radiobutton(gframe, text="М", value="М", variable=self.vars["gender"]).pack(side="left")
        ttk.Radiobutton(gframe, text="Ж", value="Ж", variable=self.vars["gender"]).pack(side="left")
        add_row("Пол*", gframe)

        add_row("Дата рождения (ДД.ММ.ГГГГ)", ttk.Entry(frame, textvariable=self.vars["birth_date"]))
        add_row("Телефон", ttk.Entry(frame, textvariable=self.vars["phone"]))
        add_row("Стаж (лет)", ttk.Entry(frame, textvariable=self.vars["experience_years"]))

        # выпадающие списки для кафедры и дисциплины
        dept_names = [name for (_id, name) in self.departments]
        subj_names = [name for (_id, name) in self.subjects]

        dept_combo = ttk.Combobox(frame, textvariable=self.vars["department"], values=dept_names, state="readonly")
        subj_combo = ttk.Combobox(frame, textvariable=self.vars["subject"], values=subj_names, state="readonly")

        add_row("Кафедра", dept_combo)
        add_row("Дисциплина", subj_combo)

        # кнопка "Добавить"
        ttk.Button(frame, text="Добавить преподавателя", command=self.add_teacher)\
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12,0))

        row += 1

        # небольшая подсказка
        hint = (
            "Форма добавляет нового преподавателя в базу Postgres.\n"
            "Удаление — через кнопку слева «Удалить выделенного».\n"
            "Список обновляется кнопкой «Обновить список»."
        )
        ttk.Label(frame, text=hint, justify="left").grid(row=row, column=0, columnspan=2, sticky="w", pady=(12,0))

    # ----------------- Бизнес-логика кнопок -----------------

    def refresh_teachers(self):
        """Запрашивает список из БД, отображает в listbox без id-шников."""
        try:
            self.teachers_cache = db.list_teachers()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось получить список преподавателей:\n{e}")
            return

        self.listbox.delete(0, tk.END)
        for t in self.teachers_cache:
            # Красиво показываем кафедру и дисциплину
            # Пример строки: "#101 | Иванов И.И. | Кафедра информатики | Программирование | стаж 5 лет"
            dep = t.get("department") or "—"
            subj = t.get("subject") or "—"
            fio = t.get("fio") or "—"
            tabn = t.get("tab_number")
            exp = t.get("experience_years")
            line = f"#{tabn} | {fio} | {dep} | {subj} | стаж {exp} лет"
            self.listbox.insert(tk.END, line)

    def add_teacher(self):
        """Считать поля из формы, провалидировать, вставить в БД."""
        try:
            tab_number = parse_int(self.vars["tab_number"].get(), "Табельный номер", 1)
            fio = nonempty(self.vars["fio"].get(), "ФИО")
            gender = normalize_gender(self.vars["gender"].get())
            birth_date = parse_date(self.vars["birth_date"].get() or "", "Дата рождения")
            phone = normalize_phone(self.vars["phone"].get())
            exp_years = parse_int(self.vars["experience_years"].get() or "0", "Стаж (лет)", 0)

            # превратить выбранные названия кафедры/дисциплины в id
            dept_name = self.vars["department"].get().strip()
            subj_name = self.vars["subject"].get().strip()

            dept_id = None
            for _id, _name in self.departments:
                if _name == dept_name:
                    dept_id = _id
                    break

            subj_id = None
            for _id, _name in self.subjects:
                if _name == subj_name:
                    subj_id = _id
                    break

            # Проверка уникальности табельного номера
            if db.tab_number_exists(tab_number):
                raise ValueError(f"Табельный номер {tab_number} уже существует в базе.")

            db.add_teacher(
                tab_number=tab_number,
                fio=fio,
                gender=gender,
                birth_date=birth_date,
                phone=phone,
                experience_years=exp_years,
                department_id=dept_id,
                subject_id=subj_id,
            )

            messagebox.showinfo("Успех", "Преподаватель добавлен в базу.")
            self.clear_form()
            self.refresh_teachers()

        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить:\n{e}")

    def delete_selected(self):
        """Удаляет по выделению в listbox."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Нет выбора", "Выберите преподавателя в списке слева.")
            return

        idx = sel[0]
        teacher_row = self.teachers_cache[idx]
        teacher_id = teacher_row["id"]
        fio = teacher_row["fio"]
        tabn = teacher_row["tab_number"]

        if not messagebox.askyesno("Удаление", f"Удалить {fio} (#{tabn}) из базы?"):
            return

        try:
            db.delete_teacher(teacher_id)
            self.refresh_teachers()
            messagebox.showinfo("Готово", "Удалено.")
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось удалить:\n{e}")

    def clear_form(self):
        for k, var in self.vars.items():
            if k in ("gender", "experience_years"):
                continue
            var.set("")
        self.vars["gender"].set("М")
        self.vars["experience_years"].set("0")


def run_gui():
    app = App()
    app.mainloop()
