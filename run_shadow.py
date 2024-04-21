#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer
from shadow.polyedr import Polyedr

tk = TkDrawer()
try:
    for name in ["ccc", "cube", "box", "king", "cow"]:
        print("=============================================================")
        print(f"Начало работы с полиэдром '{name}'")
        start_time = time()
        temp_poly = Polyedr(f"data/{name}.geom")
        temp_poly.draw(tk)
        delta_time = time() - start_time
        temp = temp_poly.character()
        delta_time_2 = time() - start_time - delta_time
        print(f"Изображение полиэдра '{name}' заняло {delta_time} сек.")
        print(f"Характеристика полиэдра{temp}")
        print(f"Вычисление характеристики заняло {delta_time_2} сек.")
        input("Hit 'Return' to continue -> ")
except (EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()
