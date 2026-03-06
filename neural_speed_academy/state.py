"""
State containers for Neural Speed Academy.
Uses dataclasses for type safety and clarity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HistoryEntry:
    """A single exercise session record."""
    timestamp: str
    exercise: str
    result: str

    @classmethod
    def create(cls, exercise: str, result: str) -> "HistoryEntry":
        """Create a new history entry with current timestamp."""
        return cls(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            exercise=exercise,
            result=result,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "exercise": self.exercise,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            timestamp=data.get("timestamp", ""),
            exercise=data.get("exercise", ""),
            result=data.get("result", ""),
        )


@dataclass
class UserProfile:
    """User profile with XP, streak, and exercise history."""
    name: str
    xp: int = 0
    streak: int = 1
    last_login: str = ""
    history: list[HistoryEntry] = field(default_factory=list)

    def __post_init__(self):
        if not self.last_login:
            self.last_login = datetime.now().strftime("%Y-%m-%d")

    def add_xp(self, amount: int) -> None:
        """Add XP to the user profile."""
        self.xp += amount

    def add_history(self, exercise: str, result: str, max_entries: int = 50) -> None:
        """Add a history entry, keeping only the most recent entries."""
        entry = HistoryEntry.create(exercise, result)
        self.history.insert(0, entry)
        self.history = self.history[:max_entries]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "xp": self.xp,
            "streak": self.streak,
            "last_login": self.last_login,
            "history": [h.to_dict() for h in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create from dictionary (JSON deserialization)."""
        history = []
        for item in data.get("history", []):
            if isinstance(item, dict):
                history.append(HistoryEntry.from_dict(item))
            elif isinstance(item, str):
                # Handle legacy string format
                parts = item.split(" | ")
                if len(parts) >= 3:
                    result = parts[2].replace("Score: ", "")
                    history.append(HistoryEntry(
                        timestamp=parts[0],
                        exercise=parts[1],
                        result=result,
                    ))
        return cls(
            name=data.get("name", ""),
            xp=data.get("xp", 0),
            streak=data.get("streak", 1),
            last_login=data.get("last_login", ""),
            history=history,
        )


@dataclass
class ExerciseState:
    """State for an active exercise session."""
    mode: str
    current_round: int = 0
    total_rounds: int = 0
    correct_count: int = 0
    target_value: str = ""
    config: dict = field(default_factory=dict)

    def next_round(self) -> bool:
        """Advance to next round. Returns True if more rounds remain."""
        self.current_round += 1
        return self.current_round <= self.total_rounds

    def record_correct(self) -> None:
        """Record a correct answer."""
        self.correct_count += 1

    def is_complete(self) -> bool:
        """Check if all rounds are complete."""
        return self.current_round >= self.total_rounds

    def get_score_string(self) -> str:
        """Get formatted score string."""
        return f"{self.correct_count}/{self.total_rounds}"


@dataclass
class SpanConfig:
    """Configuration for eye-span exercises."""
    mode: str  # "h" (horizontal), "v" (vertical), "m" (mixed)
    width: int  # Width percentage (30-90)


@dataclass
class AppState:
    """Global application state."""
    user: Optional[UserProfile] = None
    current_screen: str = "login"
    exercise: Optional[ExerciseState] = None

    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self.user is not None

    def login(self, user: UserProfile) -> None:
        """Set the current user."""
        self.user = user
        self.current_screen = "dashboard"

    def logout(self) -> None:
        """Clear the current user."""
        self.user = None
        self.current_screen = "login"
        self.exercise = None
