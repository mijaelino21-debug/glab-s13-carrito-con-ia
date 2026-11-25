# Las cuatro preguntas de revisión aplicadas a `shop/cart_ai.py`

Archivo leído sin modificar. Un «no» se demuestra con la línea exacta del diff.

| # | Pregunta | Respuesta | Línea que lo demuestra |
|---|---|---|---|
| 1 | ¿Todo el dinero es `Decimal` de principio a fin, con redondeo hacia arriba en la mitad? | **No.** | `shop/cart_ai.py:84` → `return sum(float(l.unit_price) * l.qty for l in self.lines())` acumula en `float`; `:17-18` → `Decimal(str(round(value, 2)))` redondea un `float` con `round` (0.845 → 0.84, no 0.85). Debe ser `Decimal` + `money()` de `shop/domain.py`. |
| 2 | ¿El servidor es la única fuente del precio? ¿Ninguna línea lee `price` o `unit_price` de la petición? | **No.** | `shop/cart_ai.py:139` → `cart.add(payload["sku"], payload.get("qty", 1), payload.get("price"))` lee `price` del cuerpo HTTP; `:53` → `self._prices[sku] = Decimal(str(price)) if price is not None else product.price` lo guarda y `:73` lo usa en `Line`. |
| 3 | ¿Cada regla de cantidad y existencias se cumple con cualquier secuencia (dos `add`, quitar de más, pagar cuando otro ya compró)? | **No.** | `shop/cart_ai.py:50` → `if qty > product.stock:` ignora lo que ya está en `self._qty`; `:63-64` → `self._qty[sku] -= qty` solo borra si da exactamente 0 (deja -3); `:128-129` → `checkout` descuenta sin volver a comprobar el stock. |
| 4 | ¿Repetir una acción da el mismo resultado que hacerla una vez, por ejemplo el cupón? | **No.** | `shop/cart_ai.py:81` → `self._coupons.append(code)` acumula en una lista; `:89-94` → `for code in self._coupons: total_discount += ...` vuelve a aplicar cada cupón. Aplicar `BIENVENIDA10` dos veces da 37.80 en vez de 18.90. |

Conclusión: las cuatro respuestas son «no» y cada una se corrige en un solo método, sin tocar pruebas ni reglas.
