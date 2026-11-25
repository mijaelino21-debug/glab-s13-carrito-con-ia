# Hallazgos de la auditoría de los 6 carritos

Comandos (con `$env:SHOP_MODE="ai"`): `python manage.py audit_cart carts/*.json` y
`python manage.py audit_cart carts/*.json --replay`. Salidas: `14_audit_ai.txt` y `14_audit_ai_replay.txt`.
La auditoría se ejecuta **después** de arreglar el carrito de la IA.

| Carrito | Hallazgo con `--replay` | Fallo de los 5 al que corresponde |
|---|---|---|
| `01-correcto.json` | `OK`: único carrito sin hallazgos, declarado = fórmula = replay. | Ninguno (carrito de control). |
| `02-precio-del-cliente.json` | `PRICE_MISMATCH` (LAP-01 cobra 0.01 vs 2499.90) + `TOTAL_MISMATCH` en subtotal, IGV y total. | Fallo **2**, precio tomado del cliente (seguridad, solo API). |
| `03-stock.json` | `OVER_STOCK` (4 unidades de PAD-01, solo hay 2) + `REPLAY_REJECTED` (la implementación ya rechaza esa cantidad). | Fallo **3**, existencias que no cuentan lo ya agregado / no se reverifican. |
| `04-cantidad-negativa.json` | `BAD_QTY` (MOU-01 con -3) + `TOTAL_MISMATCH` en subtotal/IGV/total + `REPLAY_REJECTED`. | Fallo **4**, cantidad negativa al quitar. |
| `05-cupon-doble.json` | `MULTIPLE_COUPONS` (dos `BIENVENIDA10`) + `TOTAL_MISMATCH` (descuento 37.80 vs 18.90, IGV y total). | Fallo **5**, descuento acumulado dos veces. |
| `06-redondeo.json` | `TOTAL_MISMATCH` solo en `discount` (declara 0.84, la fórmula da 0.85). | Fallo **1**, redondeo con `float`. |

## `TOTAL_MISMATCH` frente a `REPLAY_MISMATCH`

- **`TOTAL_MISMATCH`** compara lo que el carrito **declaró** en el JSON (`declared`) con la fórmula
  independiente `reference_totals` del catálogo. Es una comprobación de los datos entregados; no necesita
  ejecutar la implementación y por eso aparece igual con o sin `--replay`.
- **`REPLAY_MISMATCH`** compara lo que **calcula la implementación activa** al reconstruir el carrito con
  `reference_totals`. Depende de `SHOP_MODE` y del código: antes de arreglar, `13_antes_replay.txt` mostraba
  `REPLAY_MISMATCH` en 05 (descuento 37.8 vs 18.90) y en 06 (0.84 vs 0.85); después de los cinco arreglos ya
  **no hay ningún `REPLAY_MISMATCH`**, porque el carrito de la IA calcula igual que la fórmula.
- En 03 y 04 la implementación ni siquiera llega a calcular: lanza `OutOfStock` / `InvalidQuantity` y se
  registra `REPLAY_REJECTED`, que es exactamente el comportamiento que la compuerta espera para esos dos carritos.
- En resumen: `TOTAL_MISMATCH` delata el contenido del carrito declarado (lo que el cliente/IA entregó);
  `REPLAY_MISMATCH` delata al código que lo procesa. Un mismo carrito puede tener ambos a la vez (05 y 06 antes
  de arreglar) o solo `TOTAL_MISMATCH` (después de arreglar).
