"""LSB steganography baseline for comparison.

The simplest stego: hide bits in the least-significant bit of each pixel
channel. Compared to diffusion-stego it has:

  - much higher capacity (bits per pixel = 1)
  - much lower robustness — any re-encoding shifts pixel values
  - no plausibility against statistical analysis (chi-square detects easily)

Useful as a baseline because it lets you say "diffusion gives us X% the
capacity but Y× more robustness across re-encoding pipelines".
"""
from typing import Tuple

import numpy as np
from PIL import Image

from src.ecc import bits_to_bytes, bytes_to_bits


def lsb_encode(image_path: str, message: bytes, output_path: str) -> Tuple[int, int]:
    """Embed message into image LSBs. Returns (bits_used, capacity)."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img, dtype=np.uint8)
    flat = arr.reshape(-1)

    payload = (len(message).to_bytes(4, 'big') + message)
    bits = bytes_to_bits(payload)
    capacity = flat.size

    if len(bits) > capacity:
        raise ValueError(
            f"message + 4-byte header is {len(bits)} bits but image holds {capacity}"
        )

    for i, b in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | (b & 1)

    out = flat.reshape(arr.shape)
    Image.fromarray(out).save(output_path, 'PNG')
    return len(bits), capacity


def lsb_decode(image_path: str) -> bytes:
    img = Image.open(image_path).convert('RGB')
    flat = np.array(img, dtype=np.uint8).reshape(-1)

    bits = (flat & 1).tolist()
    header_bits = bits[:32]
    n = 0
    for b in header_bits:
        n = (n << 1) | b
    message_bits = bits[32 : 32 + 8 * n]
    return bits_to_bytes(message_bits)


def chi_square_lsb(image_path: str) -> float:
    """Sample chi-square statistic on pair-of-values for LSB detection.

    Higher = more likely the LSBs are uniformly distributed (stego),
    lower = more natural-image-like correlation. Not a complete
    detector — see Westfeld & Pfitzmann 2000 for the canonical test.
    """
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img, dtype=np.uint8).reshape(-1)
    pairs = arr // 2 * 2
    expected = np.bincount(pairs, minlength=256) / 2
    observed_even = np.bincount(arr, minlength=256)[0::2]
    expected_pair = expected[0::2]
    mask = expected_pair > 5  # need enough samples for chi-square
    if mask.sum() == 0:
        return 0.0
    chi2 = np.sum(
        (observed_even[mask] - expected_pair[mask]) ** 2 / expected_pair[mask]
    )
    return float(chi2)
