# -*- coding: utf-8 -*-
"""
Dibujo de la red de flujo del spec SPEC-kiro en SVG puro (sin numpy ni
matplotlib). Reproduce la MISMA geometria y los MISMOS resultados que
flow_net.py (Nf=4, Nd=24, 10 puntos rojos, datum en la roca).

Se incluye como respaldo para entornos sin matplotlib. flow_net.py sigue
siendo el archivo oficial del spec; este solo cambia el motor de dibujo.

Salida: red_de_flujo.svg
"""
import math

# ---------------- DATOS DEL ENUNCIADO (identicos a flow_net.py) ----------
A, B = 15.0, 20.0
D, C = 19.0, 6.0
E = 21.0
SL_UP, SL_DN = 3.0, 2.0
K = 2.5e-5
GW = 9.81
NF, ND = 4, 24
N_PTS = 10

# ---------------- CALCULOS ----------------
L = SL_UP * B + A + SL_DN * B
H_UP, H_DN = E + D, E + C
h = H_UP - H_DN
dh = h / ND
FF = NF / ND
q = K * h * FF
cell = E / NF
L_EFF = ND * cell
OFF = (L_EFF - L) / 2


def drop(x):
    i = h / L_EFF
    if x <= 0:
        return 0.0
    if x >= L:
        return h
    if x <= L / 2:
        return i * (x + OFF)
    return h - i * (L - x + OFF)


def eq_base(k):
    kk = min(k, ND - k)
    x = max(kk * cell - OFF, 1.0)
    return x if k <= ND / 2 else L - x


def eq_shift(k):
    kk = min(k, ND - k)
    s = -8.0 * math.exp(-(kk - 1) / 3.2)
    return s if k <= ND / 2 else -s


def bez(p0, p1, p2, p3, n=40):
    pts = []
    for q_ in range(n):
        t = q_ / (n - 1)
        mt = 1 - t
        x = (mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
             + 3 * mt * t**2 * p2[0] + t**3 * p3[0])
        y = (mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
             + 3 * mt * t**2 * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


def flow_line(j):
    d = j * cell
    f = j / NF
    r = min(6.5 * (f / (1 - f)) ** 0.75, 14.0)
    xc = 13.3
    left = bez((-r, 0), (-r, -0.5 * d), (-r + (xc + r) * 0.45, -d), (xc, -d))
    right = bez((L - xc, -d), (L + r - (xc + r) * 0.45, -d),
                (L + r, -0.5 * d), (L + r, 0))
    return left + right


xs = [L * k / (N_PTS - 1) for k in range(N_PTS)]
Hv = [H_UP - drop(x) for x in xs]

# ---------------- MAPEO MUNDO -> PIXEL ----------------
W, Hpx = 1150, 620
mL, mR, mT, mB = 60, 40, 70, 60
XMIN, XMAX = -22.0, L + 22.0
YMIN, YMAX = -E - 6.0, B + 6.0
s = min((W - mL - mR) / (XMAX - XMIN), (Hpx - mT - mB) / (YMAX - YMIN))


def PX(x): return mL + (x - XMIN) * s
def PY(y): return Hpx - mB - (y - YMIN) * s


def A_(kw): return " ".join('%s="%s"' % (a.replace("_", "-"), v)
                            for a, v in kw.items())


def rect(x, y, w, hh, **kw):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" %s/>' % (
        PX(x), PY(y), w * s, hh * s, A_(kw))


def poly(pts, **kw):
    p = " ".join("%.1f,%.1f" % (PX(a), PY(b)) for a, b in pts)
    return '<polygon points="%s" %s/>' % (p, A_(kw))


def pline(pts, **kw):
    p = " ".join("%.1f,%.1f" % (PX(a), PY(b)) for a, b in pts)
    return '<polyline points="%s" fill="none" %s/>' % (p, A_(kw))


def line(x1, y1, x2, y2, **kw):
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (
        PX(x1), PY(y1), PX(x2), PY(y2), A_(kw))


def txt(x, y, t, size=12, anchor="start", color="#000", weight="normal", rot=None):
    tr = (' transform="rotate(%.0f %.1f %.1f)"' % (rot, PX(x), PY(y))) if rot else ""
    return ('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" fill="%s" '
            'font-family="Helvetica,Arial" font-weight="%s"%s>%s</text>' % (
                PX(x), PY(y), size, anchor, color, weight, tr, t))


e = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
     'viewBox="0 0 %d %d">' % (W, Hpx, W, Hpx),
     '<rect x="0" y="0" width="%d" height="%d" fill="white"/>' % (W, Hpx)]

# Suelo permeable y roca
e.append(rect(XMIN, -E, XMAX - XMIN, E, fill="#E6DAC0"))
e.append(rect(XMIN, -E - 6, XMAX - XMIN, 6, fill="#C9C7BE"))

# Agua aguas arriba y aguas abajo
e.append(poly([(XMIN, D), (SL_UP * D, D), (0, 0), (XMIN, 0)], fill="#B5D4F4"))
e.append(poly([(L - SL_DN * C, C), (XMAX, C), (XMAX, 0), (L, 0)], fill="#B5D4F4"))

# Presa
e.append(poly([(0, 0), (SL_UP * B, B), (SL_UP * B + A, B), (L, 0)],
              fill="#B4B2A9", stroke="#444441", stroke_width="1.2"))

