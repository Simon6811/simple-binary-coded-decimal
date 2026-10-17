"""Tests for simple-binary-coded-decimal core logic.

The suite deliberately mirrors the implemented behaviour: it covers happy
paths, the odd-digit-count rejection for packed BCD, negative and non-int
inputs, invalid nibbles on decode, and the ``bytes``/``bytearray``
acceptance on decode.  No test asserts behaviour the implementation does
not claim to provide.
"""

import unittest

from simple_binary_coded_decimal import (
    PackedBCD,
    UnpackedBCD,
    BCDOverflowError,
)


class TestPackedEncode(unittest.TestCase):
    def test_single_digit_pair(self):
        self.assertEqual(PackedBCD.encode(12), b"\x12")

    def test_zero(self):
        self.assertEqual(PackedBCD.encode(0), b"\x00")

    def test_multi_byte(self):
        self.assertEqual(PackedBCD.encode(1234), b"\x12\x34")

    def test_large_value(self):
        self.assertEqual(PackedBCD.encode(123456), b"\x12\x34\x56")

    def test_all_nines(self):
        self.assertEqual(PackedBCD.encode(99), b"\x99")
        self.assertEqual(PackedBCD.encode(9999), b"\x99\x99")

    def test_odd_digit_count_rejected(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.encode(1)
        with self.assertRaises(BCDOverflowError):
            PackedBCD.encode(123)

    def test_negative_rejected(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.encode(-1)

    def test_bool_rejected(self):
        # bool is a subclass of int; we reject it to avoid surprising
        # implicit conversions (True -> b'\x01' would be ambiguous).
        with self.assertRaises(BCDOverflowError):
            PackedBCD.encode(True)

    def test_non_int_rejected(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.encode("12")

    def test_trailing_zeros_preserved(self):
        # Packed BCD is digit-wise, so trailing zeros are significant data.
        self.assertEqual(PackedBCD.encode(1200), b"\x12\x00")


class TestPackedDecode(unittest.TestCase):
    def test_single_byte(self):
        self.assertEqual(PackedBCD.decode(b"\x12"), 12)

    def test_zero_byte(self):
        self.assertEqual(PackedBCD.decode(b"\x00"), 0)

    def test_multi_byte(self):
        self.assertEqual(PackedBCD.decode(b"\x12\x34"), 1234)
        self.assertEqual(PackedBCD.decode(b"\x12\x34\x56"), 123456)

    def test_all_nines(self):
        self.assertEqual(PackedBCD.decode(b"\x99"), 99)
        self.assertEqual(PackedBCD.decode(b"\x99\x99"), 9999)

    def test_bytearray_accepted(self):
        # Decoding accepts bytearray as well as bytes, since both are
        # reasonable byte containers.
        self.assertEqual(PackedBCD.decode(bytearray(b"\x12\x34")), 1234)

    def test_invalid_high_nibble(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.decode(b"\xA0")

    def test_invalid_low_nibble(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.decode(b"\x0A")

    def test_non_bytes_rejected(self):
        with self.assertRaises(BCDOverflowError):
            PackedBCD.decode(0x12)
        with self.assertRaises(BCDOverflowError):
            PackedBCD.decode("12")


class TestPackedRoundTrip(unittest.TestCase):
    def test_round_trip(self):
        for value in (0, 12, 99, 1234, 9999, 123456, 999999):
            self.assertEqual(PackedBCD.decode(PackedBCD.encode(value)), value)


class TestUnpackedEncode(unittest.TestCase):
    def test_single_digit(self):
        self.assertEqual(UnpackedBCD.encode(1), b"\x01")

    def test_zero(self):
        self.assertEqual(UnpackedBCD.encode(0), b"\x00")

    def test_multi_digit(self):
        self.assertEqual(UnpackedBCD.encode(123), b"\x01\x02\x03")

    def test_all_nines(self):
        self.assertEqual(UnpackedBCD.encode(99), b"\x09\x09")

    def test_negative_rejected(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.encode(-1)

    def test_bool_rejected(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.encode(True)

    def test_non_int_rejected(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.encode("12")

    def test_trailing_zeros_preserved(self):
        self.assertEqual(UnpackedBCD.encode(100), b"\x01\x00\x00")


class TestUnpackedDecode(unittest.TestCase):
    def test_single_byte(self):
        self.assertEqual(UnpackedBCD.decode(b"\x01"), 1)

    def test_zero(self):
        self.assertEqual(UnpackedBCD.decode(b"\x00"), 0)

    def test_multi_byte(self):
        self.assertEqual(UnpackedBCD.decode(b"\x01\x02\x03"), 123)

    def test_all_nines(self):
        self.assertEqual(UnpackedBCD.decode(b"\x09\x09"), 99)

    def test_bytearray_accepted(self):
        self.assertEqual(
            UnpackedBCD.decode(bytearray(b"\x01\x02\x03")), 123
        )

    def test_invalid_byte_high_nibble(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.decode(b"\x12")

    def test_invalid_byte_too_large(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.decode(b"\x0A")

    def test_non_bytes_rejected(self):
        with self.assertRaises(BCDOverflowError):
            UnpackedBCD.decode(12)


class TestUnpackedRoundTrip(unittest.TestCase):
    def test_round_trip(self):
        for value in (0, 1, 9, 12, 99, 123, 9999):
            self.assertEqual(
                UnpackedBCD.decode(UnpackedBCD.encode(value)), value
            )


if __name__ == "__main__":
    unittest.main()
