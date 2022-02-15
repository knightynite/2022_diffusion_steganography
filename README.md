# 2022 — Diffusion-Based Steganography

Hide messages inside Stable-Diffusion-generated images. Use the deterministic noise
seed as the shared secret: encoder and decoder run the same diffusion pipeline, the
message is encoded into the *initial latent noise* used for sampling.
