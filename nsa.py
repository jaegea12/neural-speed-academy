from __future__ import annotations

import tkinter as tk
from typing import Optional

from neural_speed_academy.theme import COLORS, theme_manager
from neural_speed_academy.state import UserProfile
from neural_speed_academy.repositories.user_repository import JsonUserRepository
from neural_speed_academy.navigation.navigator import Navigator
from neural_speed_academy.screens.main_menu_screen import MainMenuScreen
from neural_speed_academy.screens.introduction_screen import IntroductionScreen
from neural_speed_academy.screens.login_screen import LoginScreen
from neural_speed_academy.screens.dashboard_screen import DashboardScreen
from neural_speed_academy.screens.stats_screen import StatsScreen
from neural_speed_academy.screens.menu_screens import (
    FlashMenuScreen,
    WordsMenuScreen,
    EyespanMenuScreen,
    PrimingMenuScreen,
)
from neural_speed_academy.screens.settings_screen import SettingsScreen
from neural_speed_academy.screens.paths_screen import PathSelectionScreen, PathSessionScreen, PathBuilderScreen
from neural_speed_academy.exercises.flash import FlashExercise
from neural_speed_academy.exercises.schulte import SchulteExercise
from neural_speed_academy.exercises.priming import PrimingExercise
from neural_speed_academy.exercises.pacer import PacerExercise
from neural_speed_academy.exercises.rsvp import RsvpExercise
from neural_speed_academy.exercises.chunking import ChunkingExercise


class SpeedReadingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Speed Academy")
        try:
            self.root.state('zoomed')
        except Exception:
            self.root.geometry("1280x800")
        self.root.configure(bg=COLORS["bg"])

        # Load persisted app settings (theme, etc.)
        theme_manager.load()

        # Repository for user data persistence
        self.user_repo = JsonUserRepository()

        # Navigator for screen management
        self.navigator = Navigator(self.root, self.user_repo)
        self.navigator._app = self

        # Exercise instances
        self.flash_exercise = FlashExercise(self.root, self.navigator)
        self.schulte_exercise = SchulteExercise(self.root, self.navigator)
        self.priming_exercise = PrimingExercise(self.root, self.navigator)
        self.pacer_exercise = PacerExercise(self.root, self.navigator)
        self.rsvp_exercise = RsvpExercise(self.root, self.navigator)
        self.chunking_exercise = ChunkingExercise(self.root, self.navigator)

        self._register_screens()

        # Start with main menu
        self.navigator.navigate_to("main_menu")

    def _register_screens(self) -> None:
        """Register all screens with the navigator."""
        # Exercise callbacks for dashboard
        exercise_callbacks = {
            "menu_flash": lambda: self.navigator.navigate_to("flash_menu"),
            "menu_words": lambda: self.navigator.navigate_to("words_menu"),
            "menu_priming": lambda: self.navigator.navigate_to("priming_menu"),
            "menu_eyespan": lambda: self.navigator.navigate_to("eyespan_menu"),
            "start_schulte": self.schulte_exercise.start,
            "setup_pacer": self.pacer_exercise.start,
            "setup_rsvp": self.rsvp_exercise.start,
            "setup_chunking": self.chunking_exercise.start,
            "show_stats": lambda: self.navigator.navigate_to("stats"),
            "show_paths": lambda: self.navigator.navigate_to("paths"),
        }

        self.navigator.register_screen(
            "main_menu",
            lambda: MainMenuScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "introduction",
            lambda: IntroductionScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "login",
            lambda: LoginScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "dashboard",
            lambda: DashboardScreen(self.root, self.navigator, exercise_callbacks)
        )
        self.navigator.register_screen(
            "stats",
            lambda: StatsScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "flash_menu",
            lambda: FlashMenuScreen(self.root, self.navigator, self.flash_exercise)
        )
        self.navigator.register_screen(
            "words_menu",
            lambda: WordsMenuScreen(self.root, self.navigator, self.flash_exercise)
        )
        self.navigator.register_screen(
            "eyespan_menu",
            lambda: EyespanMenuScreen(self.root, self.navigator, self.flash_exercise)
        )
        self.navigator.register_screen(
            "priming_menu",
            lambda: PrimingMenuScreen(self.root, self.navigator, self.priming_exercise)
        )
        self.navigator.register_screen(
            "settings",
            lambda: SettingsScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "paths",
            lambda: PathSelectionScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "path_session",
            lambda: PathSessionScreen(self.root, self.navigator)
        )
        self.navigator.register_screen(
            "path_builder",
            lambda: PathBuilderScreen(self.root, self.navigator)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReadingApp(root)
    root.mainloop()
