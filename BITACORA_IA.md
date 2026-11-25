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
  usa cupón y `summary`; se volverá a correr al terminar esos pasos.
- **Diff descartado:** ninguno.
