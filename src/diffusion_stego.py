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


def generate(message: str, out_path: str, model_id='runwayml/stable-diffusion-v1-5'):
    seed = message_to_seed(message)
    print(f'message -> seed: {seed}')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16 if device == 'cuda' else torch.float32
    ).to(device)

    generator = torch.Generator(device=device).manual_seed(seed)
    image = pipe(PROMPT, generator=generator, num_inference_steps=30).images[0]
    image.save(out_path)
    print(f'saved {out_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: diffusion_stego.py "message" out.png')
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
