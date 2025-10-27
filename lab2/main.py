from math import sqrt, cos, sin, exp, log, fabs, isfinite
from ast import literal_eval

err    = lambda msg: (_ for _ in ()).throw(ValueError(msg))
ensure = lambda cond, msg: cond or err(msg)

# ============ ЗАДАНИЕ 1 ============
# sqrt(|cos x|**n + exp(n**3)/ln(x) + |sin x|**(1/n))
to_float = float
x = to_float(input("Задание 1 — x (>0, x!=1): ").strip())
n = to_float(input("Задание 1 — n (n!=0): ").strip())

all(map(lambda f: f(x, n), (
    lambda x, n: x > 0,                        # ln(x)
    lambda x, n: log(x) != 0.0,                # x != 1
    lambda x, n: n != 0,                       # 1/n
    lambda x, n: (fabs(sin(x)) > 0) or (n > 0),   # 0**(отриц.) запрещено
    lambda x, n: (fabs(cos(x)) > 0) or (n >= 0),  # 0**(отриц.) запрещено
))) or err("Ошибка (Задание 1): значения вне области определения.")

res1 = sqrt(
    pow(fabs(cos(x)), n) +
    exp(n**3) / log(x) +
    pow(fabs(sin(x)), 1.0 / n)
)
print("Задание 1 — результат:", res1)

# ============ ЗАДАНИЕ 2 ============
# Коды: S — квадрат (a), T — трапеция (a,b,h), P — параллелограмм (a,h), E — выход.
# Входной список L: [ [коды], [a...], [b...], [h...] ]
L = literal_eval(input(
    "Задание 2 — список L (напр.: [['S','T','P','T','E'],[2,3,4,5,0],[0,7,6,8,0],[0,4,3,2,0]]): "
).strip())

ensure(isinstance(L, list) and (len(L) >= 2) and isinstance(L[0], list)
       and all(map(lambda r: isinstance(r, list), L[1:])),
       "Ошибка (Задание 2): ожидается [ [коды], [a...], [b...], [h...] ].")

codes, streams = L[0], L[1:]
ensure(len(streams) >= 3, "Ошибка (Задание 2): требуется минимум три числовых потока: a, b, h.")

findE = "".join(map(str, codes)).find('E')
stop  = (lambda i: (i, len(codes))[i == -1])(findE)

ensure(all(map(lambda arr: len(arr) >= stop, streams)),
       "Ошибка (Задание 2): недостаточно числовых данных под операции до 'E'.")

valid_codes = set("STP")
ensure(all(map(lambda c: c in valid_codes, codes[:stop])),
       "Ошибка (Задание 2): встречен неизвестный код фигуры (допустимы: S, T, P, E).")

need_mask = { 'S': (1,0,0), 'T': (1,1,1), 'P': (1,0,1) }
need_for_i = lambda i: need_mask[codes[i]]

pos = lambda *xs: ensure(
    all(map(lambda t: (t is not None) and isfinite(t) and (t > 0), xs)),
    "Ошибка (Задание 2): параметры должны быть положительными и конечными."
)

check_i = lambda i: pos(*tuple(
    streams[j][i] for j in range(3)
    if need_for_i(i)[j]
))
list(map(check_i, range(stop)))


S = lambda a, *_: a*a
T = lambda a, b, h, *_: (a + b) * h / 2.0
P = lambda a, _, h, *__: a * h
op = {'S': S, 'T': T, 'P': P}

take_i  = lambda i: tuple(map(lambda arr: arr[i], streams[:3]))  # (a,b,h)
apply_i = lambda i: op[codes[i]](*take_i(i))

areas = list(map(apply_i, range(stop)))
print("Задание 2 — площади (по порядку кодов до 'E'):")
print("\n".join(map(str, areas)))
