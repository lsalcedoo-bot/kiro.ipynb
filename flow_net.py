"""
Red de flujo bajo una presa de tierra impermeable (ejercicio 10).
Referencia: Juarez Badillo y Rico, Mecanica de Suelos tomo 2, cap. II.

Uso:  python flow_net.py        (requiere numpy y matplotlib)
Salida: red_de_flujo.png, red_de_flujo.svg y una tabla en consola.
Todas las longitudes en m, k en m/s, presiones en kPa.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# ---------------- DATOS DEL ENUNCIADO ----------------
A, B = 15.0, 20.0          # corona y altura de la presa
D, C = 19.0, 6.0           # agua aguas arriba / aguas abajo (sobre el terreno)
E = 21.0                   # espesor de suelo permeable hasta la roca
SL_UP, SL_DN = 3.0, 2.0    # taludes H:V (3:1 aguas arriba, 2:1 aguas abajo)
K = 2.5e-5                 # permeabilidad (m/s)
GW = 9.81                  # peso especifico del agua (kN/m3), SUPUESTO
NF, ND = 4, 24             # canales de flujo y caidas de potencial
N_PTS = 10                 # puntos rojos sobre la base

# ---------------- CALCULOS (ecs. 2-1 a 2-6 y II-5) ----------------
L = SL_UP * B + A + SL_DN * B           # base de la presa = 115 m
H_UP, H_DN = E + D, E + C               # cargas de borde (datum = roca)
h = H_UP - H_DN                         # perdida total de carga = 13 m
dh = h / ND                             # (2-2) caida por equipotencial
FF = NF / ND                            # (2-5) factor de forma
q = K * h * FF                          # (2-6) caudal por metro de presa
cell = E / NF                           # lado de la celda cuadrada (a = b)
L_EFF = ND * cell                       # longitud efectiva de la red
OFF = (L_EFF - L) / 2                   # efecto de convergencia en los pies


def drop(x):
    """Caidas de carga (m) acumuladas desde aguas arriba, a lo largo de la base."""
    i = h / L_EFF
    x = np.asarray(x, dtype=float)
    d = np.where(x <= L / 2, i * (x + OFF), h - i * (L - x + OFF))
    d = np.where(x <= 0, 0.0, d)
    return np.where(x >= L, h, d)


xs = np.linspace(0, L, N_PTS)
H = H_UP - drop(xs)                     # carga total en cada punto
Z = np.full(N_PTS, E)                   # carga de posicion (datum en la roca)
P = H - Z                               # carga de presion p/gw
U = GW * P                              # presion de poros / subpresion (kPa)
N_CAIDAS = drop(xs) / dh

# ---------------- GEOMETRIA DE LA RED ----------------
def eq_base(k):
    """x (m) donde la equipotencial k corta la base de la presa."""
    kk = min(k, ND - k)
    x = max(kk * cell - OFF, 1.0)
    return x if k <= ND / 2 else L - x


def eq_shift(k):
    """Desplazamiento horizontal de la equipotencial al llegar a la roca."""
    kk = min(k, ND - k)
    s = -8.0 * np.exp(-(kk - 1) / 3.2)
    return s if k <= ND / 2 else -s


def bez(p0, p1, p2, p3, n=40):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def flow_line(j):
    """Linea de flujo j (1..NF-1), desde el terreno aguas arriba hasta aguas abajo."""
    d = j * cell
    f = j / NF
    r = min(6.5 * (f / (1 - f)) ** 0.75, 14.0)       # punto de entrada (m del pie)
    xc = 13.3
    left = bez((-r, 0), (-r, -0.5 * d), (-r + (xc + r) * 0.45, -d), (xc, -d))
    right = bez((L - xc, -d), (L + r - (xc + r) * 0.45, -d), (L + r, -0.5 * d), (L + r, 0))
    return np.vstack([left, right])


# ---------------- DIBUJO ----------------
fig, ax = plt.subplots(figsize=(11, 5.2))
XMIN, XMAX = -22, L + 22

ax.add_patch(Rectangle((XMIN, -E), XMAX - XMIN, E, fc="#E6DAC0", ec="none"))
ax.add_patch(Rectangle((XMIN, -E - 6), XMAX - XMIN, 6, fc="#C9C7BE", ec="none"))
ax.add_patch(Polygon([(XMIN, D), (SL_UP * D, D), (0, 0), (XMIN, 0)], fc="#B5D4F4", ec="none"))
ax.add_patch(Polygon([(L - SL_DN * C, C), (XMAX, C), (XMAX, 0), (L, 0)], fc="#B5D4F4", ec="none"))
ax.add_patch(Polygon([(0, 0), (SL_UP * B, B), (SL_UP * B + A, B), (L, 0)],
                     fc="#B4B2A9", ec="#444441", lw=1.2))

for k in range(1, ND):                                  # equipotenciales
    xb = eq_base(k)
    xr = xb + eq_shift(k)
    c = bez((xb, 0), (xb, -0.466 * E), (xr, -0.74 * E), (xr, -E))
    ax.plot(c[:, 0], c[:, 1], color="#1D9E75", lw=0.8)

for j in range(1, NF):                                  # lineas de flujo
    fl = flow_line(j)
    ax.plot(fl[:, 0], fl[:, 1], color="#185FA5", lw=1.4)
ax.plot([XMIN, XMAX], [-E, -E], color="#185FA5", lw=1.4)    # roca = linea de flujo
ax.plot([0, L], [0, 0], color="#2C2C2A", lw=2.8)            # base = linea de flujo

ax.scatter(xs, np.zeros(N_PTS), s=230, c="#E24B4A", ec="#A32D2D", zorder=5)
for n, x in enumerate(xs, 1):
    ax.text(x, 0, str(n), color="white", ha="center", va="center", fontsize=8, zorder=6)

ax.text(XMIN + 1, D + 1.5, f"H = {H_UP:.0f} m", fontsize=11)
ax.text(XMAX - 1, C + 1.5, f"H = {H_DN:.0f} m", fontsize=11, ha="right")
ax.text(L / 2, B * 0.35, "Presa impermeable", ha="center", fontsize=11)
ax.text(L / 2, -E - 3.5, "Roca impermeable", ha="center", fontsize=10)
ax.plot([], [], color="#185FA5", label=f"Lineas de flujo (Nf = {NF})")
ax.plot([], [], color="#1D9E75", label=f"Equipotenciales (Nd = {ND})")
ax.legend(loc="upper right", fontsize=9, frameon=False)
ax.set_title(f"Red de flujo: q = k*h*Nf/Nd = {q:.3e} m3/s por m", fontsize=12)
ax.set_xlim(XMIN, XMAX)
ax.set_ylim(-E - 6, B + 4)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig("red_de_flujo.png", dpi=200, bbox_inches="tight")
fig.savefig("red_de_flujo.svg", bbox_inches="tight")

# ---------------- DIAGRAMA DE SUBPRESIONES u(x) (ampliacion opcional) ----
# Subpresion a lo largo de la base: u(x) = gamma_w * (H(x) - z), con z = E.
# Es la presion de poros que actua de abajo hacia arriba sobre la base de
# la presa. Se dibuja en un segundo panel y se calcula la resultante U_tot
# (empuje de subpresion por metro de presa) por integracion trapezoidal.
xs_fine = np.linspace(0, L, 200)
u_fine = GW * (H_UP - drop(xs_fine) - E)          # kPa
U_tot = np.trapz(u_fine, xs_fine)                 # kN por metro de presa
x_centroide = np.trapz(xs_fine * u_fine, xs_fine) / U_tot

fig2, ax2 = plt.subplots(figsize=(11, 4.0))
ax2.fill_between(xs_fine, 0, u_fine, color="#8FB7E8", alpha=0.6,
                 label="Diagrama de subpresion u(x)")
ax2.plot(xs_fine, u_fine, color="#185FA5", lw=1.8)
ax2.scatter(xs, U, s=60, c="#E24B4A", ec="#A32D2D", zorder=5,
            label="Puntos rojos")
for n, x in enumerate(xs, 1):
    ax2.annotate(f"{U[n-1]:.0f}", (x, U[n-1]), textcoords="offset points",
                 xytext=(0, 6), ha="center", fontsize=7)
ax2.axvline(x_centroide, color="#555", ls="--", lw=1,
            label=f"Resultante en x={x_centroide:.1f} m")
ax2.set_xlabel("x [m] (base de la presa, origen en pie aguas arriba)")
ax2.set_ylabel("Subpresion u [kPa]")
ax2.set_title(f"Diagrama de subpresiones bajo la base   |   "
              f"U_total = {U_tot:.0f} kN por metro de presa")
ax2.set_xlim(0, L)
ax2.set_ylim(0, max(u_fine) * 1.15)
ax2.grid(True, ls=":", alpha=0.4)
ax2.legend(loc="upper right", fontsize=9)
fig2.tight_layout()
fig2.savefig("subpresiones.png", dpi=200, bbox_inches="tight")
fig2.savefig("subpresiones.svg", bbox_inches="tight")

# ---------------- TABLA ----------------
print(f"L = {L:.1f} m | h = {h:.1f} m | dh = {dh:.4f} m | Ff = {FF:.4f} | q = {q:.3e} m3/s/m")
print(f"Subpresion total U = {U_tot:.1f} kN/m | resultante en x = {x_centroide:.1f} m")
print("Punto  x(m)   caidas  z(m)  p/gw(m)  H(m)    u(kPa)")
for n in range(N_PTS):
    print(f"{n+1:>5} {xs[n]:6.1f} {N_CAIDAS[n]:7.2f} {Z[n]:5.1f} {P[n]:8.2f} {H[n]:7.2f} {U[n]:8.1f}")
