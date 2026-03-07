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

    def register_screen(self, name: str, factory: Callable[[], "BaseScreen"]) -> None:
        """Register a screen factory by name."""
        self._screen_registry[name] = factory

    def navigate_to(self, screen_name: str, **kwargs) -> None:
        """Navigate to a registered screen by name."""
        if screen_name not in self._screen_registry:
            raise ValueError(f"Unknown screen: {screen_name}")
        
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
        """Clear the current user and navigate to login."""
        self.current_user = None
        self.navigate_to("login")

    def to_login(self) -> None:
        """Navigate to login screen."""
        self.navigate_to("login")

    def to_dashboard(self) -> None:
        """Navigate to dashboard/main menu."""
        self.navigate_to("dashboard")

    def to_stats(self) -> None:
        """Navigate to stats screen."""
        self.navigate_to("stats")

    def to_exercise(self, exercise_type: str, **config) -> None:
        """Navigate to an exercise screen with configuration."""
        self.navigate_to(exercise_type, **config)
