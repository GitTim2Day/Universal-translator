# Accessibility System — Pseudocode (language-agnostic)
# Source: MASTER_ACCESSIBILITY_SYSTEM_MAP.md — 2026-09-19
# Re-implement in any stack; truncate never round; fail-closed on invent.

# ============================================================
# SHARED TYPES / CONSTANTS
# ============================================================

ENUM Profile = { BLIND, DEAF, DEAFBLIND, HEARING }

ENUM Severity =
  AUTHORITIES_FIRST,    # crash, fire, violence, unresponsive, severe bleed
  BACKUP_FIRST,         # milder fall / stuck; backup may escalate
  AUTHORITIES_OR_BACKUP # ambiguous → prefer authorities if doubt

ENUM RadioPick = { CELLULAR, WIFI, BLUETOOTH, NONE }

STRUCT Roster
  authorities_number   # earned only; never invent
  backup_contacts[]    # ordered; earned only

STRUCT BeaconPayload
  node_id
  canned_rom_text
  timestamp
  gps_if_available

STRUCT TubeCell
  cells_nominal_count = 20..30   # tube-type form factor
  energy_for_one_shot_only       # not full session UPS
  depleted: BOOL

STRUCT MiniBrain
  node_id
  tube: TubeCell
  radio_modem                     # cellular preferred
  roster_pointer: Roster          # fail-closed if empty
  rom_sos: STRING

# ============================================================
# GLOBAL: EMERGENCY OVERLAY (fires from ANY node)
# ============================================================

PROCEDURE EmergencyOverlay(trigger, severity_hint, working_modality):
  # Order is fixed: detect → classify → select → confirm → dispatch → log
  event ← DetectEmergency(trigger)
  IF event is NIL THEN RETURN

  band ← ClassifyType(event, severity_hint)
  path ← SelectContactPath(band, GLOBAL.roster)
  IF path is UNDEF THEN
    Log("fail-closed: empty roster")
    LocalSosBeacon()
    RETURN

  confirmed ← ConfirmDispatch(working_modality, band)
  # hard timeout: IF high severity AND no response THEN dispatch anyway
  IF confirmed = CANCEL THEN
    Log(event, "aborted by user")
    RETURN

  ok ← Dispatch(path)   # cellular priority; NOT queued on Wi-Fi-only offline
  IF NOT ok THEN
    ok2 ← DispatchSecondary()  # satellite / second SIM IF earned
    IF NOT ok2 THEN LocalSosBeacon()
  Log(event, band, path, ok)
END

FUNCTION DetectEmergency(trigger):
  IF trigger IN { SOS_KEY, "call 911", crash_IMU, fall_detect, smoke, medical_alert, attendant_override }
    RETURN Event(trigger)
  RETURN NIL
END

FUNCTION ClassifyType(event, hint):
  IF event is auto_crash OR fire OR violence OR unresponsive OR severe_bleed
    RETURN AUTHORITIES_FIRST
  IF event is explicit_sos_911
    RETURN AUTHORITIES_FIRST
  IF event is fall AND user_says_help_not_911
    RETURN BACKUP_FIRST
  IF event is fall AND (severe OR no_confirm_in_timeout)
    RETURN AUTHORITIES_FIRST   # or AUTHORITIES_OR_BACKUP per policy
  IF hint is set THEN RETURN hint
  RETURN AUTHORITIES_OR_BACKUP   # prefer authorities if doubt
END

FUNCTION SelectContactPath(band, roster):
  IF roster empty THEN RETURN UNDEF
  IF band = AUTHORITIES_FIRST THEN RETURN Path(authorities, notify_backup_parallel=TRUE)
  IF band = BACKUP_FIRST THEN RETURN Path(backup_first, escalate_911_if_unreachable=TRUE)
  RETURN Path(authorities_preferred_or_backup_with_timeout)
END

FUNCTION ConfirmDispatch(modality, band):
  # GETKEY$-style: only Y submits; anything else = revise/abort policy per band
  Show("Submit emergency? (Y/N)", modality)  # Braille / captions / haptic Y-row
  key ← WaitKeyWithTimeout(HARD_TIMEOUT)
  IF key = 'Y' THEN RETURN CONFIRM
  IF key = CANCEL_OR_N AND band is not high THEN RETURN CANCEL
  IF timeout AND band IN { AUTHORITIES_FIRST, high } THEN RETURN CONFIRM  # dispatch anyway
  RETURN CANCEL
END

FUNCTION Dispatch(path):
  # Offline/local-only MUST NOT queue this — use priority bearer
  IF CellularUp() THEN RETURN DialOrSms(path)
  IF SatelliteEarned() THEN RETURN SatelliteSend(path)
  RETURN FALSE
