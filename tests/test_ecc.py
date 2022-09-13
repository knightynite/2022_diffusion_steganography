"""Tests for ECC encoding + bit packing helpers."""
import unittest

from src.ecc import (
    ECCEncoder,
    add_length_header,
    bits_to_bytes,
    bytes_to_bits,
    strip_length_header,
)


class TestBitPacking(unittest.TestCase):
    def test_round_trip(self):
        cases = [b'', b'a', b'hello world', bytes(range(64))]
        for c in cases:
            self.assertEqual(bits_to_bytes(bytes_to_bits(c)), c, msg=f"failed: {c}")

    def test_bit_count(self):
        self.assertEqual(len(bytes_to_bits(b'\xff')), 8)
        self.assertEqual(len(bytes_to_bits(b'\xff\x00')), 16)


class TestLengthHeader(unittest.TestCase):
    def test_round_trip(self):
        for payload in [b'', b'x', b'\x00\x01\x02', b'longer payload here']:
            framed = add_length_header(payload)
            self.assertEqual(strip_length_header(framed), payload)

    def test_bad_input(self):
        self.assertEqual(strip_length_header(b''), b'')
        self.assertEqual(strip_length_header(b'\x00'), b'')


class TestECCEncoder(unittest.TestCase):
    def test_round_trip_clean(self):
        enc = ECCEncoder(chunk_size=64, parity=16)
        msg = b'hello, this is a covert payload of moderate size'
        encoded = enc.encode(msg)
        self.assertGreater(len(encoded), len(msg))
        decoded = enc.decode(encoded)
        # length is preserved up to chunk-size padding
        self.assertTrue(decoded.startswith(msg))

    def test_corrects_a_few_errors(self):
        enc = ECCEncoder(chunk_size=64, parity=16)
        msg = b'A' * 64
        encoded = bytearray(enc.encode(msg))
        # corrupt 4 bytes (less than parity/2 = 8)
        for i in [3, 17, 25, 41]:
            encoded[i] ^= 0xFF
        decoded = enc.decode(bytes(encoded))
        self.assertEqual(decoded, msg)

    def test_overhead_ratio_sensible(self):
        enc = ECCEncoder(chunk_size=200, parity=32)
        self.assertLess(enc.overhead_ratio(), 1.5)
        self.assertGreater(enc.overhead_ratio(), 1.0)


if __name__ == '__main__':
    unittest.main()
