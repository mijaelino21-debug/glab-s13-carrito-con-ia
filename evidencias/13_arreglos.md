# Arreglos del carrito de la IA (un fallo por commit)

Modo de trabajo: `$env:SHOP_MODE="ai"` en PowerShell; después de cada arreglo se corre
`python manage.py test` con ese modo y se anota `fallaban X -> Y`.

## Antes de arreglar (línea base)

- `python manage.py test` con `SHOP_MODE=ai`: `Ran 67 tests`, `FAILED (failures=17, errors=1)` → **18 fallidas**, 49 pasan.
- `python manage.py audit_cart carts/*.json --replay` con `SHOP_MODE=ai`: `REPLAY_MISMATCH` en los carritos
  05 y 06 (cupón doble y redondeo); `REPLAY_REJECTED` en 03 y 04; `PRICE_MISMATCH` en 02.
- `python manage.py gate --modo ai`: **RECHAZAR**, código de salida **1**, 49 pasan / 18 fallan,
  4 de 6 carritos como se esperaba.
- Evidencias: `13_antes_test.txt`, `13_antes_replay.txt`, `13_antes_gate.txt`.