END

# ============================================================
# PER-NODE MINI-BRAIN + 20–30 TUBE ONE-SHOT BEACON
# ============================================================

PROCEDURE OnNodeDying(brain: MiniBrain):
  # Independent of main power bus and main AI pipeline
  IF brain.tube.depleted THEN
    LocalHapticLedSos()
    RETURN
  IF ActuatorsRunning(brain) THEN TorqueOff(brain)   # hand: no gesture show on dying budget
  IF BrailleThrashing(brain) THEN SkipRefresh(brain) # ROM text only

  radio ← PickRadio(brain)   # CELLULAR > WIFI > BLUETOOTH > NONE
  IF radio = NONE THEN
    LocalHapticLedSos()
    RETURN

  IF radio = CELLULAR AND ModemNotRegistered(brain) THEN
    # FLAG: cold attach may burn one-shot before payload
    IF NOT TryWarmOrAbort(brain) THEN
      Log("cold-modem risk")
      # still attempt one SMS if energy remains
    END
  END

  payload ← BeaconPayload(brain.node_id, brain.rom_sos, Now(), GpsIfAny())
  IF radio = CELLULAR THEN
    # Intended window: one SMS / short data — NOT long voice 911 minutes
    ok ← SendSmsOrShortData(brain, payload)
    IF NOT ok THEN TryWifiOrBt(brain, payload)
  ELSE IF radio = WIFI THEN
    ok ← ShortPing(brain, payload)   # prefer cached associate
  ELSE
    ok ← BtAlertToPhone(brain, payload)  # phone may dial
  END
  brain.tube.depleted ← TRUE   # one-shot consumed
  LogBeacon(brain, radio, ok)
END

FUNCTION PickRadio(brain):
  IF CellularAvailable(brain) THEN RETURN CELLULAR
  IF WifiAvailable(brain) THEN RETURN WIFI
  IF BluetoothPeerAvailable(brain) THEN RETURN BLUETOOTH
  RETURN NONE
END

# Power budget flags (do not claim lab Wh):
#   BLE / short Wi-Fi / one SMS  → intended for 20–30 tube pack
#   Long voice 911, cold attach, actuator thrash, Braille full refresh → may NOT fit

# ============================================================
# NODE 1 — TEXT PIPELINE (core NLP / message assembly)
# ============================================================

PROCEDURE TextPipeline_Run(input):
  out ← CoreAssemble(input)
  IF out empty OR hang THEN
    out ← RetryOnce(Shorten(input))
    IF out empty THEN
      FanOutCanned("Please wait")
      QueueUserInput()
      RETURN
    END
  END
  IF UnsafeOrGarbage(out) THEN
    RefuseGate()
    FanOut(SafeTemplate())
    Log()
    RETURN   # never drive Braille/sign/caption with ungated text
  END
  IF ExactDecideHeld() THEN
    StayTextOnlyOrQueued()
    AskConfirm(WorkingModality())
    RETURN
  END
  FanOutToModalityRouter(out, user.profile)
EXCEPTION LocalCrash:
  RestartEdgeWorker()
  OfflinePhraseBank_On(Braille, Captions)
  # Emergency overlay still available from surviving node brains
END

PROCEDURE FanOutToModalityRouter(text, profile):
  CASE profile
    BLIND:     Braille_Output(text)
    DEAF:      Caption_Display(text) ; IF fail THEN SigningHand(text)
    DEAFBLIND: Braille_Output(text) ; SigningHand_Tactile(text)  # never audio-only
    HEARING:   Caption_Display(text) ; optional Piper(text)
  END
END

# ============================================================
# NODE 2 — BRAILLE OUTPUT
# ============================================================

PROCEDURE Braille_Output(text):
  IF DisplayUnplugged OR UsbDead THEN
    HotSwapSense()
    IF HearingOK() THEN Piper_TTS(text)
    ELSE IF ScreenLeft() THEN LargePrintCaptions(text)
    ELSE HapticBuzz("error / wait")
    OnNodeDying(BRAILLE.brain)   # independent beacon if this is terminal
    RETURN
  END
  IF CellsStuck OR DriverError THEN
    ResetDriverOnce()
    IF still bad THEN
      IF HearingOK() THEN Piper_TTS(text) ELSE CaptionMirror(text)
      OnNodeDying(BRAILLE.brain)
      RETURN
    END
  END
  IF TooLongForCells(text) THEN
    PageSegment(text)  # next-page key
    IF HearingOK() THEN AudioContinuation(rest)
  ELSE
    WriteCells(text)
  END
