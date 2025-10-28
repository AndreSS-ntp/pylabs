"""
db.py — слой доступа к базе Postgres для ЛР7.
"""

import psycopg2
from datetime import datetime, date
from typing import List, Tuple, Dict, Any, Optional

# Параметры подключения к контейнеру Postgres
DB_HOST = "localhost"
DB_PORT = 5439
DB_NAME = "university"
DB_USER = "labuser"
DB_PASS = "labpass"


def get_connection():
    """Создаёт новое подключение к Postgres."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def init_db():
    """
    Создаёт таблицы, если их нет.
    Заполняет справочники кафедр и дисциплин начальными значениями.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Кафедры
            cur.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                );
            """)

            # Дисциплины
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                );
            """)

            # Преподаватели (основная таблица)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id SERIAL PRIMARY KEY,
                    tab_number INTEGER UNIQUE NOT NULL,
                    fio TEXT NOT NULL,
                    gender CHAR(1) NOT NULL CHECK (gender IN ('М','Ж')),
                    birth_date DATE,
                    phone TEXT,
                    experience_years INTEGER NOT NULL DEFAULT 0 CHECK (experience_years >= 0),

                    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL
                );
            """)

            # Начальные данные для справочников, если пусто
            cur.execute("SELECT COUNT(*) FROM departments;")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    "INSERT INTO departments(name) VALUES (%s);",
                    [
                        ("Кафедра математики",),
                        ("Кафедра информатики",),
                        ("Кафедра физики",),
                    ],
                )

            cur.execute("SELECT COUNT(*) FROM subjects;")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    "INSERT INTO subjects(name) VALUES (%s);",
                    [
                        ("Математический анализ",),
                        ("Программирование",),
                        ("Теоретическая физика",),
                    ],
                )

        conn.commit()


def list_departments() -> List[Tuple[int, str]]:
    """[(id, 'Кафедра ...'), ...]"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name FROM departments ORDER BY name;")
        return cur.fetchall()


def list_subjects() -> List[Tuple[int, str]]:
    """[(id, 'Дисциплина ...'), ...]"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name FROM subjects ORDER BY name;")
        return cur.fetchall()


def list_teachers() -> List[Dict[str, Any]]:
    """
    Возвращает преподавателей в человеко-читаемом виде:
    fio, табельный номер, стаж, Кафедра по имени, Дисциплина по имени.
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT
                t.id,
                t.tab_number,
                t.fio,
                t.gender,
                t.birth_date,
                t.phone,
                t.experience_years,
                d.name AS department,
                s.name AS subject
            FROM teachers t
            LEFT JOIN departments d ON d.id = t.department_id
            LEFT JOIN subjects   s ON s.id = t.subject_id
            ORDER BY t.id;
        """)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        # превращаем список tuples в список dict-ов
        result = [dict(zip(cols, row)) for row in rows]
        return result


def tab_number_exists(tab_number: int) -> bool:
    """Проверка уникальности табельного номера."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM teachers WHERE tab_number=%s;", (tab_number,))
        return cur.fetchone() is not None


def add_teacher(
    tab_number: int,
    fio: str,
    gender: str,
    birth_date: Optional[date],
    phone: str,
    experience_years: int,
    department_id: Optional[int],
    subject_id: Optional[int],
) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO teachers(
                tab_number, fio, gender, birth_date, phone,
                experience_years, department_id, subject_id
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
            """,
            (
                tab_number,
                fio,
                gender,
                birth_date,
                phone,
                experience_years,
                department_id,
                subject_id,
            ),
        )
        conn.commit()


def delete_teacher(teacher_id: int) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM teachers WHERE id=%s;", (teacher_id,))
        conn.commit()
