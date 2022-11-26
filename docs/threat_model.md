# Threat model

## Channel assumptions

Sender and receiver share:
1. Knowledge of the diffusion model + checkpoint hash
2. The text prompt that conditions generation
3. The encoding/decoding protocol (seed-from-message, ECC parameters)

The "image looks plausible" property comes from diffusion's natural prior —
generated images pass casual visual inspection.

## Attacker capabilities

The interesting attacker is **a content-distribution platform** that:

- Re-encodes uploaded images (JPEG, WebP, AVIF) at lower quality
- Resizes / crops to fit display constraints
- Applies perceptual hashing for duplicate detection
- May add watermarks (visible or invisible)
- Logs metadata and may run statistical detectors over time

Each of these *destroys some bits*. The platform doesn't need to know stego
is happening — just doing its job will gradually break a payload that
isn't ECC-protected.

A more sophisticated attacker is a **steganalysis adversary** who:

- Suspects this image carries a payload
- Has access to the model + prompt (for known-system attacks)
- Wants to either extract the payload or destroy it without breaking
  the cover image

This is the harder threat. Statistical detection of diffusion-stego is an
active research area; tree-ring watermarks and similar techniques can
detect "this image came from this model" but extracting the message
typically requires the prompt.

## Defender (sender) goals

In order of importance:

1. **Plausible cover.** Image looks natural, doesn't trip casual review.
2. **Receiver can decode.** Even after re-encoding, ECC + redundancy
   recover the message.
3. **Detection-resistant.** Statistical analysis doesn't flag the image
   as anomalous against the model's natural output distribution.

(3) is hard. Anyone with the model can compare your image's likelihood
under the prior to baseline outputs. If your seed-encoding biases the
distribution noticeably, that's detectable.

## Capacity / robustness tradeoffs

  Channel               Capacity     Survives JPEG?     Survives resize?
  --------------------  -----------  -----------------  ----------------
  Pure latent seed      ~256 bits    ✗                  ✗
  Latent + ECC          ~128 bits    Sometimes (q≥85)   ✗
  LSB stego (baseline)  ~3 bpp       ✗                  ✗
  Frequency-domain DCT  Lower        Yes (mod q)        Sometimes

Diffusion stego is in the "low capacity but plausible cover" regime.
For high-bandwidth covert channels you want a different primitive.

## Out of scope

- Multi-image redundancy (sending the same payload across several images)
- Active error-correction with feedback (requires bidirectional channel)
- Cryptographic confidentiality (assume payload is pre-encrypted; ECC
  here only addresses survival, not secrecy)
- Attacker who can inject their own generated images into your channel

## What could go very wrong

If a receiver decodes the wrong payload (e.g., because they used the
wrong prompt) and acts on it, you have a very different kind of bug.
Always include a HMAC / authenticated checksum in the payload so
mis-decoded data is detected before being used.
