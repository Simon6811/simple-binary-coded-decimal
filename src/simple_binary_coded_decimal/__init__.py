"""Public API for simple-binary-coded-decimal.

This package provides encoding and decoding between Python integers and
the two common Binary Coded Decimal representations:

- **Packed BCD**: two decimal digits per byte (one nibble each).
- **Unpacked BCD**: one decimal digit per byte, stored in the low nibble.

Only non-negative integers are supported.  BCD is a fixed-width digit
representation, so negative values and fractions are out of scope.
"""

from .core import (
    PackedBCD,
    UnpackedBCD,
    BCDOverflowError,
)

__all__ = [
    "PackedBCD",
    "UnpackedBCD",
    "BCDOverflowError",
]
