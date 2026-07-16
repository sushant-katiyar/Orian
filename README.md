# Project Orion

**An Android automation AI agent built from scratch in Python** — combining low-level device control, computer vision, OCR, and LLM reasoning into a single perceive-decide-act loop.

Built by Sushant (B.Tech AIML) as a milestone-based personal project. Each milestone adds one distinct capability layer on top of the last, and every design decision is reasoned through deliberately before a single line of code is written.

---

## What Orion Does (Vision)

Orion looks at an Android phone screen the way a human would — takes a screenshot, reads the text and icons on it — then hands that understanding to an LLM "brain" that decides the next single action (tap something, type something, swipe, open an app, or declare the task done/stuck). That action gets executed back on the real device through ADB. Repeat, one step at a time, until the task is complete.

No scripted macros, no fixed coordinates — the agent perceives the actual current screen state every cycle and reasons about what to do next.

---

## Architecture

```
AndroidPhone  →  ScreenCapture  →  Vision (OCR + Templates)
                                        │
                                        ▼
                                  Bridge Function
                                (merges + disambiguates
                                 into one coordinate dict)
                                        │
                                        ▼
                                     Brain (LLM)
                                  (sees labels only,
                                   returns one JSON action)
                                        │
                                        ▼
                                   Executor
                                (looks up coordinates,
                                 calls AndroidPhone)
                                        │
                                        ▼
                                  AndroidPhone
                              (executes on real device)
```

The golden rule holding this together: **the LLM never sees raw coordinates.** It only ever sees plain text labels (`dict.keys()`). The bridge function's dictionary is the single source of truth for where things actually are on screen — the executor is the only thing that looks coordinates up.

---

## Milestones

| # | Codename | Capability | Status |
|---|----------|-------------|--------|
| 1 | **The Hand** | ADB-based device control | ✅ Complete |
| 2 | **The Eye** | Screen capture + template-matching vision | ✅ Complete |
| 3 | **Vision 2.0** | OCR text recognition on screen | ✅ Complete |
| 4 | **The Brain** | LLM reasoning loop + action execution | 🔄 In progress (fully designed, bridge function next) |

### Milestone 1 — The Hand
Core device control layer.
- `AndroidPhone` class wraps ADB commands via a central `run_adb()` method.
- Custom `DeviceNotConnectedError` for clear, fail-fast error signaling.
- `_NO_CONNECTION_NEEDED` — an exempt set of commands (e.g. commands that don't require a live device connection) that prevents infinite recursion in the connection-validation logic.

### Milestone 2 — The Eye
Screen perception layer.
- `ScreenCapture`: grabs raw screenshot bytes memory-efficiently via ADB's `exec-out`, converts to a NumPy array (`np.frombuffer`), then decodes to an image with `cv2.imdecode`.
- `Vision`: template matching using `cv2.matchTemplate` (`TM_CCOEFF_NORMED`), returning center coordinates of matches. Supports a `raise_if_missing` flag for strict vs. optional matching.
- Vision is fully decoupled from image source — it takes image data in, it never captures screenshots itself.

### Milestone 3 — Vision 2.0
Text recognition layer added on top of Vision.
- OCR via `pytesseract` / Tesseract.
- **Cascade preprocessing strategy:** try raw image → standard adaptive threshold → inverted adaptive threshold, stopping at the first pass whose result confidence clears `min_confidence=60`.
- Uniform output shape: a list of dicts, each with `text`, `confidence`, `left`, `top`, `width`, `height`, `center_x`, `center_y`.
- `find_text_on_screen()`: case-insensitive substring search across OCR results, with confidence used as a tie-breaker.

### Milestone 4 — The Brain (in progress)
Full reasoning loop tying everything together.

**Vision update (done):** extracted a private `_match_template()` helper containing the core OpenCV math (`matchTemplate` + `minMaxLoc`), shared between the existing `find_on_screen()` (unchanged behavior) and a new `scan_all_templates(screenshot, template_dir, threshold)` method, which scans an entire folder of template images and returns results in the **same shape as OCR output** (using each filename, minus extension, as `"text"`). This lets the upcoming bridge function merge OCR + template detections in one uniform loop.

**Designed, not yet coded:**
- Bridge function (merges OCR + template results → one disambiguated label → coordinate dict)
- `Brain` (LLM call, JSON in/out, fixed system prompt + sliding message history)
- Executor (validates JSON, looks up coordinates, calls `AndroidPhone`)
- Stuck/complete handling with a pause-countdown UX

Full design details are in `PROJECT_ORION_NOTES.md`.

---

## Tech Stack

- **Python**
- **ADB** (Android Debug Bridge) — device control
- **OpenCV** (`cv2`) — template matching, image decoding
- **pytesseract / Tesseract** — OCR
- **NumPy** — image buffer handling
- **subprocess** — ADB process calls
- **LLM API** (provider TBD) — the "Brain" in Milestone 4

---

## Project Philosophy

- **Separation of concerns above all else.** Capture, preprocessing, matching, and text search are always distinct responsibilities that don't leak into each other.
- **Decoupling from data source.** Vision takes images in as data — it has no idea (and doesn't care) where they came from.
- **Fail fast and loudly.** No silent fallbacks, no lenient guessing on bad input — errors surface immediately and clearly.
- **Single source of truth.** Anything with more than one potential owner (like coordinates) gets exactly one place it's allowed to live.

---

## Repo Structure

```
project-orion/
├── android_phone.py      # Milestone 1 — AndroidPhone, DeviceNotConnectedError
├── screen_capture.py      # Milestone 2 — ScreenCapture
├── vision.py              # Milestones 3 — Vision (template match + OCR + scan_all_templates)
├── bridge.py               # Milestone 4 — merges Vision output → coordinate dict (upcoming)
├── brain.py                # Milestone 4 — LLM call + prompt/history management (upcoming)
├── executor.py             # Milestone 4 — validates JSON action, executes it (upcoming)
├── templates/               # Template images used for scan_all_templates / find_on_screen
└── README.md
```

## License
MIT
