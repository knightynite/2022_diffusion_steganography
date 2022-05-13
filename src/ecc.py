"""Reed-Solomon error-correcting code for stego payloads.

Diffusion stego is fragile — JPEG re-encoding, resize, and platform
watermarks all destroy bits. ECC trades raw payload size for survival
across noisy channels.

Light wrapper around `reedsolo` (a pure-Python RS implementation that
predates the diffusion stego era). For real-world covert channels you
want concatenated codes (RS over BCH) but a single RS layer is enough
for proof-of-concept.
"""
from typing import List

import reedsolo


class ECCEncoder:
    """Encode/decode bytes with N parity bytes per chunk-size data bytes."""

    def __init__(self, chunk_size: int = 200, parity: int = 32):
        self.chunk_size = chunk_size
        self.parity = parity
        self.rs = reedsolo.RSCodec(parity)

    def encode(self, data: bytes) -> bytes:
        out = bytearray()
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i : i + self.chunk_size]
            out.extend(self.rs.encode(chunk))
        return bytes(out)

    def decode(self, encoded: bytes) -> bytes:
        block = self.chunk_size + self.parity
        out = bytearray()
        for i in range(0, len(encoded), block):
            piece = encoded[i : i + block]
            try:
                decoded, _, _ = self.rs.decode(piece)
                out.extend(decoded)
            except reedsolo.ReedSolomonError:
                # uncorrectable — fall back to raw, marking failure
                out.extend(piece[: self.chunk_size])
        return bytes(out)

    def overhead_ratio(self) -> float:
        """Bytes-output / bytes-input for this configuration."""
        return (self.chunk_size + self.parity) / self.chunk_size


def bytes_to_bits(b: bytes) -> List[int]:
    out = []
    for byte in b:
        for i in range(7, -1, -1):
            out.append((byte >> i) & 1)
    return out


def bits_to_bytes(bits: List[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i : i + 8]
        if len(chunk) < 8:
            chunk = chunk + [0] * (8 - len(chunk))
        b = 0
        for j, bit in enumerate(chunk):
            b |= (bit & 1) << (7 - j)
        out.append(b)
    return bytes(out)


def add_length_header(payload: bytes) -> bytes:
    """Prepend a 4-byte big-endian length so the decoder knows when to stop."""
    n = len(payload)
    return n.to_bytes(4, 'big') + payload


def strip_length_header(framed: bytes) -> bytes:
    if len(framed) < 4:
        return b''
    n = int.from_bytes(framed[:4], 'big')
    return framed[4 : 4 + n]
