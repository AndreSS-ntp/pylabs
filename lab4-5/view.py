import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List
from typing import Optional
from model import Teacher, save_teachers, load_teachers
from controller import parse_int, parse_date, normalize_phone, normalize_gender, nonempty


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЛР4 — Преподаватели")
        self.geometry("1300x560")
        self.minsize(900, 520)

        # текущий открытый файл
        self.current_file: Optional[str] = None
        self._build_menu()

        self.teachers: List[Teacher] = []

        self._build_search_bar()

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        self._build_list_panel()
        self._build_form_panel()

        self._build_actions_panel()



    def _build_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Создать", command=self.menu_new)
        filemenu.add_command(label="Открыть…", command=self.menu_open)
        filemenu.add_separator()
        filemenu.add_command(label="Сохранить", command=self.menu_save)
        filemenu.add_command(label="Сохранить как…", command=self.menu_save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.menu_exit)
        menubar.add_cascade(label="Файл", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="О программе", command=self.menu_about)
        menubar.add_cascade(label="Справка", menu=helpmenu)

        self.config(menu=menubar)

    def menu_new(self):
        if self.teachers and not messagebox.askyesno("Создать", "Очистить текущие данные?"):
            return
        self.teachers.clear()
        self.refresh_listbox()
        self.clear_form()
        self.current_file = None
        self.title("ЛР5 — Преподаватели (новый файл)")

    def menu_open(self):
        path = filedialog.askopenfilename(title="Открыть файл",
                                          filetypes=[("JSON файлы","*.json"), ("Все файлы","*.*")])
        if not path:
            return
        try:
            self.teachers = load_teachers(path)
            self.refresh_listbox()
            self.clear_form()
            self.current_file = path
            self.title(f"ЛР5 — Преподаватели — {path}")
            messagebox.showinfo("Открыто", f"Загружено записей: {len(self.teachers)}")
        except Exception as e:
            messagebox.showerror("Ошибка открытия", str(e))

    def menu_save(self):
        if not self.current_file:
            return self.menu_save_as()
        try:
            save_teachers(self.current_file, self.teachers)
            messagebox.showinfo("Сохранено", f"Файл обновлён:\n{self.current_file}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def menu_save_as(self):
        path = filedialog.asksaveasfilename(title="Сохранить как",
                                            defaultextension=".json",
                                            filetypes=[("JSON файлы","*.json"), ("Все файлы","*.*")])
        if not path:
            return
        self.current_file = path
        self.menu_save()

    def menu_exit(self):
        if messagebox.askokcancel("Выход", "Выйти из программы?"):
            self.destroy()

    def menu_about(self):
        messagebox.showinfo("О программе",
                            "Программа: Список преподавателей\nЛР5 — работа с файлами\nРазработчик: Андрюха")
    def _build_search_bar(self):
        bar = ttk.Frame(self, padding=8)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(bar, text="Поиск по дисциплине:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=30).pack(side="left", padx=6)
        ttk.Button(bar, text="Найти", command=self.search).pack(side="left")
        ttk.Button(bar, text="Сброс", command=self.reset_search).pack(side="left", padx=(6,0))

        self.fullinfo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, variable=self.fullinfo_var, text="Показывать полную информацию").pack(side="right")

    def _build_list_panel(self):
        left = ttk.Frame(self, padding=(8,0,8,8))
        left.grid(row=1, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="Преподаватели").grid(row=0, column=0, sticky="w")

        self.listbox = tk.Listbox(left, exportselection=False)
        self.listbox.config(width=90)
        self.listbox.grid(row=1, column=0, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scroll = ttk.Scrollbar(left, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns")

    def _build_form_panel(self):
        right = ttk.Frame(self, padding=(0,0,8,8))
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        self.vars = {
            "tab_number": tk.StringVar(),
            "fio": tk.StringVar(),
            "gender": tk.StringVar(value="М"),
            "birth_date": tk.StringVar(),
            "address": tk.StringVar(),
            "phone": tk.StringVar(),
            "discipline": tk.StringVar(),
            "experience_years": tk.StringVar(value="0"),
        }

        row = 0
        def add_row(label, widget):
            nonlocal row
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0,8))
            widget.grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

        add_row("Табельный номер*", ttk.Entry(right, textvariable=self.vars["tab_number"]))
        add_row("ФИО*", ttk.Entry(right, textvariable=self.vars["fio"]))

        gframe = ttk.Frame(right)
        ttk.Radiobutton(gframe, text="М", variable=self.vars["gender"], value="М").pack(side="left")
        ttk.Radiobutton(gframe, text="Ж", variable=self.vars["gender"], value="Ж").pack(side="left")
        add_row("Пол", gframe)

        add_row("Дата рождения (ДД.ММ.ГГГГ)", ttk.Entry(right, textvariable=self.vars["birth_date"]))
        add_row("Адрес", ttk.Entry(right, textvariable=self.vars["address"]))
        add_row("Телефон", ttk.Entry(right, textvariable=self.vars["phone"]))

        disciplines = ["", "Математика", "Физика", "Информатика", "Химия", "Литература"]
        combo = ttk.Combobox(right, textvariable=self.vars["discipline"], values=disciplines)
        combo.set(disciplines[0])
        add_row("Дисциплина", combo)

        add_row("Стаж (лет)", ttk.Entry(right, textvariable=self.vars["experience_years"]))

    def _build_actions_panel(self):
        panel = ttk.Frame(self, padding=8)
        panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        panel.columnconfigure((0,1,2,3), weight=1)

        ttk.Button(panel, text="Добавить", command=self.add_teacher).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(panel, text="Обновить выделенного", command=self.update_teacher).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(panel, text="Удалить выделенного", command=self.delete_teacher).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(panel, text="Показать информацию", command=self.show_selected_info).grid(row=0, column=3, sticky="ew", padx=4)


    def validate_form(self) -> Teacher:
        try:
            tab_number = parse_int(self.vars["tab_number"].get(), "Табельный номер", 1)
            fio = nonempty(self.vars["fio"].get(), "ФИО")
            gender = normalize_gender(self.vars["gender"].get())
            birth_date = parse_date(self.vars["birth_date"].get() or "")
            address = self.vars["address"].get().strip()
            phone = normalize_phone(self.vars["phone"].get())
            discipline = self.vars["discipline"].get().strip()
            experience_years = parse_int(self.vars["experience_years"].get() or "0", "Стаж (лет)", 0)
            return Teacher(tab_number, fio, gender, birth_date, address, phone, discipline, experience_years)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            raise

    def add_teacher(self):
        try:
            t = self.validate_form()
        except ValueError:
            return
        # проверка уникальности табельного номера
        if any(x.tab_number == t.tab_number for x in self.teachers):
            messagebox.showwarning("Дубликат", f"Преподаватель с табельным номером {t.tab_number} уже есть.")
            return
        self.teachers.append(t)
        self.refresh_listbox()
        messagebox.showinfo("Готово", "Преподаватель добавлен.")

    def update_teacher(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Нет выбора", "Выберите преподавателя в списке.")
            return
        idx = sel[0]
        try:
            t = self.validate_form()
        except ValueError:
            return
        if any(x.tab_number == t.tab_number for i, x in enumerate(self.teachers) if i != idx):
            messagebox.showwarning("Дубликат", f"Табельный номер {t.tab_number} уже используется.")
            return
        self.teachers[idx] = t
        self.refresh_listbox()
        messagebox.showinfo("Готово", "Данные обновлены.")

    def delete_teacher(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Нет выбора", "Выберите преподавателя в списке.")
            return
        idx = sel[0]
        t = self.teachers[idx]
        if messagebox.askyesno("Подтверждение", f"Удалить {t.fio} (#{t.tab_number})?"):
            del self.teachers[idx]
            self.refresh_listbox()
            self.clear_form()

    def show_selected_info(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Нет выбора", "Выберите преподавателя в списке.")
            return
        t = self.teachers[sel[0]]
        text = t.full() if self.fullinfo_var.get() else t.short()
        messagebox.showinfo("Информация", text)

    def search(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_listbox()
            return
        filtered = [t for t in self.teachers if q in (t.discipline or '').lower()]
        self.refresh_listbox(filtered)

    def reset_search(self):
        self.search_var.set("")
        self.refresh_listbox()

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        t = self.teachers[sel[0]]
        self.vars["tab_number"].set(str(t.tab_number))
        self.vars["fio"].set(t.fio)
        self.vars["gender"].set(t.gender or "М")
        self.vars["birth_date"].set(t.birth_date.strftime("%d.%m.%Y") if t.birth_date else "")
        self.vars["address"].set(t.address)
        self.vars["phone"].set(t.phone)
        self.vars["discipline"].set(t.discipline)
        self.vars["experience_years"].set(str(t.experience_years))

    def clear_form(self):
        for k, v in self.vars.items():
            if k in ("gender", "experience_years"):
                continue
            v.set("")
        self.vars["gender"].set("М")
        self.vars["experience_years"].set("0")

    def refresh_listbox(self, dataset: Optional[List[Teacher]] = None):
        if dataset is None:
            dataset = self.teachers
        self.listbox.delete(0, tk.END)
        for t in dataset:
            self.listbox.insert(tk.END, t.short())
