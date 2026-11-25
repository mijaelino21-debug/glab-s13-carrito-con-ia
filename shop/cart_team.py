"""Your cart. Complete every TODO until `python manage.py test` is green.

The rules (money, stock, coupons, checkout) are in README.md and in shop/domain.py. Do not change
shop/domain.py or the tests. Money is Decimal (never float) and the price always comes from the
catalog, never from the request.
"""
from decimal import Decimal  # noqa: F401

from shop.domain import (  # noqa: F401  (you will need most of these)
    COUPONS,
    IGV_RATE,
    CartError,
    InvalidCoupon,
    InvalidQuantity,
    Line,
    OutOfStock,
    UnknownProduct,
    fmt,
    money,
)


class Cart:
    def __init__(self, catalog):
        self._catalog = catalog  # sku -> Product (price Decimal, stock int)
        self._qty = {}  # sku -> quantity, in insertion order
        self._coupon = None  # one coupon per cart

    # --- persistence between requests (already done) ---
    def to_state(self):
        return {"qty": dict(self._qty), "coupon": self._coupon}

    @classmethod
    def from_state(cls, catalog, state):
        cart = cls(catalog)
        cart._qty = {sku: int(q) for sku, q in state.get("qty", {}).items() if sku in catalog}
        cart._coupon = state.get("coupon")
        return cart

    # --- lines ---
    def add(self, sku, qty=1):
        """Add qty units of a catalog product, checking quantity and stock first."""
        if type(qty) is not int or qty < 1:
            raise InvalidQuantity("qty must be an integer >= 1")
        if sku not in self._catalog:
            raise UnknownProduct(f"unknown product: {sku!r}")
        if self._qty.get(sku, 0) + qty > self._catalog[sku].stock:
            raise OutOfStock(f"not enough stock for {sku!r}")
        self._qty[sku] = self._qty.get(sku, 0) + qty

    def remove(self, sku, qty=None):
        """Remove units from a line, dropping it at zero and never going negative."""
        if sku not in self._qty:
            raise UnknownProduct(f"unknown product in cart: {sku!r}")
        if qty is not None and (type(qty) is not int or qty < 1):
            raise InvalidQuantity("qty must be an integer >= 1")
        if qty is None or qty >= self._qty[sku]:
            del self._qty[sku]
        else:
            self._qty[sku] -= qty

    def qty_of(self, sku):
        return self._qty.get(sku, 0)

    def lines(self):
        """Build Line objects in insertion order with the price taken from the catalog."""
        return [
            Line(sku, self._catalog[sku].name, self._catalog[sku].price, qty)
            for sku, qty in self._qty.items()
        ]

    # --- coupon and totals ---
    def apply_coupon(self, code):
        """Normalize and validate the code, then replace the cart's single coupon."""
        if not isinstance(code, str):
            raise InvalidCoupon("coupon code must be a string")
        normalized = code.strip().upper()
        if normalized not in COUPONS:
            raise InvalidCoupon(f"unknown coupon: {code!r}")
        self._coupon = normalized

    def subtotal(self):
        """Sum line totals with Decimal arithmetic and round to cents."""
        return money(sum((line.total for line in self.lines()), Decimal("0")))

    def discount(self):
        """Compute the single coupon's discount, capped at the subtotal for fixed coupons."""
        if self._coupon is None:
            return Decimal("0.00")
        kind, amount = COUPONS[self._coupon]
        if kind == "percent":
            return money(self.subtotal() * amount / 100)
        return money(min(amount, self.subtotal()))

    def igv(self):
        """Charge 18 % sales tax on the discounted base, rounded half up."""
        return money((self.subtotal() - self.discount()) * IGV_RATE)

    def total(self):
        """Add the already rounded tax to the discounted base."""
        return money(self.subtotal() - self.discount()) + self.igv()

    def summary(self):
        """Return the API payload with money values formatted as two-decimal strings."""
        return {
            "lines": [
                {
                    "sku": line.sku,
                    "name": line.name,
                    "unit_price": fmt(line.unit_price),
                    "qty": line.qty,
                    "line_total": fmt(line.total),
                }
                for line in self.lines()
            ],
            "coupon": self._coupon,
            "subtotal": fmt(self.subtotal()),
            "discount": fmt(self.discount()),
            "igv": fmt(self.igv()),
            "total": fmt(self.total()),
        }

    # --- checkout ---
    def checkout(self):
        """Recheck every line first, then commit the sale without changing anything on failure."""
        if not self._qty:
            raise CartError("cannot check out an empty cart")
        for sku, qty in self._qty.items():
            if qty > self._catalog[sku].stock:
                raise OutOfStock(f"not enough stock for {sku!r}")
        order = self.summary()
        for sku, qty in self._qty.items():
            self._catalog[sku].stock -= qty
        self._qty.clear()
        self._coupon = None
        return order


def add_from_payload(cart, payload):
    """TODO: translate the JSON body of POST /api/cart/items/ ({"sku": ..., "qty": ...}) into a cart.add
    call. The body is untrusted: if it is not a dict with a string «sku», raise CartError. The price is
    NOT part of the contract: the catalog is the only source of prices."""
    raise NotImplementedError("TODO: add_from_payload")
