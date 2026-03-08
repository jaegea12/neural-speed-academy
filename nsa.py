"""
Neural Speed Academy — PyQt6 entry point.

Batch 1: Core infrastructure + main screens.
Screens not yet ported (introduction, menu_screens, paths_screen, exercises)
show a placeholder until batch 2.
"""
from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt

from neural_speed_academy.theme import COLORS, theme_manager
from neural_speed_academy.repositories.user_repository import JsonUserRepository
from neural_speed_academy.navigation.navigator import Navigator

from neural_speed_academy.screens.main_menu_screen import MainMenuScreen
from neural_speed_academy.screens.login_screen import LoginScreen
from neural_speed_academy.screens.settings_screen import SettingsScreen
from neural_speed_academy.screens.dashboard_screen import DashboardScreen
from neural_speed_academy.screens.stats_screen import StatsScreen


class PlaceholderScreen:
    """Temporary stand-in for screens not yet ported to PyQt6."""

    def __init__(self, navigator, label: str):
        from neural_speed_academy.screens.base import BaseScreen

        class _Placeholder(BaseScreen):
            def build(self_inner, **kwargs):
                from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
                c = COLORS
                self_inner.setStyleSheet(f"background-color: {c['bg']};")
                self_inner.add_nav_bar()

                body = QWidget()
                body.setStyleSheet(f"background-color: {c['bg']};")
                bl = QVBoxLayout(body)
                bl.setAlignment(Qt.AlignmentFlag.AlignCenter)

                from neural_speed_academy.theme import make_qfont
                lbl = QLabel(f"{label}\n\n(Coming in batch 2)")
                lbl.setFont(make_qfont("header"))
                lbl.setStyleSheet(f"color: {c['muted']};")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                bl.addWidget(lbl)

                back = QPushButton("BACK")
                back.setFont(make_qfont("btn_bold"))
                back.setStyleSheet(
                    f"background-color: {c['accent']}; color: {c['btn_text']}; "
                    f"border: none; padding: 8px 30px; border-radius: 4px;"
                )
                back.setCursor(Qt.CursorShape.PointingHandCursor)
                back.clicked.connect(navigator.go_back)
                bl.addWidget(back, alignment=Qt.AlignmentFlag.AlignCenter)

                self_inner._layout.addWidget(body, 1)

        self._cls = _Placeholder
        self._navigator = navigator

    def __call__(self):
        return self._cls(self._navigator)


class NeuralSpeedAcademy:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Neural Speed Academy")

        # Load persisted app settings
        theme_manager.load()

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

        # Register screens
        self._register_screens()

    def _register_screens(self) -> None:
        nav = self.navigator

        # Core screens (ported)
        nav.register_screen(
            "main_menu",
            lambda: MainMenuScreen(nav),
        )
        nav.register_screen(
            "login",
            lambda: LoginScreen(nav),
        )
        nav.register_screen(
            "settings",
            lambda: SettingsScreen(nav),
        )
        nav.register_screen(
            "dashboard",
            lambda: DashboardScreen(nav, self._exercise_callbacks()),
        )
        nav.register_screen(
            "stats",
            lambda: StatsScreen(nav),
        )

        # Placeholder screens (batch 2)
        placeholders = [
            ("introduction", "INTRODUCTION"),
            ("paths", "TRAINING PATHS"),
            ("path_session", "PATH SESSION"),
            ("path_builder", "PATH BUILDER"),
            ("flash_menu", "FLASH NUMBERS"),
            ("words_menu", "WORD DRILLS"),
            ("eyespan_menu", "EYE-SPAN"),
            ("priming_menu", "EYE PRIMING"),
        ]
        for name, label in placeholders:
            ph = PlaceholderScreen(nav, label)
            nav.register_screen(name, ph)

    def _exercise_callbacks(self) -> dict:
        nav = self.navigator
        return {
            "menu_flash": lambda: nav.navigate_to("flash_menu"),
            "menu_words": lambda: nav.navigate_to("words_menu"),
            "menu_eyespan": lambda: nav.navigate_to("eyespan_menu"),
            "menu_priming": lambda: nav.navigate_to("priming_menu"),
            "start_schulte": lambda: nav.navigate_to("flash_menu"),
            "setup_pacer": lambda: nav.navigate_to("flash_menu"),
            "setup_rsvp": lambda: nav.navigate_to("flash_menu"),
            "setup_chunking": lambda: nav.navigate_to("flash_menu"),
            "show_paths": lambda: nav.navigate_to("paths"),
            "show_stats": lambda: nav.navigate_to("stats"),
        }

    def run(self) -> None:
        self.navigator.navigate_to("main_menu")
        self.window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    NeuralSpeedAcademy().run()
