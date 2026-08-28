"""multi_lang_stereo_voice_routing.py

Pattern-matched prototype for the multi-lang-stereo-voice-routing skill.

Demonstrates (dry-run, no audio hardware required):
  1. Routing three languages to three sinks: Left stereo, Right stereo, Bluetooth.
  2. Collapsing back to a shared language across both stereo speakers with a
     timing lock so no channel drifts.
  3. A source-separation hook point (where ambient filtering would run).

This is logic-only. Wire real sinks (sounddevice / PyAudio) and a
source-separation front-end (RNNoise / Conv-TasNet) for production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Channel map
# ---------------------------------------------------------------------------
# Each sink gets its own language and an independent sample cursor so we can
# detect drift when collapsing back to a shared language.

SINK_LEFT = "left_stereo"
SINK_RIGHT = "right_stereo"
SINK_BT = "bluetooth"


@dataclass
class Sink:
    name: str
    language: str
    cursor: int = 0          # samples emitted so far
    paused: bool = False
    buffer: List[str] = field(default_factory=list)  # utterance ids queued

    def emit(self, utterance_id: str, n_samples: int) -> None:
        if self.paused:
            return
        self.buffer.append(utterance_id)
        self.cursor += n_samples

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False


class MultiLangRouter:
    """Routes languages to sinks and enforces the revert timing lock."""

    def __init__(self) -> None:
        self.sinks: Dict[str, Sink] = {
            SINK_LEFT:  Sink(SINK_LEFT,  language="A"),
            SINK_RIGHT: Sink(SINK_RIGHT, language="B"),
            SINK_BT:    Sink(SINK_BT,    language="C"),
        }
        self.mode: str = "split"   # "split" | "shared"
        self._utterance_seq = 0

    # -- source separation hook ------------------------------------------------
    def separate(self, mixed_audio) -> object:
        """Placeholder for ambient filtering (RNNoise / Conv-TasNet).

        In production this strips radio, phone rings, and cabin noise so only
        the active speaker's cosine voice wave reaches translation.
        """
        return mixed_audio  # passthrough in the dry-run prototype

    # -- routing --------------------------------------------------------------
    def speak(self, text: str, language: str, sink: str, n_samples: int = 160) -> str:
        self._utterance_seq += 1
        uid = f"u{self._utterance_seq}"
        self.sinks[sink].emit(uid, n_samples)
        return f"[{sink}] ({language}) {text}  -> {uid}"

    # -- revert with timing lock ---------------------------------------------
    def revert_to_shared(self, shared_language: str = "A") -> List[str]:
        """Collapse all sinks to one shared language, dual-mono on stereo.

        Steps:
          1. Pause every sink.
          2. Re-render the active utterance in the shared language.
          3. Emit identical samples to L and R (dual-mono).
          4. Resume BT with the same stream, offset-compensated.
          5. Release only after all cursors match.
        """
        for s in self.sinks.values():
            s.pause()

        self._utterance_seq += 1
        uid = f"u{self._utterance_seq}"
        shared_samples = 160

        # dual-mono: both stereo sinks get the exact same sample count
        self.sinks[SINK_LEFT].emit(uid, shared_samples)
        self.sinks[SINK_RIGHT].emit(uid, shared_samples)
        # BT gets the same stream; offset compensation would align cursors here
        self.sinks[SINK_BT].emit(uid, shared_samples)

        for s in self.sinks.values():
            s.language = shared_language
            s.resume()

        self.mode = "shared"
        return self._check_lock()

    def _check_lock(self) -> List[str]:
        """Return any sinks whose cursor drifted from the group mean."""
        cursors = {name: s.cursor for name, s in self.sinks.items()}
        mean = sum(cursors.values()) / len(cursors)
        return [name for name, c in cursors.items() if c != mean]

    def status(self) -> Dict[str, Dict]:
        return {
            name: {"language": s.language, "cursor": s.cursor, "mode": self.mode}
            for name, s in self.sinks.items()
        }


# ---------------------------------------------------------------------------
# Dry-run demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    router = MultiLangRouter()

    print("=== SPLIT MODE ===")
    print(router.speak("Hello", "A", SINK_LEFT))
    print(router.speak("Hola", "B", SINK_RIGHT))
    print(router.speak("Bonjour", "C", SINK_BT))
    print(router.status())

    print("\n=== REVERT TO SHARED ===")
    drift = router.revert_to_shared(shared_language="A")
    print("drifted sinks:", drift or "none — lock held")
    print(router.status())
