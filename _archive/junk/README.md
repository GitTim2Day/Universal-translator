# Archived junk — 2026-10-05

This folder holds the accidental `https:` path tree that appeared in the repository root. It was not code: it was a literal URL path (`https://raw.githubusercontent.com/GitTim2Day/<repo>/main/example4d.nii.gz`) committed as a directory structure, likely from a pasted link or a bad clone path.

## What was moved

- `https:/raw.githubusercontent.com/GitTim2Day/<repo>/main/example4d.nii.gz` — a 74-byte text file containing only the URL string itself. Not a real NIfTI image.

## Why archived, not deleted

- Preserves the commit history and the original blob SHA.
- Keeps the root tree clean for anyone cloning or browsing.
- If the real `example4d.nii.gz` (a 4D NIfTI medical imaging file) is ever needed, it should be re-added as a proper binary at the repo root or in a `data/` folder.

## Note on the placeholder

The path contained the literal string `<repo>` — a template placeholder that was never substituted. This confirms the junk was created by a pasted or templated URL, not by any build step.
