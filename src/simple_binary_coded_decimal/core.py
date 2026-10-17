"""Core BCD encoding and decoding logic.

Design decisions
----------------
* **Input validation rejects early**: callers get a clear ``BCDOverflowError``
  instead of a confusing structural failure deep inside the encoder.
* **Packed BCD** stores two digits per byte; the count of decimal digits must
  be even so that every byte is fully populated.  An odd digit count is a
  usage error, not silently zero-padded, because silently padding changes the
  width of the output and can misalign downstream parsers.
* **Unpacked BCD** stores one digit per byte.  The high nibble of each byte
  is zeroed, matching the most common hardware convention.
* The decoders are intentionally strict: an invalid nibble (value > 9) raises
  rather than guessing, because corrupted BCD almost always indicates a
  higher-level framing bug that should not be silently masked.
"""

from __future__ import annotations


class BCDOverflowError(ValueError):
    """Raised when input cannot be represented in the requested BCD form.

    Distinct from plain ``ValueError`` so callers can catch BCD-specific
    validation failures without also catching unrelated value errors from
    other code on the same call path.
    """


class PackedBCD:
    """Encode to and decode from packed Binary Coded Decimal.

    Packed BCD stores two decimal digits per byte: the high nibble is the
    tens digit, the low nibble is the units digit.  For example, the decimal
    number ``12`` becomes the single byte ``0x12``.
    """

    @staticmethod
    def encode(value: int) -> bytes:
        """Encode a non-negative integer into packed BCD bytes.

        The number of decimal digits in ``value`` must be even so that every
        output byte carries two digits.  ``0`` is represented as a single
        zero byte (one digit pair whose value is zero).

        Raises:
            BCDOverflowError: if ``value`` is negative or not an ``int``.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise BCDOverflowError(
                f"expected int, got {type(value).__name__}"
            )
        if value < 0:
            raise BCDOverflowError("negative values are not supported")
        if value == 0:
            return b"\x00"

        digits = [int(c) for c in str(value)]
        if len(digits) % 2 != 0:
            raise BCDOverflowError(
                "packed BCD requires an even number of decimal digits; "
                "left-pad the input with a zero if you need a specific width"
            )

        out = bytearray()
        for i in range(0, len(digits), 2):
            out.append((digits[i] << 4) | digits[i + 1])
        return bytes(out)

    @staticmethod
    def decode(data: bytes) -> int:
        """Decode packed BCD bytes back into a Python ``int``.

        Every nibble of every byte must hold a value in ``0..9``.  This
        strictness is deliberate: silently treating ``0xA`` as ``0`` would
        hide data corruption that the caller almost certainly needs to know
        about.

        Raises:
            BCDOverflowError: if ``data`` is not ``bytes`` or contains a
                nibble greater than 9.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise BCDOverflowError(
                f"expected bytes, got {type(data).__name__}"
            )

        value = 0
        for byte in data:
            hi = (byte >> 4) & 0x0F
            lo = byte & 0x0F
            if hi > 9 or lo > 9:
                raise BCDOverflowError(
                    f"invalid nibble in packed BCD: byte 0x{byte:02x}"
                )
            value = value * 100 + hi * 10 + lo
        return value


class UnpackedBCD:
    """Encode to and decode from unpacked Binary Coded Decimal.

    Unpacked BCD stores one decimal digit per byte, always in the low nibble.
    The high nibble is zero.  This matches the convention used by most
    BCD-capable peripherals and software interfaces.
    """

    @staticmethod
    def encode(value: int) -> bytes:
        """Encode a non-negative integer into unpacked BCD bytes.

        One output byte is produced per decimal digit.  ``0`` encodes to a
        single ``b'\x00'`` byte.

        Raises:
            BCDOverflowError: if ``value`` is negative or not an ``int``.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise BCDOverflowError(
                f"expected int, got {type(value).__name__}"
            )
        if value < 0:
            raise BCDOverflowError("negative values are not supported")

        digits = [int(c) for c in str(value)]
        return bytes(digits)

    @staticmethod
    def decode(data: bytes) -> int:
        """Decode unpacked BCD bytes back into a Python ``int``.

        Each byte must hold a value in ``0..9``.  Values with a non-zero high
        nibble are rejected to surface framing mistakes early.

        Raises:
            BCDOverflowError: if ``data`` is not ``bytes`` or contains a
                byte outside the range ``0..9``.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise BCDOverflowError(
                f"expected bytes, got {type(data).__name__}"
            )

        value = 0
        for byte in data:
            if not 0 <= byte <= 9:
                raise BCDOverflowError(
                    f"invalid byte in unpacked BCD: 0x{byte:02x}"
                )
            value = value * 10 + byte
        return value
