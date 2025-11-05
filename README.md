# РК1 по 3D моделированию студента ИУ8-52 Захарова Ивана

## Структура репозитория

```
RK.py            # основной скрипт с кодом
imageForRK.jpg   # исходная текстура для заливки
RK.png           # готовый результат (вывод программы)
```

## Структура кода

Один файл со всеми функциями и `main()`.

Блоки:

1. **Геометрия**: `point_in_polygon`, `segments_intersection`.
2. **Цвет/палитры**: `clamp8`, `mix_rgb`, `gradient_at` (линейная интерполяция RGB, выбор цвета по t∈[0,1]).
3. **Линии**: `draw_line`, `draw_line_gradient`, `draw_line_dashed`, `draw_line_dashed_palette`.
4. **Окружности/дуги**: `draw_circle_8`, `draw_circle_8_gradient`, `draw_circle_4_dashed`, `draw_circle_4_dashed_palette`, `draw_circle_8_arc_225`.
5. **Многоугольники/сканлайны**: `polygon_edges`, `edge_x_at_y`, `intersections_on_scanline`, `draw_line_outside_polygon`.
6. **Текстура**: `fill_texture_outside_circle` — заливка текстурой вне круга.
7. **main()**: сборка сцены, вызовы функций, `img.show()` и сохранение **RK.png**.

---

### Геометрия

* `point_in_polygon(x, y, polygon_points)` — опредление принадлежности к многоугольнику.
* `segments_intersection(p1, p2, p3, p4)` — точка пересечения отрезков или `None` (для параллельных/непересекающихся).

### Цвет и палитры

* `clamp8(x)` — ограничение диапазона 0..255.
* `mix_rgb(a, b, t)` — интерполяция двух цветов `a` и `b` по параметру `t`.
* `gradient_at(palette, t)` — вернуть цвет из списка опорных RGB по `t ∈ [0,1]` (между соседними опорными цветами — линейная интерполяция).

### Линии

* `draw_line(img, x0, y0, x1, y1, color)` — линия Брезенхэма (сплошная).
* `draw_line_gradient(img, x0, y0, x1, y1, palette)` — линия, цвет плавно меняется от начала к концу.
* `draw_line_dashed(img, x0, y0, x1, y1, color, dash_segments=11)` — пунктир, реализованный делением «длины хода» на сегменты.
* `draw_line_dashed_palette(img, x0, y0, x1, y1, palette, dash_segments=12)` — пунктир, где цвет сегмента берётся из палитры.

### Окружности и дуги

* `draw_circle_8(img, cx, cy, r, color)` — окружность Брезенхэма (8‑симметрийная).
* `draw_circle_8_gradient(img, cx, cy, r, palette)` — окружность с градиентом по **углу** (через `atan2`).
* `draw_circle_4_dashed(img, cx, cy, r, color, sector_deg=30)` — пунктир по секторам (пример: 30° рисуем / 30° пропускаем).
* `draw_circle_4_dashed_palette(img, cx, cy, r, palette, sector_deg=30)` — то же, но цвет сектора задаётся палитрой по углу.
* `draw_circle_8_arc_225(img, cx, cy, r, color)` — частичная окружность, заданные октанты.

### Многоугольники и сканлайны

* `polygon_edges(points)` — подготовка рёбер (горизонтальные исключаем — удобнее для сканлайнов).
* `edge_x_at_y(edge, y)` — пересечение ребра с горизонталью `y`.
* `intersections_on_scanline(edges, y)` — отсортированные по X точки пересечений для строки `y`.
* `draw_line_outside_polygon(img, x0, y0, x1, y1, color, polygon)` — разделяем исходный отрезок по пересечениям с полигоном и рисуем только те подпары, где средняя точка **снаружи**.

### Текстура

* `fill_texture_outside_circle(img, inters, texture, circle_center, circle_radius)` — заливает текстуру, но только там, где точка находится **вне** круга. Центр текстуры совмещён с `circle_center` (при необходимости можно сместить, изменив внутри функции `ax, ay`).

### main()

* Задаёт палитры, геометрию сцены, путь к текстуре (`texture_path = "rock.png"`).
* Вызывает функции в нужном порядке, формируя итоговую картинку.
* Показывает окно предпросмотра `img.show()` и сохраняет результат в **RK.png**:

  ```python
  img.show()
  img.save("RK.png")
  ```

---
