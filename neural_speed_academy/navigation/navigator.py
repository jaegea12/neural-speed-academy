"""
Navigator for centralized screen routing using QStackedWidget.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from PyQt6.QtWidgets import QStackedWidget

if TYPE_CHECKING:
    from neural_speed_academy.screens.base import BaseScreen
    from neural_speed_academy.state import UserProfile
    from neural_speed_academy.repositories.base import UserRepositoryInterface


class Navigator:
    """Manages screen transitions via a QStackedWidget."""

    SCREEN_LABELS = {
        "main_menu": "Menu",
        "login": "Login",
        "dashboard": "HUB",
        "flash_menu": "Flash Numbers",
        "words_menu": "Word Drills",
        "eyespan_menu": "Eye-Span",
        "priming_menu": "Eye Priming",
        "sequence_memory_menu": "Sequence Memory",
        "peripheral_flash_menu": "Peripheral Flash",
        "rapid_decision_menu": "Rapid Decision",
        "mot_menu": "Object Tracking",
        "split_attention_menu": "Split Attention",
        "reaction_time_menu": "Reaction Time",
        "stats": "Stats",
        "settings": "Settings",
        "introduction": "Introduction",
        "paths": "Training Paths",
        "path_session": "Path Session",
    }

    def __init__(self, stack: QStackedWidget, user_repo: "UserRepositoryInterface"):
        self.stack = stack
        self.user_repo = user_repo
        self.current_user: Optional["UserProfile"] = None
        self._screen_registry: dict[str, Callable[[], "BaseScreen"]] = {}
        self._history: list[str] = []
        self._current_name: str = ""
        self._app = None
        self._path_step_pending: tuple[str, int] | None = None
        self._post_login_redirect: str | None = None

    def register_screen(self, name: str, factory: Callable[[], "BaseScreen"]) -> None:
        self._screen_registry[name] = factory

    def navigate_to(self, screen_name: str, **kwargs) -> None:
        if screen_name not in self._screen_registry:
            raise ValueError(f"Unknown screen: {screen_name}")

        if screen_name in ("dashboard", "main_menu"):
            self._history = []
        elif self._current_name and self._current_name not in ("login", "exercise"):
            self._history.append(self._current_name)
        self._current_name = screen_name

        screen = self._screen_registry[screen_name]()
        self._show_screen(screen, **kwargs)

    def _show_screen(self, screen: "BaseScreen", **kwargs) -> None:
        # Remove old widgets from stack
        while self.stack.count() > 0:
            old = self.stack.widget(0)
            self.stack.removeWidget(old)
            old.deleteLater()

        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)
        screen.show_screen(**kwargs)

    def set_user(self, user: "UserProfile") -> None:
        self.current_user = user

    def get_user(self) -> Optional["UserProfile"]:
        return self.current_user

    def save_user(self) -> None:
        if self.current_user:
            self.user_repo.save(self.current_user)

    def logout(self) -> None:
        self.current_user = None
        self._post_login_redirect = None
        self._path_step_pending = None
        self.navigate_to("main_menu")

    def to_login(self) -> None:
        self.navigate_to("login")

    def to_dashboard(self) -> None:
        self.navigate_to("dashboard")

    def require_login(self, redirect_to: str) -> None:
        self._post_login_redirect = redirect_to
        self.navigate_to("login")

    def complete_login(self) -> None:
        target = self._post_login_redirect
        self._post_login_redirect = None
        if target:
            self.navigate_to(target)
        else:
            self.to_dashboard()

    def finish_exercise(self) -> None:
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
        self.navigate_to("stats")

    def launch_exercise(self, exercise_cls, **kwargs) -> None:
        """Create and show an exercise widget in the stack."""
        if self._current_name:
            self._history.append(self._current_name)
        self._current_name = "exercise"

        while self.stack.count() > 0:
            old = self.stack.widget(0)
            self.stack.removeWidget(old)
            old.deleteLater()

        ex = exercise_cls(self)
        self.stack.addWidget(ex)
        self.stack.setCurrentWidget(ex)
        ex.start(**kwargs)

    def go_back(self) -> None:
        # Skip non-navigable entries (e.g. "exercise") in history
        while self._history and self._history[-1] not in self._screen_registry:
            self._history.pop()

        if self._history:
            target = self._history.pop()
            self._current_name = ""
            self.navigate_to(target)
        elif self._current_name == "dashboard":
            self.navigate_to("main_menu")
        elif self.current_user:
            self.to_dashboard()
        else:
            self.navigate_to("main_menu")
