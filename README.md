# Universal-translator
Real-time speech translator for I rebuilt the whole thing: the discriminator plus its own attack suite, all passing (28/28). To be clear, this is a **new build, not a recovery.** The originals in your September 11 code hop are still unread, and if they turn up, they win. That's why I gave these files their own dated names instead of reusing yours; I didn't want to squat on the canonical filenames.

| File | Lines | SHA-256 |
|---|---|---|
| `voice_discriminator_rebuild_2026_09_21.py` | 595 | `9886a016…b60d5` |
| `attack_voice_discriminator_rebuild_2026_09_21.py` | 212 | `c4d14f75…bc7a7` |
| `run.log` (the 28/28 run) | — | `335bdeee…3bef1` |

## What it answers, per burst of speech
- **Same or different human:** it matches the burst to an enrolled speaker, or returns UNKNOWN.
- **Human or AI:** it returns HUMAN, AI, or UNDETERMINED.
- **Which AI:** each AI voice is its own enrolled identity.
- **Combination:** if a burst resolves to two identities, it returns MIXED with both names.
- **Relation to the previous burst:** SAME_SPEAKER, DIFFERENT_HUMAN, DIFFERENT_AI, HUMAN_TO_AI, or AI_TO_HUMAN.

## How it avoids the August 20 audit's defects
- **No fixed human/AI threshold anywhere.** The HUMAN or AI call comes only from voices you've enrolled and labeled. Test T23 proves it: swapping the labels flips the verdict. A voice outside every enrolled speaker's range is UNKNOWN, never guessed human.
- **Pitch is one feature of nine,** measured with a method (YIN) that resists octave errors. Test T09 confirms 150 Hz reads as 150, not 300.
- **Input must already be 16-bit mono 16 kHz WAV.** It refuses anything else rather than resampling silently. Decode with `ffmpeg -i in.m4a -ac 1 -ar 16000 -c:a pcm_s16le out.wav`, without `-c copy`.
- **Every hash covers exactly the bytes it names,** and output is read back and re-verified before release.

## Two real defects the tests caught and I fixed
1. **An uncalibrated roster leaked a crash** instead of refusing cleanly. It now refuses at the entry guard.
2. **The zero-radius trap.** When an enrolled voice's recordings were identical, its acceptance radius came out exactly 0.0, which is a stored zero and a gate so tight it rejected that voice itself. The same pattern as the September 8 filter's zero-MAD branch, and a real risk with repeatable AI voices. Instead of inventing a tolerance, it now refuses enrollment until the recordings carry real variation.

## Honest limits
- **Standing is ASSERTED.** The tests use synthetic voices, so they prove the code paths and the airlock, not accuracy on real speech. To earn it: enroll at least 3–4 varied clips each of you, Poly, and any other AI or person, run `GOSUB_Holdout` on separate labeled clips, and seal the counts.
- **Two declared, uncalibrated settings** appear in every output header: the speech threshold (about 12 dB over the noise floor) and the pitch threshold (0.15, the default from the published YIN method). Segmentation also needs some non-speech in the recording to find its noise floor.
- **It's pure Python,** so it's slow: roughly several seconds per second of audio. That's fine for review on a laptop but not for real time on the Pi yet.
- **Truly overlapping speech,** two people talking at once, is only caught when the sub-windows resolve to different speakers. It doesn't separate simultaneous voices.

**Auto-route:** I ran the attack suite until it passed before handing anything over, fixed defects rather than adjusting tests to pass, and sealed all three files. I haven't emailed them to the ledger; say the word and I'll send them as attachments.
