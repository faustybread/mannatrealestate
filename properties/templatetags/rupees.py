"""
Template filters for rendering Indian Rupee (INR) prices.

Two flavours are exposed:

* ``{{ value|inr }}``       — headline shorthand used in cards and hero
                              blocks. Renders as ``₹4.5 Cr``, ``₹85 L`` or
                              ``₹42,500`` depending on magnitude, keeping the
                              luxury Tailwind cards tight and legible.

* ``{{ value|inr_full }}``  — exact, Indian-style grouped rupee amount for
                              detail views (e.g. ``₹4,50,00,000``). Useful
                              when the buyer wants the full number.

Both filters accept ``int``, ``float``, ``Decimal`` and numeric strings.
Anything that can't be coerced returns an empty string so the UI stays
graceful rather than raising a ``VariableDoesNotExist``.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

# Rupee sign; kept as a module constant so tests / other filters can import it.
RUPEE = "₹"

_CRORE = Decimal("10000000")   # 1,00,00,000
_LAKH = Decimal("100000")      # 1,00,000


def _to_decimal(value) -> Decimal | None:
    """Coerce ``value`` to Decimal, or return None if not possible."""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _trim(d: Decimal) -> str:
    """Format a Decimal with up to 2 dp, dropping trailing zeros."""
    # Quantize keeps at most 2 decimals; normalize strips trailing zeros
    # but can produce scientific notation for whole numbers, so we handle
    # the integer case explicitly.
    q = d.quantize(Decimal("0.01"))
    if q == q.to_integral_value():
        return f"{int(q)}"
    # Trim trailing zeros without dropping the decimal separator.
    text = format(q, "f").rstrip("0").rstrip(".")
    return text or "0"


def _indian_group(n: int) -> str:
    """Group a non-negative integer in Indian style: 1,23,45,678."""
    s = str(n)
    if len(s) <= 3:
        return s
    last3, rest = s[-3:], s[:-3]
    # Break `rest` into 2-digit chunks from the right.
    chunks = []
    while len(rest) > 2:
        chunks.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        chunks.append(rest)
    return ",".join(reversed(chunks)) + "," + last3


@register.filter(name="inr")
def inr(value) -> str:
    """Compact INR — ``₹4.5 Cr``, ``₹85 L`` or grouped for smaller values."""
    d = _to_decimal(value)
    if d is None:
        return ""

    neg = d < 0
    d = -d if neg else d
    sign = "-" if neg else ""

    if d >= _CRORE:
        return f"{sign}{RUPEE}{_trim(d / _CRORE)} Cr"
    if d >= _LAKH:
        return f"{sign}{RUPEE}{_trim(d / _LAKH)} L"
    # Sub-lakh: show the exact grouped number, no decimals.
    return f"{sign}{RUPEE}{_indian_group(int(d))}"


@register.filter(name="inr_full")
def inr_full(value) -> str:
    """Exact Indian-grouped rupee amount, e.g. ``₹4,50,00,000``."""
    d = _to_decimal(value)
    if d is None:
        return ""
    neg = d < 0
    whole = int(-d if neg else d)
    return f"{'-' if neg else ''}{RUPEE}{_indian_group(whole)}"
