# Neural Speed Academy

A desktop application for speed reading and cognitive training, built with Python and PyQt6.

15 exercises across three categories — Perception, Cognition, and Reading — with structured training paths, per-user profiles, and data export for research use.

## Exercises

### Perception
| Exercise | Description |
|---|---|
| **Flash Numbers** | Rapid digit recognition with configurable digit count, range modes, and round count |
| **Word Drills** | Timed word recognition with length and round settings |
| **Eye-Span** | Peripheral digit recognition in horizontal, vertical, or mixed directions with adjustable width |
| **Schulte Grid** | Numbered grid exercises (3×3 to 7×7) with configurable cell size for peripheral vision training |
| **Peripheral Flash** | Directional flash detection in peripheral vision |

### Cognition
| Exercise | Description |
|---|---|
| **Sequence Memory** | Reproduce increasingly long sequences of numbers, words, or mixed items |
| **Rapid Decision** | Rule-based grid decisions under time pressure |
| **Object Tracking (MOT)** | Track moving targets among distractors at configurable speed and count |
| **Split Attention** | Dual-task training — center word + peripheral shape in sequential, simultaneous, and rapid modes |
| **Reaction Time** | Simple, choice, and go/no-go reaction drills |

### Reading
| Exercise | Description |
|---|---|
| **Pacer & Quiz** | Guided reading with highlight modes (line, multi-line, Z-pattern), adjustable WPM, and comprehension quiz |
| **RSVP Reader** | Rapid serial visual presentation for speed reading |
| **Chunking** | Text chunking exercises to increase reading span |
| **Spaced Repetition** | SM-2 algorithm flashcard review with custom decks |
| **Slide Processing** | Absorb text slides with facts, then answer comprehension questions. Built-in and custom slide sets |

### Visual Warmup
- **Eye Priming** — saccade and smooth pursuit exercises (horizontal, vertical, diagonal, expanding, circular, figure-8)

## Training Paths

16 built-in training paths with progress tracking, plus a path builder for creating custom sequences. Paths combine multiple exercises into structured sessions with configurable difficulty.

## Slide Creator

In-app editor for creating custom slide sets with title, bullet points, and multiple-choice questions per slide. Import and export slide sets as `.json` files for sharing.

## Features

- **9 color profiles** — Dark, Light, High Contrast, Warm/Focus, Twilight, Soft Light, Silver, Monochrome, Ember. All WCAG AA compliant
- **Font scaling** — 6 steps from 80% to 150%, per-user preference
- **Per-user profiles** — individual theme, font scale, progress, and history. Optional password protection
- **Unified config menus** — two-panel layout with preset/difficulty toggles and adjustable parameters
- **Progress tracking** — per-exercise charts, session history, personal bests, XP system
- **Data export** — CSV (Excel-compatible) and JSON with full exercise metadata. Anonymization option for research use
- **Keyboard navigation** — Ctrl+Enter to start, number keys for answers, F11 fullscreen toggle
- **Responsive layout** — scales to any screen size (reference: 1920×1080)
- **Accessibility** — focus indicators on all interactive elements, accessible names, WCAG AA contrast

## Requirements

- Python ≥ 3.10
- PyQt6 ≥ 6.5

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/neural-speed-academy.git
cd neural-speed-academy
pip install PyQt6>=6.5
python nsa.py
```

## Project Structure

```
nsa.py                                  # Entry point
assets/
  icon.png                              # App icon (512×512)
  icon.ico                              # Windows icon (multi-resolution)
neural_speed_academy/
  __init__.py                           # Version
  config.py                             # Exercise configs, guides, slide/text libraries
  theme.py                              # Color profiles, fonts, screen metrics
  state.py                              # User profile and history data models
  navigation/
    navigator.py                        # Screen routing (QStackedWidget)
  repositories/
    user_repository.py                  # User data persistence (JSON)
    slide_repository.py                 # Custom slide set storage
  exercises/
    base.py                             # BaseExercise — nav bar, results, guides
    flash.py                            # Flash numbers, words, eye-span
    pacer.py                            # Guided reading with highlight overlay
    rsvp.py                             # Rapid serial visual presentation
    chunking.py                         # Text chunking
    schulte.py                          # Schulte grid
    priming.py                          # Eye movement exercises
    sequence_memory.py                  # Sequence memory
    recall.py                           # Recall training
    peripheral_flash.py                 # Peripheral flash detection
    rapid_decision.py                   # Rapid decision grid
    mot.py                              # Multiple object tracking
    split_attention.py                  # Split attention dual-task
    reaction_time.py                    # Reaction time drills
    slide_processing.py                 # Slide processing with comprehension
    spaced_repetition.py                # SM-2 spaced repetition
  screens/
    base.py                             # BaseScreen, guide dialog, scroll helper
    main_menu_screen.py                 # Main menu with app icon and login
    login_screen.py                     # Profile selection and creation
    dashboard_screen.py                 # Training hub — 3-column exercise grid
    menu_screens.py                     # Two-panel config menus for all exercises
    settings_screen.py                  # Theme, font scale, FOV, display mode
    stats_screen.py                     # Progress charts, history, data export
    paths_screen.py                     # Training path selection
    path_session_screen.py              # Path session runner and path builder
    introduction_screen.py              # App introduction and limitations
    slide_creator_screen.py             # Custom slide set editor
```

## Data Files

Created at runtime in the working directory (not committed):

| File/Directory | Purpose |
|---|---|
| `neural_profile.json` | User profiles, history, personal bests |
| `nsa_settings.json` | App settings (theme, FOV, font scale) |
| `nsa_slide_sets/` | Custom slide sets (one `.json` per set) |

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

## Credits

Created by Adam Jaeger — admjae@proton.me

Repository setup and GitLab integration by Orlando Pereira
