"""Encode a short message as a Stable Diffusion seed and generate the image.

Protocol (toy/demo):
  - hash(message + salt) -> 32-bit seed
  - prompt is fixed and shared between sender and receiver
  - receiver brute-force-searches over a candidate message dictionary

This is a demonstration of the *channel*. For a real covert channel you'd
encode bits into a high-entropy structured perturbation of the initial latent,
not via brute-force seed search.
"""
import hashlib
import sys

import torch
from diffusers import StableDiffusionPipeline


PROMPT = 'a watercolor painting of a quiet harbor at dusk'
SALT = b'stego2022'


def message_to_seed(msg: str) -> int:
    h = hashlib.sha256(SALT + msg.encode('utf-8')).digest()
    return int.from_bytes(h[:4], 'big')  # 32-bit seed


