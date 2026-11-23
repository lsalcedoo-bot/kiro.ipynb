# -*- coding: utf-8 -*-
"""
Diagrama de subpresiones u(x) bajo la base de la presa (ampliacion opcional
del spec), en SVG puro (sin numpy ni matplotlib).

u(x) = gamma_w * (H(x) - z), con z = E (datum en la roca). Es la presion de
poros que empuja la base de la presa hacia arriba. Se calcula la resultante
U_total (kN por metro de presa) y su punto de aplicacion por integracion
trapezoidal.

Salida: subpresiones.svg
"""
import math

# ---------------- DATOS (identicos a flow_net.py) ----------------
A, B = 15.0, 20.0
D, C = 19.0, 6.0
E = 21.0
SL_UP, SL_DN = 3.0, 2.0
K = 2.5e-5
GW = 9.81
NF, ND = 4, 24
N_PTS = 10

L = SL_UP * B + A + SL_DN * B
H_UP, H_DN = E + D, E + C
h = H_UP - H_DN
dh = h / ND
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


def u_of(x):
    """Subpresion en kPa."""
    return GW * (H_UP - drop(x) - E)


# Muestreo fino para la curva e integracion trapezoidal
N = 200
xf = [L * k / (N - 1) for k in range(N)]
uf = [u_of(x) for x in xf]

U_tot = 0.0
mom = 0.0
for k in range(N - 1):
    dx = xf[k + 1] - xf[k]
    U_tot += 0.5 * (uf[k] + uf[k + 1]) * dx
    mom += 0.5 * (xf[k] * uf[k] + xf[k + 1] * uf[k + 1]) * dx
x_centroide = mom / U_tot

# Puntos rojos
xs = [L * k / (N_PTS - 1) for k in range(N_PTS)]
us = [u_of(x) for x in xs]
umax = max(uf)

# ---------------- MAPEO MUNDO -> PIXEL ----------------
W, Hpx = 1100, 470
mL, mR, mT, mB = 70, 40, 60, 70
xmin, xmax = 0.0, L
ymin, ymax = 0.0, umax * 1.18
sx = (W - mL - mR) / (xmax - xmin)
sy = (Hpx - mT - mB) / (ymax - ymin)


def PX(x): return mL + (x - xmin) * sx
def PY(y): return Hpx - mB - (y - ymin) * sy


def A_(kw): return " ".join('%s="%s"' % (a.replace("_", "-"), v)
                            for a, v in kw.items())


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

# Area de subpresion (relleno)
area_pts = ["%.1f,%.1f" % (PX(xf[0]), PY(0.0))]
area_pts += ["%.1f,%.1f" % (PX(xf[k]), PY(uf[k])) for k in range(N)]
area_pts += ["%.1f,%.1f" % (PX(xf[-1]), PY(0.0))]
e.append('<polygon points="%s" fill="#8FB7E8" fill-opacity="0.6" '
         'stroke="none"/>' % " ".join(area_pts))
# Curva u(x)
curve = " ".join("%.1f,%.1f" % (PX(xf[k]), PY(uf[k])) for k in range(N))
e.append('<polyline points="%s" fill="none" stroke="#185FA5" '
         'stroke-width="2"/>' % curve)

# Rejilla y ejes
e.append(line(xmin, 0, xmax, 0, stroke="black", stroke_width="1"))
e.append(line(xmin, 0, xmin, ymax, stroke="black", stroke_width="1"))
yt = 0
while yt <= ymax:
    e.append(line(xmin, yt, xmax, yt, stroke="#ccc", stroke_width="0.5"))
    e.append(txt(xmin - 1.5, yt + ymax * 0.01, "%d" % yt, 10, anchor="end"))
    yt += 25
for xt in range(0, int(L) + 1, 20):
    e.append(line(xt, 0, xt, -ymax * 0.015, stroke="black", stroke_width="0.8"))
    e.append(txt(xt, -ymax * 0.05, "%d" % xt, 10, anchor="middle"))

# Linea de la resultante
e.append(line(x_centroide, 0, x_centroide, ymax * 0.95, stroke="#555",
              stroke_width="1.2", stroke_dasharray="6,4"))
e.append(txt(x_centroide, ymax * 0.99, "Resultante x=%.1f m" % x_centroide,
             11, anchor="middle", color="#333"))

# Puntos rojos con su valor
for n, (x, u) in enumerate(zip(xs, us), 1):
    cx, cy = PX(x), PY(u)
    e.append('<circle cx="%.1f" cy="%.1f" r="5" fill="#E24B4A" '
             'stroke="#A32D2D" stroke-width="1"/>' % (cx, cy))
    e.append('<text x="%.1f" y="%.1f" font-size="9" text-anchor="middle" '
             'fill="#A32D2D" font-family="Helvetica,Arial">%.0f</text>'
             % (cx, cy - 8, u))

# Titulos
e.append(txt((xmin + xmax) / 2, -ymax * 0.11,
             "x [m]  (base de la presa, origen en el pie aguas arriba)",
             13, anchor="middle"))
e.append('<text x="18" y="%d" font-size="13" text-anchor="middle" '
         'font-family="Helvetica,Arial" transform="rotate(-90 18 %d)">'
         'Subpresion u [kPa]</text>' % (Hpx // 2, Hpx // 2))
e.append('<text x="%d" y="26" font-size="15" text-anchor="middle" '
         'font-weight="bold" font-family="Helvetica,Arial">'
         'Diagrama de subpresiones bajo la base de la presa</text>' % (W // 2))
e.append('<text x="%d" y="45" font-size="12" text-anchor="middle" '
         'font-family="Helvetica,Arial">U_total = %.0f kN por metro de presa'
         '  |  aplicada en x = %.1f m</text>' % (W // 2, U_tot, x_centroide))

e.append('</svg>')
with open("subpresiones.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(e))

print("[OK] subpresiones.svg generado.")
print("U_total = %.1f kN por metro de presa | resultante en x = %.1f m"
      % (U_tot, x_centroide))
print("u en puntos rojos (kPa):", ", ".join("%.1f" % v for v in us))
