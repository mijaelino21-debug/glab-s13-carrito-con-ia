# Salida para un agente: `--json` y `--strict`

Evidencias: `15_audit_json.txt` (`python manage.py audit_cart carts/*.json --json`, `$LASTEXITCODE=0`) y
`15_audit_strict.txt` (`... --strict`, `$LASTEXITCODE=1`). Modo `ai`.

## ¿Qué haría un agente con esa salida?

1. Parsear el JSON: `{"mode": "ai", "carts": [{"file", "ok", "findings": [{"code", "detail"}]}]}`.
   No tendría que leer prosa en español: filtra `carts[].ok == false` y agrupa por `findings[].code`.
2. Clasificar: `PRICE_MISMATCH` → fallo 2 (seguridad); `OVER_STOCK` / `REPLAY_REJECTED` → fallo 3;
   `BAD_QTY` → fallo 4; `MULTIPLE_COUPONS` → fallo 5; `TOTAL_MISMATCH` de un céntimo → fallo 1.
3. Decidir con `--strict`: como `$LASTEXITCODE=1`, un script de CI/CI-agent puede detener el despliegue sin
   interpretar el texto. `--json` devuelve 0 porque solo informa; `--strict` convierte los hallazgos en fallo.
4. Proponer **un** cambio por turno en `shop/cart_ai.py`, volver a correr las pruebas y la compuerta, y dejar
   que la persona responda las cuatro preguntas de `AGENTS.md`. El agente propone; las pruebas y la compuerta deciden.

## ¿Por qué la auditoría no sustituye las reglas del servidor?

- La auditoría es **observacional**: lee un carrito ya producido y compara sus números con
  `reference_totals`. Detecta el síntoma (un precio distinto, una cantidad negativa), pero no impide que
  se produzca: no valida la petición HTTP que viene por delante.
- El servidor sí es la frontera: `shop/views.py` traduce errores `CartError` a 400/404/409 y
  `shop/cart_team.py` valida `sku`, `qty`, existencias, cupón y usa `money()` antes de escribir. Sin esas
  reglas, un atacante podría enviar `price: 0.01` y la auditoría solo lo descubriría **después** del pago.
- `--replay` depende de la implementación activa (`SHOP_MODE`): con el carrito de la IA sin arreglar daba
  `REPLAY_MISMATCH`; con el carrito arreglado ya no da, aunque los carritos declarados sigan mal. Es una
  comprobación del código, no una autorización de la transacción.
- Por eso `gate` une ambos oráculos (pruebas + replay) y aun así `AGENTS.md` exige las cuatro preguntas de
  revisión: la compuerta comprueba lo que las pruebas saben preguntar, no todo lo que nadie escribió.
