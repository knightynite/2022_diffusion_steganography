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


def image_distance(a: Image.Image, b: Image.Image) -> float:
    a = np.asarray(a.convert('RGB'), dtype=np.float32)
    b = np.asarray(b.convert('RGB'), dtype=np.float32)
    return float(np.mean((a - b) ** 2))


def extract(image_path: str, model_id='runwayml/stable-diffusion-v1-5'):
    target = Image.open(image_path)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16 if device == 'cuda' else torch.float32
    ).to(device)

    best = (None, float('inf'))
    for candidate in DICT:
        seed = msg_to_seed(candidate)
        gen = torch.Generator(device=device).manual_seed(seed)
        img = pipe(PROMPT, generator=gen, num_inference_steps=30).images[0]
        d = image_distance(img, target)
        print(f'  {candidate:20s}  MSE = {d:9.2f}')
        if d < best[1]:
            best = (candidate, d)
    print(f'\nbest match: "{best[0]}"')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: extract_message.py stego.png')
        sys.exit(1)
    extract(sys.argv[1])
