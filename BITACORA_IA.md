# Bitácora de uso de IA

Cada turno registra el pedido recibido, el método tocado, las pruebas corridas y el veredicto de la compuerta
antes y después. Idioma del código y de los mensajes de commit: inglés.

## Turno 0 — preparación del repositorio

- **Pedido:** clonar el repo base en la subcarpeta `glab-s13-carrito-con-ia`, quitar el `origin` del profesor,
  crear el repo vacío `mijaelino21-debug/glab-s13-carrito-con-ia` y apuntar `origin` a él; instalar dependencias,
  migrar y sembrar el catálogo; leer `AGENTS.md`.
- **Método tocado:** ninguno.
- **Pruebas:** ninguna todavía.
- **Gate antes / después:** no ejecutado / no ejecutado.
- **Diff:** `.gitignore` reducido a `.venv/` y `db.sqlite3`. `gh` no está instalado en esta máquina, así que el repo
  se creó con la API de GitHub (token ya guardado en el credential manager de Git) y el `origin` se agregó con `git remote add`.
  No se hizo push.

## Turno 1 — prueba inicial

- **Pedido:** correr `python manage.py test` y guardar la salida, y con `-v 2` listar qué pruebas pasan.
- **Método tocado:** ninguno.
- **Pruebas:** `python manage.py test` → `Ran 67 tests`, `FAILED (failures=2, errors=67)`, código 1.
  `python manage.py test -v 2` → las 7 que pasan son todas de `shop.tests.test_audit`:
  `test_a_consistent_cart_has_no_findings`, `test_coupon_applied_twice`, `test_float_rounding`,
  `test_more_units_than_the_stock`, `test_negative_quantity`, `test_price_taken_from_the_client`,
  `test_the_command_reports_in_json`.
- **Gate antes / después:** no ejecutado / no ejecutado (la compuerta se usa a partir del primer cambio).
- **Diff descartado:** ninguno.

## Turno 2 — `add`

- **Pedido:** validar la cantidad (entero real, no `bool`, `>= 1`), producto conocido y existencias que cubran
  lo ya agregado más lo nuevo, sin tocar el carrito si falla.
- **Método tocado:** `Cart.add`.
- **Pruebas:** `python manage.py test shop.tests.test_lines` → 13 errores antes, 0 errores de `add` después;
  los que quedan vienen de `lines`, `remove`, `total`, `apply_coupon` (métodos aún pendientes).
- **Gate antes / después:** `rechazar` (1, 43 fallidas) / `rechazar` (1, 43 fallidas).
- **Diff descartado:** ninguno.

## Turno 3 — `remove`

- **Pedido:** `qty=None` borra la línea; si se indica, resta y borra al llegar a cero, sin negativos.
- **Método tocado:** `Cart.remove`.
- **Pruebas:** `python manage.py test shop.tests.test_lines` → 9 errores (ya ninguno de `remove`).
- **Gate antes / después:** `rechazar` (1) / `rechazar` (1).
- **Diff descartado:** ninguno.

## Turno 4 — `lines`

- **Pedido:** una `Line` por SKU en orden de inserción con el precio del catálogo.
- **Método tocado:** `Cart.lines`.
- **Pruebas:** `python manage.py test shop.tests.test_lines` → 3 errores, todos de `total`, `apply_coupon` y
  `summary` (pasos 6 y 7), ninguno de líneas/cantidades.
- **Gate antes / después:** `rechazar` (1, 43 fallidas) / `rechazar` (1, 43 fallidas, 24 pasan).
- **Comentario:** `test_lines` no puede quedar verde todavía porque `test_state_survives_between_requests`
  usa cupón y `summary`;   se volverá a correr al terminar esos pasos.
- **Diff descartado:** ninguno.

## Turno 5 — `checkout`

- **Pedido:** volver a comprobar todas las líneas antes de descontar cualquiera, bajar existencias, vaciar
  carrito y cupón y devolver el resumen.
- **Método tocado:** `Cart.checkout`.
- **Pruebas:** `python manage.py test shop.tests.test_stock` → 7 de 10 pasan; los 3 errores restantes son
  `summary` y `apply_coupon` (pasos 6 y 7), no stock ni checkout.
- **Gate antes / después:** `rechazar` (1) / `rechazar` (1).
- **Diff descartado:** ninguno.

## Turno 6 — decimales en el intérprete

- **Pedido:** ejecutar las cuatro expresiones de decimales y guardar los resultados.
- **Método tocado:** ninguno.
- **Pruebas:** no aplica; salida en `evidencias/05_decimal.txt`. `0.1+0.2` da `0.30000000000000004`,
  `Decimal` da `0.3`, `round(0.845, 2)` da `0.84` y `quantize(..., ROUND_HALF_UP)` da `0.85`.
- **Gate antes / después:** no ejecutado / no ejecutado.
- **Diff descartado:** ninguno.

## Turnos 7-11 — `subtotal`, `discount`, `igv`, `total`, `summary`

- **Pedido:** calcular todos los importes con `Decimal` y `money()`, y devolver el resumen con cadenas de dos decimales.
- **Métodos tocados:** `Cart.subtotal`, `Cart.discount`, `Cart.igv`, `Cart.total`, `Cart.summary` (uno por turno).
- **Pruebas:** `python manage.py test shop.tests.test_totals` → 9 errores tras `subtotal`, 4 tras los demás;
  los 4 restantes eran de `apply_coupon`, que aún no existía. Tras implementarlo: 10/10 OK.
- **Gate antes / después:** `rechazar` (1) / se volverá a medir al terminar el carrito completo.
- **Diff descartado:** ninguno.

## Turno 12 — `apply_coupon`

- **Pedido:** un solo cupón que se reemplaza, `strip` + `upper`, desconocido → `InvalidCoupon`, fijo sin pasar del subtotal.
- **Método tocado:** `Cart.apply_coupon` (y `Cart.discount` para el tope del cupón fijo).
- **Pruebas:** `shop.tests.test_coupons` → 9/9 OK; regresión `test_lines + test_stock + test_totals` → 35/35 OK.
- **Gate antes / después:** `rechazar` (1) / se medirá en el paso 9.
- **Nota de commit:** los pasos 6 y 7 se commitean juntos porque `test_totals` no puede quedar verde sin
  `apply_coupon`; separarlos dejaría un commit con pruebas en rojo.
- **Diff descartado:** ninguno.

## Turno 13 — `add_from_payload`

- **Pedido:** aceptar solo un dict con `sku` string; no leer `price` de la petición.
- **Método tocado:** `add_from_payload`.
- **Pruebas:** `shop.tests.test_api` → 14/14 OK. Regresión: `shop.tests.test_lines` → 15/15 OK.
- **Gate antes / después:** `rechazar` (1) / se medirá en el paso 9.
- **Pregunta de revisión aplicada:** #2 (el servidor es la única fuente del precio): la función solo pasa
  `sku` y `qty`; el precio lo toma `Cart.lines` del catálogo.
- **Diff descartado:** ninguno.

