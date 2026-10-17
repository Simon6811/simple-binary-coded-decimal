# simple-binary-coded-decimal

Encodes and decodes non-negative integers to and from packed and unpacked Binary Coded Decimal byte representations.

## Usage

```python
from simple_binary_coded_decimal import PackedBCD, UnpackedBCD

# Packed BCD: two decimal digits per byte.
PackedBCD.encode(1234)   # -> b'\x12\x34'
PackedBCD.decode(b'\x12\x34')  # -> 1234

# Unpacked BCD: one decimal digit per byte, low nibble only.
UnpackedBCD.encode(123)   # -> b'\x01\x02\x03'
UnpackedBCD.decode(b'\x01\x02\x03')  # -> 123
```

## Why this exists

Interfacing with hardware peripherals, legacy protocols, and embedded systems often requires BCD-formatted integers. Rather than hand-crafting nibble logic per project, this library provides two small, self-contained encoders and decoders with strict validation and no dependencies.

The trade-off is simplicity over generality: only non-negative integers are supported, and there is no support for sign nibbles or fractional digits. This keeps the surface area small and the behaviour predictable.

## Edge cases you will hit

- **Packed BCD requires an even number of decimal digits.** `PackedBCD.encode(1)` raises `BCDOverflowError` because a single digit cannot fill a byte. Left-pad your input (e.g. encode `10` or `01` as a string-derived integer) if you need a specific width.
- **Negative values are not supported.** Both encoders raise `BCDOverflowError` for negative input.
- **Decoding is strict.** A nibble or byte with a value greater than 9 raises `BCDOverflowError` rather than silently masking corrupt data.
- **`bool` is rejected as input.** Although `bool` is a subclass of `int` in Python, accepting it would introduce ambiguity (`True` encoding to `0x01`), so it is explicitly rejected.
- **Trailing zeros are significant.** `PackedBCD.encode(1200)` produces `b'\x12\x00'`, not `b'\x12'`, because BCD encodes digits, not numeric magnitude alone.
