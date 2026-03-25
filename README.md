# Neural Speed Academy

A desktop application for speed reading and cognitive training built with Python and PyQt6.

## Features

- **Flash Perception** — rapid number, word, and eye-span recognition training with configurable difficulty
- **Pacer Reading** — guided reading with highlight modes (single-line, multi-line, Z-pattern), adjustable WPM, chunk size, and comprehension quiz
- **RSVP** — rapid serial visual presentation for speed reading
- **Chunking** — text chunking exercises to increase reading span
- **Schulte Grid** — numbered grid exercises for peripheral vision training with configurable grid size (3x3 to 7x7) and cell size
- **Eye Priming** — saccade and smooth pursuit exercises (horizontal, vertical, diagonal, expanding, circular, figure-8)
- **Training Paths** — structured multi-exercise sessions with progress tracking

### Additional features

- 7 color themes (Dark, Twilight, Silver, Soft Light, Focus, Light, High Contrast) — all WCAG AA compliant
- Field of View presets affecting pacer page width and font sizing
- Responsive layout scaling to any screen size (reference: 1920x1080)
- Fullscreen and windowed mode (F11 to toggle)
- User profiles with optional password protection
- Per-exercise progress charts and session history
- CSV/JSON export of training data

## Requirements

- Python >= 3.10
- PyQt6 >= 6.5

## Setup

```bash
# Clone the repository
git clone https://code.roche.com/jaegea12/neural-speed-academy.git
cd neural-speed-academy

# Install dependencies
pip install -e .
# or just: pip install PyQt6>=6.5

# Run
python nsa.py
```

## Project structure

```
nsa.py                              # Entry point
neural_speed_academy/
  config.py                         # Exercise configs, guides, constants
  theme.py                          # Color themes, fonts, screen metrics
  state.py                          # User profile and history data models
  navigation/
    navigator.py                    # Screen routing (QStackedWidget)
  repositories/
    user_repository.py              # User data persistence (JSON)
  exercises/
    base.py                         # BaseExercise with nav bar, results, guides
    flash.py                        # Flash numbers, words, eye-span
    pacer.py                        # Guided reading with highlight overlay
    rsvp.py                         # Rapid serial visual presentation
    chunking.py                     # Text chunking
    schulte.py                      # Schulte grid
    priming.py                      # Eye movement exercises
  screens/
    base.py                         # BaseScreen, shared guide dialog
    main_menu_screen.py             # Main menu with login-aware buttons
    login_screen.py                 # Profile selection and creation
    dashboard_screen.py             # Training hub with exercise categories
    menu_screens.py                 # Exercise selection menus
    settings_screen.py              # Theme, FOV, display mode, training text
    stats_screen.py                 # Progress charts and session history
    paths_screen.py                 # Training path selection
    path_session_screen.py          # Training path builder
    introduction_screen.py          # App introduction
```

## Contributing

Contributions, feedback, and ideas are welcome. Feel free to open an issue or submit a merge request. If you have suggestions for new exercises or improvements to existing ones, start a discussion via an issue.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

## Credits

Created by Adam Jaeger

Repository setup and GitLab integration by Orlando Pereira
