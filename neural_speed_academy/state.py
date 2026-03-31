"""
State containers for Neural Speed Academy.
Uses dataclasses for type safety and clarity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HistoryEntry:
    """A single exercise session record."""
    timestamp: str
    exercise: str
    result: str
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(cls, exercise: str, result: str,
               metadata: dict | None = None) -> "HistoryEntry":
        """Create a new history entry with current timestamp."""
        return cls(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            exercise=exercise,
            result=result,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = {
            "timestamp": self.timestamp,
            "exercise": self.exercise,
            "result": self.result,
        }
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            timestamp=data.get("timestamp", ""),
            exercise=data.get("exercise", ""),
            result=data.get("result", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PathProgress:
    """Tracks progress through a training path."""
    path_id: str
    current_step: int = 0
    completed: bool = False
    start_xp: int = 0

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "current_step": self.current_step,
            "completed": self.completed,
            "start_xp": self.start_xp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PathProgress":
        return cls(
            path_id=data.get("path_id", ""),
            current_step=data.get("current_step", 0),
            completed=data.get("completed", False),
            start_xp=data.get("start_xp", 0),
        )


@dataclass
class UserProfile:
    """User profile with XP, streak, and exercise history."""
    name: str
    xp: int = 0
    streak: int = 1
    last_login: str = ""
    password_hash: str = ""
    history: list[HistoryEntry] = field(default_factory=list)
    active_path: Optional[str] = None
    path_progress: dict = field(default_factory=dict)
    personal_bests: dict = field(default_factory=dict)
    custom_paths: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.last_login:
            self.last_login = datetime.now().strftime("%Y-%m-%d")

    def update_streak(self) -> None:
        """Update login streak based on last_login date.

        Increments streak if last login was yesterday, resets to 1 if
        more than one day has passed, and leaves it unchanged if
        already logged in today.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_login == today:
            return
        try:
            last = datetime.strptime(self.last_login, "%Y-%m-%d").date()
            diff = (datetime.now().date() - last).days
            if diff == 1:
                self.streak += 1
            elif diff > 1:
                self.streak = 1
        except (ValueError, TypeError):
            self.streak = 1
        self.last_login = today

    def update_personal_best(self, exercise: str, score: int, total: int) -> bool:
        """Update personal best for an exercise if the new score is higher.

        Returns True if a new personal best was set.
        """
        if total == 0:
            return False
        pct = round(score / total * 100, 1)
        prev = self.personal_bests.get(exercise)
        if prev is None or pct > prev.get("pct", 0):
            self.personal_bests[exercise] = {
                "score": score,
                "total": total,
                "pct": pct,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            return True
        return False

    def add_xp(self, amount: int) -> None:
        """Add XP to the user profile."""
        self.xp += amount

    def add_history(self, exercise: str, result: str,
                    max_entries: int = 50,
                    metadata: dict | None = None) -> None:
        """Add a history entry, keeping only the most recent entries."""
        entry = HistoryEntry.create(exercise, result, metadata)
        self.history.insert(0, entry)
        self.history = self.history[:max_entries]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        pp = {}
        for k, v in self.path_progress.items():
            pp[k] = v.to_dict() if isinstance(v, PathProgress) else v
        d = {
            "name": self.name,
            "xp": self.xp,
            "streak": self.streak,
            "last_login": self.last_login,
            "history": [h.to_dict() for h in self.history],
            "active_path": self.active_path,
            "path_progress": pp,
            "personal_bests": self.personal_bests,
            "custom_paths": self.custom_paths,
        }
        if self.password_hash:
            d["password_hash"] = self.password_hash
        return d

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
        pp = {}
        for k, v in data.get("path_progress", {}).items():
            if isinstance(v, dict):
                pp[k] = PathProgress.from_dict(v)
        return cls(
            name=data.get("name", ""),
            xp=data.get("xp", 0),
            streak=data.get("streak", 1),
            last_login=data.get("last_login", ""),
            password_hash=data.get("password_hash", ""),
            history=history,
            active_path=data.get("active_path"),
            path_progress=pp,
            personal_bests=data.get("personal_bests", {}),
            custom_paths=data.get("custom_paths", {}),
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