END
# Fallbacks: TTS(if hearing) → captions → haptic → ROM
# Emergency: hardware SOS still live; beacon = mini-brain + tube

# ============================================================
# NODE 3 — CAPTION DISPLAY (separate daemon)
# ============================================================

PROCEDURE Caption_Display(text):
  IF ScreenOff OR AppCrashed THEN
    RelaunchCaptionSurface()
    IF still fail THEN
      Braille_Mirror(text)
      IF still fail THEN SigningHand_FingerspellOrKeywords(text)
      IF still fail AND HearingOK() THEN Piper_TTS(text)
      OnNodeDying(CAPTION.brain)
      RETURN
    END
  END
  IF FontContrastBad THEN BumpPreset() ; IF still bad THEN Braille_Mirror(text)
  IF NoDisplayHardware THEN Prefer(Braille, SigningHand) ; audio if applicable
  ShowCaptions(text)
END
# Emergency: SOS button / haptic confirm bypasses UI process
# Beacon: caption daemon mini-brain + 20–30 tube

# ============================================================
# NODE 4 — SIGNING-HAND ACTUATOR
# ============================================================

PROCEDURE SigningHand(text):
  IF ActuatorOffline OR Jam THEN
    SafeTorqueOff()
    Caption_Display(text)
    IF fail THEN Braille_Output(text)
    IF fail AND HearingOK() THEN Piper_TTS(text)
    OnNodeDying(SIGN.brain)   # radio only; no gesture show on tube budget
    RETURN
  END
  IF GestureLibraryMiss(text) THEN
    Fingerspell(vocab)
    Caption_Display(full_sentence)
  ELSE IF AmbiguousSign THEN
    Hold()
    CaptionClarify()   # should-speak/sign gate
  ELSE
    PerformSigns(text)
  END
END
# Emergency does not block 911 dial
# Beacon: torque-off + mini-brain + tube

# ============================================================
# NODE 5 — NETWORK / CONNECTIVITY
# ============================================================

PROCEDURE Network_Watch():
  IF CloudApiDown THEN
    FailSoft_LocalPipeline(Vosk_or_WhisperCpp, Piper_tables)
    QueueOutbound_ChatOnly()   # NOT emergency
  END
  IF WifiOrBtDrop THEN
    FallToUsbIfPresent()
    EnterLocalOnlyMode()
    StatusOn(Braille, Captions)
  END
  IF HighLatency THEN
    PreferLocal(Captions, Braille)
    DeferSignSync()
    Mark("delayed")
  END
END
# EXCEPTION: EmergencyOverlay uses cellular/satellite — never queued here

# ============================================================
# SECOND-ORDER FAILURES (fallback depends on failed node)
# ============================================================

PROCEDURE SecondOrder_Guards():
  # Text down → all modalities starve
  Ensure DualSourceText = EdgeLastGoodBuffer + OfflinePhraseROM

  # Shared USB hub
  Ensure SplitPowerData(Braille_dedicated_USB, Captions_on_BT_or_WiFi)

  # Caption UI same process as sign controller
  Ensure SeparateCaptionDaemon()

  # Wrong compensatory exit
  Ensure ProfileGate:
    IF DEAF THEN never choose audio alone
    IF BLIND THEN never rely on captions alone
    IF DEAFBLIND THEN Braille + tactile hand only

  # Offline must not use cloud STT for Braille
  Ensure LocalSttOnly_WhenNetDown()

  # Fingerspell must not need live core
  Ensure EdgeCachedLastSentence + ROM_alphabet
END

# ============================================================
# MAIN CONTROL LOOP (compact)
# ============================================================

PROCEDURE Main():
  LoadRoster_FailClosed()
  InitMiniBrains(Braille, SignHand, CaptionDaemon, SosNode)  # each + 20–30 tube
  SecondOrder_Guards()

  LOOP
    IF EmergencyTriggerPending() THEN
      EmergencyOverlay(trigger, hint, WorkingModality())
      CONTINUE
    END

    IF NetworkFailed() THEN Network_Watch()

    msg ← NextUserOrSystemMessage()
    TextPipeline_Run(msg)

    FOR EACH brain IN CriticalNodes
      IF NodeDying(brain) THEN OnNodeDying(brain)
    END
  END
END

# ============================================================
# HIGHEST-RISK PATH (documentation as guard comment)
# ============================================================
# Worst case: main AI/bus already dead AND every per-node RF path
# fails OR every tube pack depleted/unprovisioned OR cold-modem
# burns the only shot before SMS.
# Harden pattern: mini-brain + tube one-shot on EVERY critical node;
# pre-register modem; prefer SMS/text-to-911 over long voice;
# actuators off dying budget.

# END OF PSEUDOCODE