# Equipotenciales
for k in range(1, ND):
    xb = eq_base(k)
    xr = xb + eq_shift(k)
    c = bez((xb, 0), (xb, -0.466 * E), (xr, -0.74 * E), (xr, -E))
    e.append(pline(c, stroke="#1D9E75", stroke_width="0.8"))

# Lineas de flujo
for j in range(1, NF):
    e.append(pline(flow_line(j), stroke="#185FA5", stroke_width="1.4"))
e.append(line(XMIN, -E, XMAX, -E, stroke="#185FA5", stroke_width="1.4"))  # roca
e.append(line(0, 0, L, 0, stroke="#2C2C2A", stroke_width="2.8"))          # base

# Puntos rojos numerados
for n, x in enumerate(xs, 1):
    cx, cy = PX(x), PY(0.0)
    e.append('<circle cx="%.1f" cy="%.1f" r="9" fill="#E24B4A" '
             'stroke="#A32D2D" stroke-width="1.3"/>' % (cx, cy))
    e.append('<text x="%.1f" y="%.1f" font-size="9" fill="white" '
             'text-anchor="middle" font-family="Helvetica,Arial" '
             'font-weight="bold">%d</text>' % (cx, cy + 3, n))
    # carga total encima
    e.append('<text x="%.1f" y="%.1f" font-size="9" fill="#A32D2D" '
             'text-anchor="middle" font-family="Helvetica,Arial">H=%.1f</text>'
             % (cx, cy - 13, Hv[n - 1]))

# Rotulos de carga de borde
e.append(txt(XMIN + 1, D + 1.5, "H = %.0f m" % H_UP, 13, color="#124"))
e.append(txt(XMAX - 1, C + 1.5, "H = %.0f m" % H_DN, 13, anchor="end", color="#124"))
e.append(txt(L / 2, B * 0.4, "Presa impermeable", 13, anchor="middle"))
e.append(txt(L / 2, -E - 3.5, "Roca impermeable", 11, anchor="middle"))
e.append(txt(XMIN + 1, -E / 2, "Suelo permeable (E=%.0f m)" % E, 11, color="#7a5c1e"))

# Ejes
e.append(line(XMIN, YMIN, XMIN, YMAX, stroke="black", stroke_width="1"))
e.append(line(XMIN, YMIN, XMAX, YMIN, stroke="black", stroke_width="1"))
zt = int(YMIN // 5) * 5
while zt <= YMAX:
    if YMIN <= zt <= YMAX:
        e.append(line(XMIN, zt, XMIN + 1.2, zt, stroke="black", stroke_width="0.8"))
        e.append(txt(XMIN - 1.2, zt - 0.5, "%d" % zt, 9, anchor="end"))
    zt += 5
for xt in range(0, int(L) + 1, 20):
    e.append(line(xt, YMIN, xt, YMIN + 1.2, stroke="black", stroke_width="0.8"))
    e.append(txt(xt, YMIN - 2.6, "%d" % xt, 9, anchor="middle"))
e.append(txt((W / 2 - mL) / s + XMIN, YMIN - 5.2, "x [m] (origen en pie aguas arriba)",
             13, anchor="middle"))
e.append('<text x="16" y="%d" font-size="13" text-anchor="middle" '
         'font-family="Helvetica,Arial" transform="rotate(-90 16 %d)">'
         'z [m] (datum = roca, z=0 en y=-E)</text>' % (Hpx // 2, Hpx // 2))

# Titulo + leyenda
e.append('<text x="%d" y="26" font-size="16" text-anchor="middle" '
         'font-weight="bold" font-family="Helvetica,Arial">'
         'Red de flujo bajo presa de tierra impermeable</text>' % (W // 2))
e.append('<text x="%d" y="46" font-size="12" text-anchor="middle" '
         'font-family="Helvetica,Arial">Nf=%d, Nd=%d  |  q = k*h*Nf/Nd = '
         '%.3e m3/s por m  |  dh=%.4f m</text>' % (W // 2, NF, ND, q, dh))

lx, ly = W - 260, 78
leg = [("#B5D4F4", "Agua (embalse / aguas abajo)"),
       ("#E24B4A", "Punto rojo (1..10)"),
       ("#185FA5", "Lineas de flujo (Nf=4)"),
       ("#1D9E75", "Equipotenciales (Nd=24)")]
e.append('<rect x="%d" y="%d" width="248" height="%d" fill="white" '
         'stroke="#888" stroke-width="0.8" opacity="0.95"/>'
         % (lx - 10, ly - 18, len(leg) * 20 + 14))
for i, (col, lab) in enumerate(leg):
    yy = ly + i * 20
    e.append('<rect x="%d" y="%d" width="16" height="10" fill="%s"/>' % (lx, yy - 9, col))
    e.append('<text x="%d" y="%d" font-size="11" font-family="Helvetica,Arial">'
             '%s</text>' % (lx + 22, yy, lab))

e.append('</svg>')

with open("red_de_flujo.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(e))
print("[OK] red_de_flujo.svg generado (motor SVG puro, mismos datos del spec).")
print("L=%.0f h=%.0f dh=%.4f Ff=%.4f q=%.3e" % (L, h, dh, FF, q))
