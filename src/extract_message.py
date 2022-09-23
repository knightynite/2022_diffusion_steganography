"""Extract a hidden message from a stego image.

This demo extractor brute-forces a small candidate dictionary, regenerating
each candidate's image and matching against the input. In a real protocol
the message would be carried by structured noise and recovered analytically;
this is sufficient to demonstrate the channel.
"""
import hashlib
import sys
from itertools import product

import numpy as np
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image


PROMPT = 'a watercolor painting of a quiet harbor at dusk'
SALT = b'stego2022'

# Candidate dictionary — tune to your use case
DICT = ['attack at dawn', 'meet at noon', 'hold the line', 'secret message',
        'go now', 'wait for signal']


def msg_to_seed(msg: str) -> int:
    return int.from_bytes(
        hashlib.sha256(SALT + msg.encode('utf-8')).digest()[:4], 'big')


