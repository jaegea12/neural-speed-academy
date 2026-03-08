"""
Navigator for centralized screen routing.
Decouples screens from each other by providing a single point of navigation.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable
import tkinter as tk

if TYPE_CHECKING:
    from neural_speed_academy.screens.base import BaseScreen
    from neural_speed_academy.state import UserProfile
    from neural_speed_academy.repositories.base import UserRepositoryInterface


class Navigator:
    """
    Manages screen transitions and maintains navigation state.
    Screens request navigation through this class instead of calling each other directly.
    """

    # Human-readable labels for screen names
    SCREEN_LABELS = {
        "main_menu": "Menu",
        "login": "Login",
        "dashboard": "HUB",
        "flash_menu": "Flash Numbers",
        "words_menu": "Word Drills",
        "eyespan_menu": "Eye-Span",
        "priming_menu": "Eye Priming",
        "stats": "Stats",
        "settings": "Settings",
        "introduction": "Introduction",
        "paths": "Training Paths",
        "path_session": "Path Session",
    }

    def __init__(
        self,
        root: tk.Tk,
        user_repo: "UserRepositoryInterface",
    ):
        self.root = root
        self.user_repo = user_repo
        self.current_user: Optional["UserProfile"] = None
        self.current_screen: Optional["BaseScreen"] = None
        self._screen_registry: dict[str, Callable[[], "BaseScreen"]] = {}
        self._history: list[str] = []
        self._current_name: str = ""
        self._app = None  # Set by NeuralSpeedAcademy after init
        self._path_step_pending: tuple[str, int] | None = None

    def register_screen(self, name: str, factory: Callable[[], "BaseScreen"]) -> None:
        """Register a screen factory by name."""
        self._screen_registry[name] = factory

    def navigate_to(self, screen_name: str, **kwargs) -> None:
        """Navigate to a registered screen by name."""
        if screen_name not in self._screen_registry:
            raise ValueError(f"Unknown screen: {screen_name}")

        # Track history (dashboard and main_menu reset the stack)
        if screen_name in ("dashboard", "main_menu"):
            self._history = []
        elif self._current_name and self._current_name != "login":
            self._history.append(self._current_name)
        self._current_name = screen_name

        screen = self._screen_registry[screen_name]()
        self._show_screen(screen, **kwargs)

    def _show_screen(self, screen: "BaseScreen", **kwargs) -> None:
        """Display a screen, hiding the current one first."""
        if self.current_screen:
            self.current_screen.hide()
        self.current_screen = screen
        screen.show(**kwargs)

    def set_user(self, user: "UserProfile") -> None:
        """Set the current logged-in user."""
        self.current_user = user

    def get_user(self) -> Optional["UserProfile"]:
        """Get the current logged-in user."""
        return self.current_user

    def save_user(self) -> None:
        """Save the current user to the repository."""
        if self.current_user:
            self.user_repo.save(self.current_user)

    def logout(self) -> None:
        """Clear the current user and navigate to main menu."""
        self.current_user = None
        self.navigate_to("main_menu")

    def to_login(self) -> None:
        """Navigate to login screen."""
        self.navigate_to("login")

    def to_dashboard(self) -> None:
        """Navigate to dashboard/main menu."""
        self.navigate_to("dashboard")

    def finish_exercise(self) -> None:
        """Navigate after an exercise ends.

        If the exercise was launched from a training path, advance the
        path step and return to the path session screen.  Otherwise
        fall back to the dashboard.
        """
        pending = self._path_step_pending
        if pending:
            path_id, step_idx = pending
            self._path_step_pending = None
            user = self.current_user
            if user:
                pp = user.path_progress.get(path_id)
                if pp and pp.current_step == step_idx:
                    pp.current_step += 1
                    from neural_speed_academy.config import TRAINING_PATHS
                    path_data = TRAINING_PATHS.get(path_id, {})
                    if pp.current_step >= len(path_data.get("steps", [])):
                        pp.completed = True
                        user.active_path = None
                    self.user_repo.save(user)
            self.navigate_to("path_session")
        else:
            self.to_dashboard()

    def to_stats(self) -> None:
        """Navigate to stats screen."""
        self.navigate_to("stats")

    def to_exercise(self, exercise_type: str, **config) -> None:
        """Navigate to an exercise screen with configuration."""
        self.navigate_to(exercise_type, **config)

    def get_breadcrumbs(self) -> list[tuple[str, str]]:
        """Return list of (label, screen_name) pairs for the current path."""
        crumbs = [("HUB", "dashboard")]
        for name in self._history:
            label = self.SCREEN_LABELS.get(name, name)
            crumbs.append((label, name))
        if self._current_name and self._current_name != "dashboard":
            label = self.SCREEN_LABELS.get(self._current_name, self._current_name)
            crumbs.append((label, self._current_name))
        return crumbs

    def go_back(self) -> None:
        """Navigate to the previous screen in history."""
        if self._history:
            target = self._history[-1]
            # Pop so navigate_to doesn't re-push
            self._history.pop()
            self._current_name = ""
            self.navigate_to(target)
        elif self._current_name == "dashboard":
            self.navigate_to("main_menu")
        elif self.current_user:
            self.to_dashboard()
        else:
            self.navigate_to("main_menu")
