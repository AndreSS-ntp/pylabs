import math
import sys

def part1_expression():
    try:
        x = float(input("Введите x: "))
        n = float(input("Введите n: "))

        if x <= 0:
            print("Error: введите x > 0!")
            return

        if n == 0:
            print("Error: введите n != 0")
            return

        # sqrt( |cos x|**n + exp(n**3)/ln(x) + |sin x|**(1/n) )
        term1 = abs(math.cos(x)) ** n

        ln_x = math.log(x)
        if ln_x == 0:
            print("Error: ln(x) = 0, деление на 0 запрещено.")
            return

        term2 = math.exp(n ** 3) / ln_x
        term3 = abs(math.sin(x)) ** (1.0 / n)

        inside = term1 + term2 + term3

        if inside < 0:
            print("Error: подкоренное выражение < 0.")
            return

        result = math.sqrt(inside)
        print(f"Результат: {result}")

    except ValueError:
        print("Error: введены неверные данные (требуется int).")
    except Exception as e:
        print("Произошла Error:", str(e))


def input_typed_value():
    t = input("Выберите тип добавляемого элемента (int, float, str, bool): ").lower()
    if t == "int":
        v = input("Введите int число: ")
        try:
            return int(v)
        except ValueError:
            raise ValueError("Неверное int число.")
    elif t == "float":
        v = input("Введите float число: ")
        try:
            return float(v)
        except ValueError:
            raise ValueError("Неверное float число.")
    elif t == "bool":
        v = input("Введите bool значение: ").lower()
        if v in ("true", "t", "1"):
            return True
        elif v in ("false", "f", "0"):
            return False
        else:
            raise ValueError("Неверное bool значение.")
    elif t == "str":
        v = input("Введите строку: ")
        return v
    else:
        raise ValueError("Неизвестный тип данных.")


def part2_list_manager():
    lst = []
    while True:
        print("\nТекущее содержимое списка:", lst)
        print("\nМеню (выберите номер операции):")
        print("1) Показать значения списка на экране")
        print("2) Добавление нового элемента в конец списка (разных типов)")
        print("3) Удаление указанного пользователем элемента из списка (удалится первое вхождение)")
        print("4) Сформировать кортеж из вещественных положительных элементов списка и вывести его")
        print("5) Найти произведение всех целочисленных элементов списка (int, исключая bool)")
        print("6) Сформировать строку из значений элементов списка и посчитать, сколько раз встречается указанное слово")
        print("7) Задать с клавиатуры множество M1, сформировать множество M2 из списка; вывести симметрическую разницу M1 и M2")
        print("8) Получить из списка словарь: ключ = позиция элемента (начиная с 1), значение = элемент; вывести элементы словаря с нечетными ключами")
        print("9) Выйти в главное меню")
        choice = input("Ваш выбор: ")

        if choice == "1":
            print("Список:", lst)

        elif choice == "2":
            try:
                val = input_typed_value()
                lst.append(val)
                print("Элемент добавлен.")
            except ValueError as e:
                print("Ошибка при вводе:", e)

        elif choice == "3":
            if not lst:
                print("Список пуст, нечего удалять.")
                continue
            to_remove = input("Введите элемент для удаления: ")
            removed = False
            candidates = []
            for i, e in enumerate(lst):
                if str(e) == to_remove:
                    candidates.append(i)
            if candidates:
                idx = candidates[0]
                print(f"Удалить элемент {lst[idx]} (позиция {idx}).")
                lst.pop(idx)
                removed = True
            else:
                print("Элемент не найден в списке.")

        elif choice == "4":
            tup = tuple(e for e in lst if isinstance(e, float) and e > 0)
            print("Кортеж из положительных вещественных элементов:", tup)

        elif choice == "5":
            prod = 1
            found = False
            for e in lst:
                if isinstance(e, int) and not isinstance(e, bool):
                    prod *= e
                    found = True
            if found:
                print("Произведение целочисленных элементов:", prod)
            else:
                print("Целочисленные (int) элементы не найдены.")

        elif choice == "6":
            s = " ".join(str(e) for e in lst)
            print("Сформированная строка:", s)
            word = input("Введите слово для подсчёта в этой строке: ")
            count = s.count(word)
            print(f"Слово '{word}' встречается в строке {count} раз(а).")

        elif choice == "7":
            s = input("Введите элементы множества M1 через пробел: ")
            if s == "":
                M1 = set()
            else:
                M1 = set(s.split())
            M2 = set()
            for e in lst:
                try:
                    M2.add(str(e))
                except Exception:
                    pass
            sym_diff = (M1 ^ M2)
            print("M1 =", M1)
            print("M2 =", M2)
            print("Симметрическая разница M1 и M2 =", sym_diff)

        elif choice == "8":
            d = {}
            for i in range(len(lst)):
                d[i + 1] = lst[i]

            print("Словарь:")
            for k, v in d.items():
                print(f"{k}: {v}")
            print("\nЭлементы словаря с нечетными значениями ключа:")
            for k, v in d.items():
                if k % 2 == 1:
                    print(f"{k}: {v}")

        elif choice == "9":
            print("Выход в главное меню.")
            break
        else:
            print("Неверный выбор, попробуйте ещё раз.")


def part3_areas():
    while True:
        print("\nВыберите фигуру:")
        print("S - площадь квадрата")
        print("T - площадь трапеции")
        print("P - площадь параллелограмма")
        print("E - выход в главное меню")
        choice = input("Ваш выбор (S/T/P/E): ").upper()

        if choice == "S":
            a_str = input("Введите сторону квадрата: ")
            try:
                a = float(a_str)
                if a <= 0:
                    print("Error: сторона должна быть положительной.")
                else:
                    area = a * a
                    print(f"Площадь квадрата: {area}")
            except ValueError:
                print("Error: введено не число.")

        elif choice == "T":
            a_str = input("Введите первую основу трапеции: ")
            b_str = input("Введите вторую основу трапеции: ")
            h_str = input("Введите высоту трапеции: ")
            try:
                a = float(a_str)
                b = float(b_str)
                h = float(h_str)
                if h <= 0:
                    raise ValueError
                else:
                    area = (a + b) / 2.0 * h
                    print(f"Площадь трапеции: {area}")
            except ValueError:
                print("Error: введены неверные числа.")

        elif choice == "P":
            base_str = input("Введите основание параллелограмма: ")
            h_str = input("Введите высоту (положительное число): ")
            try:
                base = float(base_str)
                h = float(h_str)
                if h <= 0:
                    print("Error: высота должна быть положительной.")
                else:
                    area = base * h
                    print(f"Площадь параллелограмма: {area}")
            except ValueError:
                print("Error: введены неверные числа.")

        elif choice == "E":
            print("Выход в главное меню.")
            break

        else:
            print("Error: неверный пункт меню. Введите S, T, P или E.")


def main_menu():
    while True:
        print("\n==== Лабораторная работа — Главное меню ====")
        print("1) Часть 1: вычисление выражения")
        print("2) Часть 2: работа со списком и структурами")
        print("3) Часть 3: вычисление площадей фигур")
        print("4) Выход из программы")
        sel = input("Выберите пункт (1-4): ")
        if sel == "1":
            part1_expression()
        elif sel == "2":
            part2_list_manager()
        elif sel == "3":
            part3_areas()
        elif sel == "4":
            print("Выход.")
            sys.exit(0)
        else:
            print("Неверный выбор (1-4)")


if __name__ == "__main__":
    main_menu()
