from PIL import Image
import math

def point_in_polygon(x, y, polygon_points):
    inside = False
    n = len(polygon_points)
    for i in range(n):
        x1, y1 = polygon_points[i]
        x2, y2 = polygon_points[(i + 1) % n]
        if ((y1 > y) != (y2 > y)):
            x_at_y = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-10) + x1
            if x < x_at_y:
                inside = not inside
    return inside


def segments_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

def clamp8(x):
    if x < 0: return 0
    if x > 255: return 255
    return int(x + 0.5)


def mix_rgb(a, b, t):
    return (
        clamp8(a[0] + (b[0] - a[0]) * t),
        clamp8(a[1] + (b[1] - a[1]) * t),
        clamp8(a[2] + (b[2] - a[2]) * t),
    )


def gradient_at(palette, t):
    if not palette:
        return (255, 255, 255)
    if t <= 0:
        return palette[0]
    if t >= 1:
        return palette[-1]
    pos = t * (len(palette) - 1)
    i = int(pos)
    frac = pos - i
    return mix_rgb(palette[i], palette[i + 1], frac)


def draw_line(img, x0, y0, x1, y1, color):
    dx, dy = x1 - x0, y1 - y0
    sx = 1 if dx > 0 else -1 if dx < 0 else 0
    sy = 1 if dy > 0 else -1 if dy < 0 else 0
    dx, dy = abs(dx), abs(dy)

    if dx >= dy:
        step_x, step_y, short, long = sx, 0, dy, dx
    else:
        step_x, step_y, short, long = 0, sy, dx, dy

    x, y = x0, y0
    err = 0
    img.putpixel((x, y), color)
    for _ in range(long):
        err += 2 * short
        if err > long:
            err -= 2 * long
            x += sx
            y += sy
        else:
            x += step_x
            y += step_y
        img.putpixel((x, y), color)


def draw_line_gradient(img, x0, y0, x1, y1, palette):
    dx, dy = x1 - x0, y1 - y0
    sx = 1 if dx > 0 else -1 if dx < 0 else 0
    sy = 1 if dy > 0 else -1 if dy < 0 else 0
    dx, dy = abs(dx), abs(dy)

    if dx >= dy:
        step_x, step_y, short, long = sx, 0, dy, dx
    else:
        step_x, step_y, short, long = 0, sy, dx, dy

    x, y = x0, y0
    err = 0
    for i in range(long + 1):
        t = 0 if long == 0 else i / float(long)
        img.putpixel((x, y), gradient_at(palette, t))
        err += 2 * short
        if err > long:
            err -= 2 * long
            x += sx
            y += sy
        else:
            x += step_x
            y += step_y


def draw_line_dashed(img, x0, y0, x1, y1, color, dash_segments=11):
    dx, dy = x1 - x0, y1 - y0
    sx = 1 if dx > 0 else -1 if dx < 0 else 0
    sy = 1 if dy > 0 else -1 if dy < 0 else 0
    dx, dy = abs(dx), abs(dy)

    if dx >= dy:
        step_x, step_y, short, long = sx, 0, dy, dx
    else:
        step_x, step_y, short, long = 0, sy, dx, dy

    x, y = x0, y0
    err = 0
    seg_len = max(1.0, long / float(dash_segments))

    for i in range(long + 1):
        seg_index = int(i / seg_len)
        if seg_index % 2 == 0 and seg_index < dash_segments:
            img.putpixel((x, y), color)

        err += 2 * short
        if err > long:
            err -= 2 * long
            x += sx
            y += sy
        else:
            x += step_x
            y += step_y


def draw_line_dashed_palette(img, x0, y0, x1, y1, palette, dash_segments=12):
    dx, dy = x1 - x0, y1 - y0
    sx = 1 if dx > 0 else -1 if dx < 0 else 0
    sy = 1 if dy > 0 else -1 if dy < 0 else 0
    dx, dy = abs(dx), abs(dy)

    if dx >= dy:
        step_x, step_y, short, long = sx, 0, dy, dx
    else:
        step_x, step_y, short, long = 0, sy, dx, dy

    x, y = x0, y0
    err = 0
    seg_len = max(1.0, long / float(dash_segments))

    for i in range(long + 1):
        seg_index = int(i / seg_len)
        t_seg = min(1.0, (seg_index + 0.5) / max(1, dash_segments - 1))
        if seg_index % 2 == 0 and seg_index < dash_segments:
            img.putpixel((x, y), gradient_at(palette, t_seg))

        err += 2 * short
        if err > long:
            err -= 2 * long
            x += sx
            y += sy
        else:
            x += step_x
            y += step_y


