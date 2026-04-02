"""
Neural Speed Academy — PyQt6 entry point.
"""
from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
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
    SequenceMemoryMenuScreen, RapidDecisionMenuScreen,
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
        nav.register_screen(
            "sequence_memory_menu",
            lambda: SequenceMemoryMenuScreen(nav))
        nav.register_screen(
            "rapid_decision_menu",
            lambda: RapidDecisionMenuScreen(nav))

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
            "menu_sequence_memory": lambda: nav.navigate_to("sequence_memory_menu"),
            "menu_rapid_decision": lambda: nav.navigate_to("rapid_decision_menu"),
            "show_paths": lambda: nav.navigate_to("paths"),
            "show_stats": lambda: nav.navigate_to("stats"),
        }

    _WINDOWED_MIN_W, _WINDOWED_MIN_H = 900, 650

    def _set_windowed(self) -> None:
        from PyQt6.QtWidgets import QApplication
        self.window.setMaximumSize(16777215, 16777215)
        self.window.setMinimumSize(self._WINDOWED_MIN_W, self._WINDOWED_MIN_H)
        # Size to 75% of available screen, but at least the minimum
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            w = max(int(geo.width() * 0.75), self._WINDOWED_MIN_W)
            h = max(int(geo.height() * 0.75), self._WINDOWED_MIN_H)
            # Don't exceed available area
            w = min(w, geo.width() - 40)
            h = min(h, geo.height() - 40)
            self.window.resize(w, h)
        else:
            self.window.resize(self._WINDOWED_MIN_W, self._WINDOWED_MIN_H)
        self.window.showNormal()
        # Center on screen
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.window.width()) // 2 + geo.x()
            y = (geo.height() - self.window.height()) // 2 + geo.y()
            self.window.move(x, y)

    def _set_fullscreen(self) -> None:
        self.window.setMinimumSize(0, 0)
        self.window.setMaximumSize(16777215, 16777215)
        self.window.showFullScreen()

    def _toggle_fullscreen(self) -> None:
        if self.window.isFullScreen():
            self._set_windowed()
            theme_manager.fullscreen = False
        else:
            self._set_fullscreen()
            theme_manager.fullscreen = True
        theme_manager.save()

    def _handle_escape(self) -> None:
        """Esc: go back, then main menu, then quit."""
        current = self.navigator._current_name

        # If in an exercise, stop it
        if current == "exercise":
            widget = self.stack.currentWidget()
            if widget and hasattr(widget, '_stop_exercise'):
                widget._stop_exercise()
            return

        # If on main menu, trigger quit
        if current == "main_menu":
            widget = self.stack.currentWidget()
            if widget and hasattr(widget, '_quit'):
                widget._quit()
            return

        # If on settings, check unsaved changes via the intercept
        if current == "settings":
            widget = self.stack.currentWidget()
            if widget and hasattr(widget, '_check_unsaved'):
                if not widget._check_unsaved():
                    return

        # Otherwise go back
        self.navigator.go_back()

    def _handle_enter(self) -> None:
        """Enter: click the continue/start button if visible."""
        widget = self.stack.currentWidget()
        if not widget:
            return

        # Don't intercept Enter when a text input has focus
        from PyQt6.QtWidgets import QTextEdit, QLineEdit
        focus = self.app.focusWidget()
        if isinstance(focus, (QTextEdit, QLineEdit)):
            return

        # Look for a CONTINUE or START button on the current screen
        from PyQt6.QtWidgets import QPushButton
        for btn in widget.findChildren(QPushButton):
            text = btn.text().upper()
            if text in ("CONTINUE", "CONTINUE TRAINING", "CREATE & START") and btn.isVisible():
                btn.click()
                return

    def _handle_space(self) -> None:
        """Space: pause/resume during exercises."""
        # Don't intercept Space when a text input has focus
        from PyQt6.QtWidgets import QTextEdit, QLineEdit
        focus = self.app.focusWidget()
        if isinstance(focus, (QTextEdit, QLineEdit)):
            return

        if self.navigator._current_name != "exercise":
            return
        widget = self.stack.currentWidget()
        if widget and hasattr(widget, '_toggle_pause'):
            widget._toggle_pause()

    def run(self) -> None:
        # Global keyboard shortcuts
        for key, handler in [
            ("F11", self._toggle_fullscreen),
            ("Escape", self._handle_escape),
            ("Return", self._handle_enter),
            ("Space", self._handle_space),
            ("Ctrl+Q", lambda: self.app.quit()),
        ]:
            s = QShortcut(QKeySequence(key), self.window)
            s.setContext(Qt.ShortcutContext.ApplicationShortcut)
            s.activated.connect(handler)

        self.navigator.navigate_to("main_menu")
        if theme_manager.fullscreen:
            self._set_fullscreen()
        else:
            self._set_windowed()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    NeuralSpeedAcademy().run()
