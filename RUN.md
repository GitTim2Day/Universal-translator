# Universal-translator — Run notes (fail-closed)

Honest status as of 2026-09-18: partial. No `requirements.txt` existed before this fix branch.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Entrypoints

| Path | What it does | Notes |
|------|----------------|-------|
| `python app.py` | Gradio mic UI + Whisper ASR + NLLB eng→spa demo | Downloads `openai/whisper-large-v3-turbo` and `facebook/nllb-200-distilled-600M` on first run (large; needs network + disk). Uses CPU in source. |
| `python adapted_k9.py` | SecureLog AES-GCM + SHA-512 chain smoke | Stdlib + `cryptography`. `__main__` uses stub translations (not live ASR). |
| `python multi_lang_stereo_voice_routing.py` | Dry-run stereo/BT language routing | Stdlib only. No audio hardware. |

## Blockers (named, not invented away)

1. **No prior lockfile** — versions unpinned; install may resolve differently across machines.
2. **Model download** — first `app.py` launch pulls heavy Hugging Face models; offline runs fail until cached.
3. **`torch` not imported** — not listed in requirements; if `transformers` ASR/translation pipelines require it on your platform, pip may install it as a transitive dep or fail until you add it yourself after observing the error.
4. **Gradio Audio API** — `gr.Audio(source="microphone", ...)` may need Gradio version-compatible args depending on resolver.
5. **Odd path `https:`** — present in tree; not a run entrypoint documented here.
6. Advanced K9 tier described as not on GitHub — do not invent bodies for it.

## Do not

- Do not invent `kbld9_core_r4` or Base360 CSV here (those are out of scope for this repo).
- Do not stub missing sealed modules.
