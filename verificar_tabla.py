# -*- coding: utf-8 -*-
"""
Verificador en Python puro (sin numpy/matplotlib) que replica EXACTAMENTE
la aritmetica de flow_net.py y la compara contra la tabla de "Resultados
esperados" del spec SPEC-kiro. Solo valida numeros; no dibuja.
"""

# ---------- DATOS (identicos a flow_net.py) ----------
A, B = 15.0, 20.0
D, C = 19.0, 6.0
E = 21.0
SL_UP, SL_DN = 3.0, 2.0
K = 2.5e-5
GW = 9.81
NF, ND = 4, 24
N_PTS = 10

# ---------- CALCULOS (identicos a flow_net.py) ----------
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
    """Replica numpy.where de flow_net.drop para un escalar."""
    i = h / L_EFF
    if x <= 0:
        return 0.0
    if x >= L:
        return h
    if x <= L / 2:
        return i * (x + OFF)
    return h - i * (L - x + OFF)


def linspace(a, b, n):
    return [a + (b - a) * k / (n - 1) for k in range(n)]


xs = linspace(0, L, N_PTS)
Hv = [H_UP - drop(x) for x in xs]
Zv = [E] * N_PTS
Pv = [Hv[i] - Zv[i] for i in range(N_PTS)]
Uv = [GW * Pv[i] for i in range(N_PTS)]
Nc = [drop(x) / dh for x in xs]

# ---------- TABLA ESPERADA (del spec) ----------
esperado = [
    # punto, caidas, z, p/gw, H, u
    (1,  0.00, 21, 19.00, 40.00, 186.4),
    (2,  3.48, 21, 17.11, 38.11, 167.9),
    (3,  5.92, 21, 15.80, 36.80, 155.0),
    (4,  8.35, 21, 14.48, 35.48, 142.0),
    (5, 10.78, 21, 13.16, 34.16, 129.1),
    (6, 13.22, 21, 11.84, 32.84, 116.2),
    (7, 15.65, 21, 10.52, 31.52, 103.2),
    (8, 18.08, 21,  9.20, 30.20,  90.3),
    (9, 20.52, 21,  7.89, 28.89,  77.4),
    (10, 24.00, 21,  6.00, 27.00,  58.9),
]

print("Parametros globales:")
print("  L = %.1f m | h = %.1f m | dh = %.4f m | Ff = %.4f | q = %.3e m3/s/m"
      % (L, h, dh, FF, q))
print("  cell = %.3f m | L_EFF = %.1f m | OFF = %.1f m" % (cell, L_EFF, OFF))
print("  Esperado spec: dh=0.5417, Ff=0.1667, q=5.417e-05, L_EFF=126, OFF=5.5")
print()

hdr = "%4s %7s %8s %6s %9s %8s %9s" % ("Pto", "x(m)", "caidas", "z(m)",
                                       "p/gw(m)", "H(m)", "u(kPa)")
print(hdr)
print("-" * len(hdr))

tol = 0.06   # tolerancia (los esperados estan redondeados a 2 decimales)
todo_ok = True
for i in range(N_PTS):
    e = esperado[i]
    row = (i + 1, xs[i], Nc[i], Zv[i], Pv[i], Hv[i], Uv[i])
    # comparaciones
    ok = (abs(Nc[i] - e[1]) < tol and abs(Pv[i] - e[3]) < tol and
          abs(Hv[i] - e[4]) < tol and abs(Uv[i] - e[5]) < 0.6)
    todo_ok = todo_ok and ok
    marca = "OK" if ok else "DIF"
    print("%4d %7.1f %8.2f %6.1f %9.2f %8.2f %9.1f   %s"
          % (row + (marca,)))

print()
print("Resultado de la verificacion:",
      "TODOS LOS PUNTOS COINCIDEN CON EL SPEC" if todo_ok
      else "HAY DIFERENCIAS")