def draw_circle_8(img, cx, cy, r, color):
    d = 3 - 2 * r
    x, y = 0, r
    while y >= x:
        pts = [
            (cx + x, cy + y), (cx + x, cy - y),
            (cx - x, cy + y), (cx - x, cy - y),
            (cx + y, cy + x), (cx + y, cy - x),
            (cx - y, cy + x), (cx - y, cy - x),
        ]
        for p in pts:
            img.putpixel(p, color)

        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * x - 4 * y + 10
            y -= 1
        x += 1


def draw_circle_8_gradient(img, cx, cy, r, palette):
    d = 3 - 2 * r
    x, y = 0, r
    def put(dx, dy):
        ang = math.atan2(dy, dx)
        if ang < 0:
            ang += 2 * math.pi
        t = ang / (2 * math.pi)
        img.putpixel((cx + dx, cy + dy), gradient_at(palette, t))

    while y >= x:
        put( x,  y); put( x, -y)
        put(-x,  y); put(-x, -y)
        put( y,  x); put( y, -x)
        put(-y,  x); put(-y, -x)

        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * x - 4 * y + 10
            y -= 1
        x += 1


def draw_circle_4_dashed(img, cx, cy, r, color, sector_deg=30):
    d = 2 - 2 * r
    x, y = 0, r
    while y >= 0:
        for dx, dy in ((x, y), (x, -y), (-x, y), (-x, -y)):
            ang = math.degrees(math.atan2(dy, dx))
            if ang < 0:
                ang += 360
            if int(ang // sector_deg) % 2 == 0:
                img.putpixel((cx + dx, cy + dy), color)

        if d < 0:
            err = 2 * d + 2 * y - 1
            if err <= 0:
                x += 1
                d += 2 * x + 1
            else:
                x += 1
                y -= 1
                d += 2 * x - 2 * y + 2
        elif d > 0:
            err = 2 * d - 2 * x - 1
            if err <= 0:
                x += 1
                y -= 1
                d += 2 * x - 2 * y + 2
            else:
                y -= 1
                d -= 2 * y + 1
        else:
            x += 1
            y -= 1
            d += 2 * x - 2 * y + 2


def draw_circle_4_dashed_palette(img, cx, cy, r, palette, sector_deg=30):
    d = 2 - 2 * r
    x, y = 0, r
    while y >= 0:
        for dx, dy in ((x, y), (x, -y), (-x, y), (-x, -y)):
            ang = math.atan2(dy, dx)
            if ang < 0:
                ang += 2 * math.pi
            if int((ang * 180.0 / math.pi) // sector_deg) % 2 == 0:
                t = ang / (2 * math.pi)
                img.putpixel((cx + dx, cy + dy), gradient_at(palette, t))

        if d < 0:
            err = 2 * d + 2 * y - 1
            if err <= 0:
                x += 1
                d += 2 * x + 1
            else:
                x += 1
                y -= 1
                d += 2 * x - 2 * y + 2
        elif d > 0:
            err = 2 * d - 2 * x - 1
            if err <= 0:
                x += 1
                y -= 1
                d += 2 * x - 2 * y + 2
            else:
                y -= 1
                d -= 2 * y + 1
        else:
            x += 1
            y -= 1
            d += 2 * x - 2 * y + 2


def draw_circle_8_arc_225(img, cx, cy, r, color):
    d = 3 - 2 * r
    x, y = 0, r
    while y >= x:
        pts = [
            (cx + x, cy + y),
            (cx - x, cy + y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx - y, cy - x),
        ]
        for p in pts:
            img.putpixel(p, color)

        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * x - 4 * y + 10
            y -= 1
        x += 1

def polygon_edges(points):
    edges = []
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        if a[1] != b[1]:
            edges.append((a, b))
    return tuple(edges)


def edge_x_at_y(edge, y):
    (x0, y0), (x1, y1) = edge
    t = (y - y0) / (y1 - y0)
    x = int(t * x1 + (1 - t) * x0)
    return (x, y)


def intersections_on_scanline(edges, y):
    xs = []
    for e in edges:
        y_min = min(e[0][1], e[1][1])
        y_max = max(e[0][1], e[1][1])
        if y_min <= y <= y_max:
            pt = edge_x_at_y(e, y)
            if pt not in xs:
                xs.append(pt)
    xs.sort(key=lambda p: p[0])
    return xs


def draw_line_outside_polygon(img, x0, y0, x1, y1, color, polygon):
    hits = []
    for i in range(len(polygon)):
        a = polygon[i]
        b = polygon[(i + 1) % len(polygon)]
        hit = segments_intersection((x0, y0), (x1, y1), a, b)
        if hit:
            hits.append(hit)

    hits.extend([(x0, y0), (x1, y1)])
    hits.sort(key=lambda p: (p[0] - x0) ** 2 + (p[1] - y0) ** 2)

    for i in range(len(hits) - 1):
        ax, ay = hits[i]
        bx, by = hits[i + 1]
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        if not point_in_polygon(mx, my, polygon):
            draw_line(img, int(ax), int(ay), int(bx), int(by), color)


def fill_texture_outside_circle(img, inters, texture, circle_center, circle_radius):
    tex_w, tex_h = texture.size
    cx, cy = circle_center
    r2 = circle_radius * circle_radius

    ax, ay = circle_center
    txc, tyc = tex_w // 2, tex_h // 2

    for i in range(0, len(inters) - 1, 2):
        x_start, y = inters[i]
        x_end, _ = inters[i + 1]

        if 0 <= y < img.height:
            for x in range(max(0, x_start), min(img.width, x_end)):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) >= r2:
                    tx = (x - ax + txc) % tex_w
                    ty = (y - ay + tyc) % tex_h
                    img.putpixel((x, y), texture.getpixel((tx, ty)))


def main():

    # Красивые цвета
    palette_lines = [(255, 88, 93), (255, 160, 122), (255, 214, 165), (170, 215, 255)]
    palette_dash = [(116, 235, 213), (172, 182, 229), (255, 175, 204)]
    palette_circ = [(72, 209, 204), (65, 105, 225), (186, 85, 211), (255, 105, 180)]
    palette_arc = [(255, 199, 125), (255, 140, 0), (255, 88, 93)]

    width, height = 200, 200
    bg = (8, 10, 14)
    white = (240, 242, 245)

    triangle = [(60, 130), (100, 50), (140, 130)]
    circle_center = (100, 100)
    circle_radius = 20
    outer_radius = 90

    texture_path = "imageForRK.png"

    img = Image.new("RGB", (width, height), bg)

    # Треугольник
    draw_line_gradient(img, 60, 130, 100, 50, palette_lines)
    draw_line_gradient(img, 60, 130, 140, 130, palette_lines)
    draw_line_gradient(img, 100, 50, 140, 130, palette_lines)

    # Линия через треугольник
    draw_line_outside_polygon(img, 0, 6, 199, 110, white, triangle)

    # Пунктирные рёбра
    draw_line_dashed_palette(img, 56, 133, 100, 45, palette_dash, dash_segments=12)
    draw_line_dashed_palette(img, 56, 133, 144, 133, palette_dash, dash_segments=12)
    draw_line_dashed_palette(img, 100, 45, 144, 133, palette_dash, dash_segments=12)

    # Окружности
    draw_circle_8(img, circle_center[0], circle_center[1], circle_radius, white)
    draw_circle_4_dashed_palette(img, circle_center[0], circle_center[1], 17, palette_circ, sector_deg=30)
    draw_circle_8_arc_225(img, circle_center[0], circle_center[1], outer_radius, palette_arc[-1])

    # Заливка снаружи круга внутри треугольника
    edges = polygon_edges(triangle)
    texture = Image.open(texture_path).convert("RGB")
    y_min = min(p[1] for p in triangle)
    y_max = max(p[1] for p in triangle)
    for y in range(y_min, y_max):
        xs = intersections_on_scanline(edges, y)
        if len(xs) >= 2:
            fill_texture_outside_circle(img, xs, texture, circle_center, circle_radius)

    draw_circle_8_gradient(img, circle_center[0], circle_center[1], circle_radius, palette_circ)
    draw_line_gradient(img, 60, 130, 100, 50, palette_lines)

    img.show()
    img.save("RK.png")

if __name__ == "__main__":
    main()

