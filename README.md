# Neural Speed Academy

A desktop app for speed reading and cognitive training built with Python and Tkinter.

## Features

- **Flash Perception** - Rapid number and word recognition training
- **Eye-Span Training** - Horizontal, vertical, and mixed peripheral vision exercises
- **Schulte Grid** - 5x5 number grid for focus and peripheral awareness
- **Eye Priming** - Warm-up exercises for eye muscles
- **Pacer Reading** - Guided reading with configurable WPM (200-1000)
- **Progress Tracking** - XP system, streaks, and session history

## Requirements

- Python 3.10+
- Tkinter (included with Python on most systems)

## Running the Application

```bash
python3 nsa.py
```

## Project Structure

```
NeuralSpeedAcademy/
├── nsa.py                          # Application entry point
└── neural_speed_academy/           # Main package
    ├── theme.py                    # Colors and fonts
    ├── config.py                   # Exercise configurations
    ├── state.py                    # Data classes (UserProfile, HistoryEntry, etc.)
    ├── repositories/               # Data persistence layer
    │   ├── base.py                 # Repository interface
    │   └── user_repository.py      # JSON file implementation
    ├── navigation/                 # Screen routing
    │   └── navigator.py            # Centralized navigation controller
    ├── screens/                    # UI screens
    │   ├── base.py                 # BaseScreen with lifecycle methods
    │   ├── login_screen.py         # User login
    │   ├── dashboard_screen.py     # Main menu
    │   ├── stats_screen.py         # Performance analytics
    │   └── menu_screens.py         # Exercise selection menus
    └── exercises/                  # Training exercises
        ├── base.py                 # BaseExercise with common functionality
        ├── flash.py                # Flash perception (numbers, words, eye-span)
        ├── schulte.py              # Schulte grid
        ├── priming.py              # Eye priming
        └── pacer.py                # Pacer reading
```

## Architecture

### Design Patterns

| Pattern | Usage |
|---------|-------|
| **Repository** | `UserRepositoryInterface` abstracts data storage, allowing easy swap between JSON, SQLite, or cloud backends |
| **Navigator** | Centralized screen routing decouples screens from each other |
| **Template Method** | `BaseScreen` and `BaseExercise` define lifecycle hooks (`build()`, `start()`, `complete()`) |
| **Strategy** | Exercises are interchangeable; new ones can be added by subclassing `BaseExercise` |
| **Factory** | Screen registration uses factory lambdas for lazy instantiation |

### Key Components

**Navigator** (`navigation/navigator.py`)
- Manages screen transitions
- Holds current user reference
- Screens navigate via `navigator.to_dashboard()`, `navigator.navigate_to("stats")`, etc.

**BaseScreen** (`screens/base.py`)
- Abstract base for all screens
- Provides `show()`, `hide()`, `clear()` lifecycle
- Includes `add_nav_bar()` and `show_guide()` helpers

**BaseExercise** (`exercises/base.py`)
- Abstract base for all exercises
- Handles XP awards and history logging via `complete()`
- Provides error handling via `handle_error()`

**UserRepository** (`repositories/user_repository.py`)
- Persists user profiles to JSON
- Atomic writes prevent data corruption
- Auto-backup of corrupted files

### Data Flow

```
User Action
    ↓
Screen/Exercise
    ↓
Navigator (routing + user state)
    ↓
UserRepository (persistence)
    ↓
JSON File (neural_profile.json)
```

## Adding a New Exercise

1. Create a new file in `exercises/`:

```python
from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult

class MyExercise(BaseExercise):
    @property
    def name(self) -> str:
        return "My Exercise"

    def start(self, **config) -> None:
        self.clear()
        self.add_nav_bar()
        # Build your exercise UI here

    def _complete_exercise(self) -> None:
        result = ExerciseResult(
            exercise_name=self.name,
            score=self.score,
            total=self.total,
            xp_gained=self.score * 10
        )
        self.complete(result)
        self.navigator.to_dashboard()
```

2. Register in `nsa.py`:

```python
from neural_speed_academy.exercises.my_exercise import MyExercise

# In __init__:
self.my_exercise = MyExercise(self.root, self.navigator)

# In _register_screens, add to exercise_callbacks:
"start_my_exercise": self.my_exercise.start,
```

3. Add a button in `DashboardScreen`.

## Adding a New Screen

1. Create a new file in `screens/`:

```python
from neural_speed_academy.screens.base import BaseScreen

class MyScreen(BaseScreen):
    def build(self, **kwargs) -> None:
        self.add_nav_bar()
        # Build your screen UI here
```

2. Register in `nsa.py`:

```python
from neural_speed_academy.screens.my_screen import MyScreen

# In _register_screens:
self.navigator.register_screen(
    "my_screen",
    lambda: MyScreen(self.root, self.navigator)
)
```

3. Navigate to it: `self.navigator.navigate_to("my_screen")`

## Configuration

Exercise parameters are centralized in `config.py`:

- `WORD_PAIRS` - Word pairs for ambiguous word exercises
- `EXERCISE_GUIDES` - Help text for each exercise type
- `PACER_CONFIG` - WPM range and defaults
- `SCHULTE_CONFIG` - Grid size and scoring
- `PRIMING_CONFIG` - Positions and timing
- `USER_DATA_CONFIG` - File name, history limits, XP per correct

## User Data

User profiles are stored in `neural_profile.json`:

```json
{
  "username": {
    "name": "username",
    "xp": 150,
    "streak": 3,
    "last_login": "2024-01-15",
    "history": [
      {"timestamp": "2024-01-15 10:30", "exercise": "FLASH_NUM", "result": "8/10"}
    ]
  }
}
```

## Error Handling

The application includes error recovery:

- **Corrupted data files** are backed up to `.corrupted` and a fresh start is made
- **Save failures** show user-friendly error messages
- **Exercise errors** are caught and logged, returning user to dashboard

## License

MIT
