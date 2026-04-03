"""
State containers for Neural Speed Academy.
Uses dataclasses for type safety and clarity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
class SRCard:
    """A single spaced repetition card with SM-2 scheduling state."""
    front: str
    back: str
    ease: float = 2.5
    interval: int = 0       # days until next review
    repetitions: int = 0    # consecutive correct recalls
    due_date: str = ""      # YYYY-MM-DD, empty = new card
    last_review: str = ""

    def review(self, quality: int) -> None:
        """Apply SM-2 algorithm. quality: 0=again, 1=hard, 2=good, 3=easy."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.last_review = today

        if quality < 1:
            # Failed — reset
            self.repetitions = 0
            self.interval = 0
            self.due_date = today
            return

        if self.repetitions == 0:
            self.interval = 1
        elif self.repetitions == 1:
            self.interval = 3
        else:
            self.interval = max(1, round(self.interval * self.ease))

        # Adjust ease factor
        ease_delta = {1: -0.15, 2: 0.0, 3: 0.15}
        self.ease = max(1.3, self.ease + ease_delta.get(quality, 0.0))

        # Bonus for easy
        if quality == 3:
            self.interval = round(self.interval * 1.3)

        self.repetitions += 1
        due = datetime.now() + timedelta(days=self.interval)
        self.due_date = due.strftime("%Y-%m-%d")

    def is_due(self) -> bool:
        if not self.due_date:
            return True  # new card
        today = datetime.now().strftime("%Y-%m-%d")
        return self.due_date <= today

    def to_dict(self) -> dict:
        return {
            "front": self.front, "back": self.back,
            "ease": self.ease, "interval": self.interval,
            "repetitions": self.repetitions,
            "due_date": self.due_date, "last_review": self.last_review,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SRCard":
        return cls(
            front=data.get("front", ""),
            back=data.get("back", ""),
            ease=data.get("ease", 2.5),
            interval=data.get("interval", 0),
            repetitions=data.get("repetitions", 0),
            due_date=data.get("due_date", ""),
            last_review=data.get("last_review", ""),
        )


@dataclass
class SRDeck:
    """A deck of spaced repetition cards."""
    name: str
    cards: list[SRCard] = field(default_factory=list)
    builtin: bool = False

    def due_cards(self) -> list[SRCard]:
        return [c for c in self.cards if c.is_due()]

    def new_cards(self) -> list[SRCard]:
        return [c for c in self.cards if not c.due_date]

    def stats(self) -> dict:
        total = len(self.cards)
        due = len(self.due_cards())
        new = len(self.new_cards())
        learned = total - new
        return {"total": total, "due": due, "new": new, "learned": learned}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cards": [c.to_dict() for c in self.cards],
            "builtin": self.builtin,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SRDeck":
        cards = [SRCard.from_dict(c) for c in data.get("cards", [])]
        return cls(
            name=data.get("name", ""),
            cards=cards,
            builtin=data.get("builtin", False),
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
    sr_decks: list = field(default_factory=list)
    theme: str = ""  # empty = use global default
    font_scale: float = 0.0  # 0 = use global default

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

    def update_personal_best(
        self, exercise: str, score: int, total: int,
        metadata: dict | None = None,
    ) -> bool:
        """Update personal best for an exercise if the new score is higher.

        Returns True if a new personal best was set.
        """
        if total == 0:
            return False
        pct = min(round(score / total * 100, 1), 100.0)
        prev = self.personal_bests.get(exercise)
        if prev is None or pct > prev.get("pct", 0):
            entry = {
                "score": score,
                "total": total,
                "pct": pct,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            if metadata:
                entry["metadata"] = metadata
            self.personal_bests[exercise] = entry
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
            "sr_decks": [d.to_dict() for d in self.sr_decks],
        }
        if self.password_hash:
            d["password_hash"] = self.password_hash
        if self.theme:
            d["theme"] = self.theme
        if self.font_scale:
            d["font_scale"] = self.font_scale
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
            sr_decks=[SRDeck.from_dict(d) for d in data.get("sr_decks", [])],
            theme=data.get("theme", ""),
            font_scale=float(data.get("font_scale", 0.0)),
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
