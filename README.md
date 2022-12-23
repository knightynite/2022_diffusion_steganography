# 2022 — Diffusion-Based Steganography

Hide messages inside Stable-Diffusion-generated images. Use the deterministic noise
seed as the shared secret: encoder and decoder run the same diffusion pipeline, the
message is encoded into the *initial latent noise* used for sampling.

## Approach

1. Convert the secret message to a bitstring, then to a deterministic seed (or to a
   structured perturbation of the initial noise).
2. Generate an image with that seed using a fixed prompt.
3. Receiver, knowing the prompt + extraction protocol, regenerates and recovers the
   message.

This is *fragile* steganography (any re-encoding/cropping breaks it) but it
demonstrates the conceptual class of attacks where generated content carries hidden
payload that's invisible to the visual channel.


## Files

- `src/diffusion_stego.py` — encode message → seed → image
- `src/extract_message.py` — extract message from image given prompt + protocol


## Run

```bash
pip install -r requirements.txt
python src/diffusion_stego.py "secret message" stego.png
python src/extract_message.py stego.png
```

You'll need a HuggingFace account for the SD weights:
```bash
huggingface-cli login
```


## Caveats — read before publishing anything you build on this

- Modern image distribution platforms re-encode (JPEG, resize, watermark). Real covert
  channels through these need redundancy + ECC.
- This is intentionally a small-payload channel — kilobits, not megabytes.
- Detection-side research (forensics for diffusion-generated content) is the more
  defensively useful direction.
