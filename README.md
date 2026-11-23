# Red de flujo bajo una presa de tierra impermeable (Ejercicio 10)

Cálculo de la red de flujo y de las cargas (total, de presión y de posición)
en 10 puntos sobre la base de una presa de tierra con núcleo impermeable,
con el diagrama de subpresiones bajo la base.

Referencia teórica: Juárez Badillo y Rico, *Mecánica de Suelos* tomo 2, cap. II.

## Datos del problema (de la imagen del enunciado)

| Símbolo | Valor | Significado |
|---|---|---|
| A | 15 m | ancho de la corona |
| B | 20 m | altura de la presa |
| C | 6 m | nivel de agua aguas abajo |
| D | 19 m | nivel de agua aguas arriba |
| E | 21 m | espesor del suelo permeable hasta la roca |
| talud aguas arriba | 3H:1V | |
| talud aguas abajo | 2H:1V | |
| k | 2.5×10⁻⁵ m/s | permeabilidad |
| γw | 9.81 kN/m³ | peso específico del agua |
| Nf, Nd | 4, 24 | canales de flujo y caídas de potencial |

## Datum y convención de signos

- **Datum (z = 0): la roca impermeable** (base del estrato permeable).
  Por lo tanto los puntos de la base tienen z = E = 21 m.
- Cargas de borde: H_arriba = E + D = 40 m; H_abajo = E + C = 27 m;
  pérdida total h = 13 m.
- Carga total: H = z + p/γw (se desprecia v²/2g en medio poroso).
- Se cumple en cada punto: **H = z + p/γw**.

## Resultados

- Base de la presa: L = 3B + A + 2B = **115 m**
- Caída por equipotencial: Δh = h/Nd = **0.5417 m**
- Factor de forma: Ff = Nf/Nd = **0.1667**
- Caudal de filtración: q = k·h·Ff = **5.417×10⁻⁵ m³/s por metro de presa**
- Subpresión total bajo la base: U ≈ **14 102 kN por metro de presa**,
  aplicada en x ≈ **48.4 m** desde el pie aguas arriba.

| Punto | x [m] | caídas | z [m] | p/γw [m] | H [m] | u [kPa] |
|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.00 | 21 | 19.00 | 40.00 | 186.4 |
| 2 | 12.8 | 3.48 | 21 | 17.11 | 38.11 | 167.9 |
| 3 | 25.6 | 5.92 | 21 | 15.80 | 36.80 | 155.0 |
| 4 | 38.3 | 8.35 | 21 | 14.48 | 35.48 | 142.0 |
| 5 | 51.1 | 10.78 | 21 | 13.16 | 34.16 | 129.1 |
| 6 | 63.9 | 13.22 | 21 | 11.84 | 32.84 | 116.2 |
| 7 | 76.7 | 15.65 | 21 | 10.52 | 31.52 | 103.2 |
| 8 | 89.4 | 18.08 | 21 | 9.20 | 30.20 | 90.3 |
| 9 | 102.2 | 20.52 | 21 | 7.89 | 28.89 | 77.4 |
| 10 | 115.0 | 24.00 | 21 | 6.00 | 27.00 | 58.9 |

## Archivos

| Archivo | Descripción |
|---|---|
| `flow_net.py` | Script principal (numpy + matplotlib). Genera `red_de_flujo.png/svg`, `subpresiones.png/svg` y la tabla en consola. |
| `verificar_tabla.py` | Verificador en Python puro (sin dependencias) que replica la aritmética y la compara con la tabla esperada. |
| `flow_net_svg.py` | Dibuja la red de flujo en SVG puro (sin numpy/matplotlib). |
| `subpresiones_svg.py` | Dibuja el diagrama de subpresiones u(x) en SVG puro. |
| `red_de_flujo.svg` | Figura de la red de flujo. |
| `subpresiones.svg` | Diagrama de subpresiones bajo la base. |

## Uso

```bash
# Versión completa (requiere numpy y matplotlib)
pip install -r requirements.txt
python flow_net.py

# Versión sin dependencias (genera los SVG directamente)
python flow_net_svg.py
python subpresiones_svg.py

# Verificar la tabla (sin dependencias)
python verificar_tabla.py
```
