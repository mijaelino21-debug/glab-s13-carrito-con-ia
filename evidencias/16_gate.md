# Veredictos de la compuerta

Evidencias: `16_gate_ai.txt`, `16_gate_team.txt`, `16_gate_json.txt`.

| Comando | Veredicto | `$LASTEXITCODE` | Detalle |
|---|---|---|---|
| `python manage.py gate --modo ai` | **aceptar** | 0 | 67 pasan / 0 fallan, 6 de 6 carritos como se esperaba |
| `python manage.py gate` (team) | **aceptar** | 0 | 67 pasan / 0 fallan, 6 de 6 carritos como se esperaba |
| `python manage.py gate --json` (team) | `"verdict": "aceptar"` | 0 | `"failed": 0`, `failing: []`, los 6 `carts[].result == "ok"` |

## ¿Por qué los carritos 03 y 04 deben rechazarse?

- `03-stock.json` declara 4 unidades de PAD-01 y solo hay 2 → `OVER_STOCK`.
- `04-cantidad-negativa.json` declara MOU-01 con `qty: -3` → `BAD_QTY`.
- `shop/gate.py:14` define `MUST_REJECT = {"BAD_QTY", "UNKNOWN_SKU", "OVER_STOCK"}` y `expected_outcome`
  (`:25-27`) marca esos carritos como `rechazar`. `judge_cart` (`:38-39`) solo los da por buenos si aparece
  `REPLAY_REJECTED`, es decir, si la implementación activa lanza `OutOfStock` / `InvalidQuantity`.
- Si una implementaciónaceptara esos carritos y calculara totales, el resultado sería
  `acepta_lo_que_debia_rechazar` y la compuerta daría `rechazar` (1) aunque las pruebas estuvieran en verde.

## ¿Por qué el replay no detecta el precio del cliente?

- El precio falso (`unit_price: "0.01"`) vive en el **carrito declarado**, no en la acción que reconstruye
  el replay. Al reproducir `02-precio-del-cliente.json`, la implementación activa recibe `sku` y `qty` y toma
  el precio del catálogo (2499.90), así que no hay `REPLAY_MISMATCH`.
- `shop/gate.py:32-34` calcula el resultado esperado solo con los códigos declarados; `PRICE_MISMATCH` **no**
  está en `MUST_REJECT`, por lo que el carrito 02 se espera como `totales`. `judge_cart` (`:42-44`) decide
  el resultado mirando únicamente `REPLAY_*`. Con el carrito arreglado, el replay da los totales correctos y
  el carrito 02 resulta `ok`.
- Entonces, ¿qué lo detecta? Dos piezas, ninguna es el replay:
  1. **La auditoría**, `shop/audit.py`, al comparar el precio declarado con el catálogo, emite
     `PRICE_MISMATCH` (`14_audit_ai.txt`: "el carrito cobra 0.01 y el catálogo dice 2499.90"). Es una señal
     sobre los datos entregados, visible en `audit_cart --json`.
  2. **Las pruebas**, dentro del propio `gate`: `ApiTests.test_the_price_comes_from_the_catalog_not_from_the_client`
     y `test_a_negative_price_from_the_client_changes_nothing_either` fallaban con la IA original
     (`unit_price '0.01' != '2499.90'`). Son las que hacen que `tests.failed` pase de 18 a 0.
- Es decir: el replay comprueba que el **código** calcule bien; la auditoría comprueba lo que el **carrito
  declaró**, y las pruebas comprueban que el código no lea el precio de la petición. Por eso `gate` junta
  los dos oráculos en vez de fiarse solo del replay, y por eso la compuerta en verde no reemplaza la
  pregunta de revisión #2.
