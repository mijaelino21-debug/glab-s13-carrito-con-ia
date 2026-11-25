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

## Arreglo 1 — redondeo con float

- **Pedido:** todo el dinero en `Decimal` con `money()` y redondeo half up.
- **Métodos tocados (uno por turno):** `IGV` / import, `_money`, `_subtotal`, `_discount`, `igv`, `total`.
- **Cambio:** `_subtotal` suma `unit_price * qty` con `Decimal("0")`; `_discount` acumula `Decimal`;
  `IGV = Decimal("0.18")`; `_money` delega en `money`; `igv` y `total` usan los importes ya redondeados
  (`self.subtotal()` y `self.discount()`) para no redondear dos veces la misma base.
- **Pruebas con `SHOP_MODE=ai`:** fallaban **18** → **13** (`Ran 67`, `failures=12, errors=1`).
  Desaparecieron `test_the_discount_rounds_half_up`, `test_igv_rounds_half_up`,
  `test_a_discount_of_one_and_a_half_cents`, `test_total_is_the_sum_of_its_rounded_parts` y
  `test_replay_of_the_rounding_cart_matches_your_cart`.
- **Gate:** sigue en `rechazar` (1); se volverá a medir al terminar los cinco arreglos.
- **Evidencia:** `13_fix1_test.txt`.

## Arreglo 2 — precio tomado del cliente (seguridad)

- **Pedido:** el catálogo es la única fuente del precio; ninguna línea lee `price` del cuerpo HTTP.
- **Métodos tocados (uno por turno):** `Cart.add`, `add_from_payload`.
- **Cambio:** `add` ya no acepta el parámetro `price` y guarda `product.price`; `add_from_payload` pasa solo
  `sku` y `qty`. Review question #2 queda respondida con `shop/cart_ai.py:139` y `:53` ya limpias.
- **Pruebas con `SHOP_MODE=ai`:** fallaban **13** → **11**. Se arreglan
  `test_the_price_comes_from_the_catalog_not_from_the_client` y
  `test_a_negative_price_from_the_client_changes_nothing_either`.
- **Gate:** sigue en `rechazar` (1).
- **Evidencia:** `13_fix2_test.txt`.

## Arreglo 3 — existencias que no cuentan lo ya agregado

- **Pedido:** dos `add` seguidos no pueden rebasar el stock y `checkout` debe volver a comprobar todo antes de descontar.
- **Métodos tocados (uno por turno):** `Cart.add`, `Cart.checkout`.
- **Cambio:** `add` compara `self._qty.get(sku, 0) + qty` contra `product.stock`; `checkout` recorre todas las
  líneas y lanza `OutOfStock` antes de tocar cualquier existencia.
- **Pruebas con `SHOP_MODE=ai`:** fallaban **11** → **5**. Se arreglan las cuatro de stock y
  `test_more_than_the_stock_is_409` y el error `test_checkout_when_the_stock_changed_is_409_and_keeps_the_cart`.
- **Gate:** sigue en `rechazar` (1).
- **Evidencia:** `13_fix3_test.txt`.

## Arreglo 4 — cantidad negativa al quitar

- **Pedido:** quitar más de lo que hay debe borrar la línea y nunca dejar `-3`.
- **Método tocado:** `Cart.remove`.
- **Cambio:** si `qty >= self._qty[sku]` se borran la línea y su precio; si no, se resta. Ya no se compara
  solo con `== 0`.
- **Pruebas con `SHOP_MODE=ai`:** fallaban **5** → **3**. Se arreglan
  `test_remove_more_than_there_is_never_leaves_a_negative_quantity` y
  `test_remove_more_than_there_is_leaves_no_negative_line`.
- **Gate:** sigue en `rechazar` (1).
- **Evidencia:** `13_fix4_test.txt`.
