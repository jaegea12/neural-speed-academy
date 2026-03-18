"""
Neural Speed Academy — PyQt6 entry point.
"""
from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.theme import COLORS, theme_manager, screen_metrics
from neural_speed_academy.repositories.user_repository import JsonUserRepository
from neural_speed_academy.navigation.navigator import Navigator

from neural_speed_academy.screens.main_menu_screen import MainMenuScreen
from neural_speed_academy.screens.login_screen import LoginScreen
from neural_speed_academy.screens.settings_screen import SettingsScreen
from neural_speed_academy.screens.dashboard_screen import DashboardScreen
from neural_speed_academy.screens.stats_screen import StatsScreen
from neural_speed_academy.screens.introduction_screen import IntroductionScreen
from neural_speed_academy.screens.menu_screens import (
    FlashMenuScreen, WordsMenuScreen, EyespanMenuScreen, PrimingMenuScreen,
)
from neural_speed_academy.screens.paths_screen import PathSelectionScreen, CustomPathsScreen
from neural_speed_academy.screens.path_session_screen import (
    PathSessionScreen, PathBuilderScreen,
)

from neural_speed_academy.exercises.flash import FlashExercise
from neural_speed_academy.exercises.rsvp import RsvpExercise
from neural_speed_academy.exercises.chunking import ChunkingExercise
from neural_speed_academy.exercises.pacer import PacerExercise
from neural_speed_academy.exercises.schulte import SchulteExercise
from neural_speed_academy.exercises.priming import PrimingExercise


class NeuralSpeedAcademy:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Neural Speed Academy")

        # Load persisted app settings
        theme_manager.load()
        screen_metrics.init_from_screen()

        # Main window
        self.window = QMainWindow()
        self.window.setWindowTitle("Neural Speed Academy")
        self.window.resize(1280, 800)

        # Central stacked widget
        self.stack = QStackedWidget()
        self.window.setCentralWidget(self.stack)

        # Repository
        self.user_repo = JsonUserRepository()

        # Navigator
        self.navigator = Navigator(self.stack, self.user_repo)
        self.navigator._app = self

        # Exercises
        self.flash_exercise = FlashExercise(self.navigator)
        self.rsvp_exercise = RsvpExercise(self.navigator)
        self.chunking_exercise = ChunkingExercise(self.navigator)
        self.pacer_exercise = PacerExercise(self.navigator)
        self.schulte_exercise = SchulteExercise(self.navigator)
        self.priming_exercise = PrimingExercise(self.navigator)

        # Register screens
        self._register_screens()

    def _register_screens(self) -> None:
        nav = self.navigator

        nav.register_screen(
            "main_menu", lambda: MainMenuScreen(nav))
        nav.register_screen(
            "login", lambda: LoginScreen(nav))
        nav.register_screen(
            "settings", lambda: SettingsScreen(nav))
        nav.register_screen(
            "dashboard", lambda: DashboardScreen(nav, self._exercise_callbacks()))
        nav.register_screen(
            "stats", lambda: StatsScreen(nav))
        nav.register_screen(
            "introduction", lambda: IntroductionScreen(nav))
        nav.register_screen(
            "paths", lambda: PathSelectionScreen(nav))
        nav.register_screen(
            "custom_paths", lambda: CustomPathsScreen(nav))
        nav.register_screen(
            "path_session", lambda: PathSessionScreen(nav))
        nav.register_screen(
            "path_builder", lambda: PathBuilderScreen(nav))

        # Exercise menu screens
        nav.register_screen(
            "flash_menu",
            lambda: FlashMenuScreen(nav, self.flash_exercise))
        nav.register_screen(
            "words_menu",
            lambda: WordsMenuScreen(nav, self.flash_exercise))
        nav.register_screen(
            "eyespan_menu",
            lambda: EyespanMenuScreen(nav, self.flash_exercise))
        nav.register_screen(
            "priming_menu",
            lambda: PrimingMenuScreen(nav, self.priming_exercise))

    def _exercise_callbacks(self) -> dict:
        nav = self.navigator
        return {
            "menu_flash": lambda: nav.navigate_to("flash_menu"),
            "menu_words": lambda: nav.navigate_to("words_menu"),
            "menu_eyespan": lambda: nav.navigate_to("eyespan_menu"),
            "menu_priming": lambda: nav.navigate_to("priming_menu"),
            "start_schulte": lambda: nav.launch_exercise(SchulteExercise),
            "setup_pacer": lambda: nav.launch_exercise(PacerExercise),
            "setup_rsvp": lambda: nav.launch_exercise(RsvpExercise),
            "setup_chunking": lambda: nav.launch_exercise(ChunkingExercise),
            "show_paths": lambda: nav.navigate_to("paths"),
            "show_stats": lambda: nav.navigate_to("stats"),
        }

    def _toggle_fullscreen(self) -> None:
        if self.window.isFullScreen():
            self.window.showNormal()
            theme_manager.fullscreen = False
        else:
            self.window.showFullScreen()
            theme_manager.fullscreen = True
        theme_manager.save()

    def run(self) -> None:
        # F11 to toggle fullscreen
        shortcut = QShortcut(QKeySequence("F11"), self.window)
        shortcut.activated.connect(self._toggle_fullscreen)

        self.navigator.navigate_to("main_menu")
        if theme_manager.fullscreen:
            self.window.showFullScreen()
        else:
            self.window.showNormal()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    NeuralSpeedAcademy().run()
