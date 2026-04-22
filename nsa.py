"""
Neural Speed Academy — PyQt6 entry point.
"""
from __future__ import annotations

import os
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

from neural_speed_academy.theme import COLORS, theme_manager, screen_metrics, load_bundled_fonts
from neural_speed_academy.repositories.user_repository import JsonUserRepository
from neural_speed_academy.navigation.navigator import Navigator



def _lazy(module: str, attr: str):
    """Import a class lazily — module is loaded on first call."""
    return getattr(__import__(module, fromlist=[attr]), attr)


# Screens and exercises are imported lazily inside register_screen lambdas
# and _exercise_callbacks() to reduce startup time.


def _set_timer_resolution():
    """Request 1ms timer resolution on Windows for smooth animations.

    Windows defaults to ~15.6ms granularity, causing jitter in QTimer-
    based animations (MOT at 16ms, priming pursuit at 20ms). Returns a
    cleanup function to restore the default on exit.
    """
    if sys.platform != "win32":
        return lambda: None
    try:
        import ctypes
        winmm = ctypes.windll.winmm
        winmm.timeBeginPeriod(1)
        return lambda: winmm.timeEndPeriod(1)
    except (AttributeError, OSError):
        return lambda: None


class NeuralSpeedAcademy:

    def __init__(self):
        self._restore_timer = _set_timer_resolution()
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Neural Speed Academy")

        # Register bundled fonts before any UI is built
        load_bundled_fonts()

        # App icon (title bar, taskbar, Alt-Tab)
        _icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(_icon_path):
            self.app.setWindowIcon(QIcon(_icon_path))

        # Load persisted app settings
        theme_manager.load()
        screen_metrics.init_from_screen()

        # Global focus indicators for accessibility
        from neural_speed_academy.theme import global_focus_css
        self.app.setStyleSheet(global_focus_css())
        def _on_theme_change(_):
            self.app.setStyleSheet(global_focus_css())
            if hasattr(self, 'stack'):
                self.stack.setStyleSheet(f"background-color: {COLORS['bg']};")
        theme_manager.on_change(_on_theme_change)

        # Main window
        self.window = QMainWindow()
        self.window.setWindowTitle("Neural Speed Academy")

        # Central stacked widget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLORS['bg']};")
        self.window.setCentralWidget(self.stack)

        # Repository
        self.user_repo = JsonUserRepository()

        # Navigator
        self.navigator = Navigator(self.stack, self.user_repo)
        self.navigator._app = self

        # Register screens
        self._register_screens()

    def _register_screens(self) -> None:
        nav = self.navigator

        def _reg(name, factory):
            nav.register_screen(name, factory)

        # Core screens (lazy imports)
        _reg("main_menu", lambda: _lazy(
            "neural_speed_academy.screens.main_menu_screen", "MainMenuScreen")(nav))
        _reg("login", lambda: _lazy(
            "neural_speed_academy.screens.login_screen", "LoginScreen")(nav))
        _reg("settings", lambda: _lazy(
            "neural_speed_academy.screens.settings_screen", "SettingsScreen")(nav))
        _reg("dashboard", lambda: _lazy(
            "neural_speed_academy.screens.dashboard_screen", "DashboardScreen")(
            nav, self._exercise_callbacks()))
        _reg("stats", lambda: _lazy(
            "neural_speed_academy.screens.stats_screen", "StatsScreen")(nav))
        _reg("introduction", lambda: _lazy(
            "neural_speed_academy.screens.introduction_screen", "IntroductionScreen")(nav))
        _reg("language", lambda: _lazy(
            "neural_speed_academy.screens.language_screen", "LanguageScreen")(nav))
        _reg("paths", lambda: _lazy(
            "neural_speed_academy.screens.paths_screen", "PathSelectionScreen")(nav))
        _reg("custom_paths", lambda: _lazy(
            "neural_speed_academy.screens.paths_screen", "CustomPathsScreen")(nav))
        _reg("path_session", lambda: _lazy(
            "neural_speed_academy.screens.path_session_screen", "PathSessionScreen")(nav))
        _reg("path_builder", lambda: _lazy(
            "neural_speed_academy.screens.path_session_screen", "PathBuilderScreen")(nav))

        # Exercise menu screens
        _reg("flash_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "FlashMenuScreen")(nav))
        _reg("words_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "WordsMenuScreen")(nav))
        _reg("eyespan_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "EyespanMenuScreen")(nav))
        _reg("schulte_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "SchulteMenuScreen")(nav))
        _reg("priming_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "PrimingMenuScreen")(nav))
        _reg("sequence_memory_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "SequenceMemoryMenuScreen")(nav))
        _reg("peripheral_flash_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "PeripheralFlashMenuScreen")(nav))
        _reg("rapid_decision_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "RapidDecisionMenuScreen")(nav))
        _reg("mot_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "MotMenuScreen")(nav))
        _reg("split_attention_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "SplitAttentionMenuScreen")(nav))
        _reg("reaction_time_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "ReactionTimeMenuScreen")(nav))
        _reg("slide_processing_menu", lambda: _lazy(
            "neural_speed_academy.screens.menu_screens", "SlideProcessingMenuScreen")(nav))
        _reg("slide_creator", lambda: _lazy(
            "neural_speed_academy.screens.slide_creator_screen", "SlideCreatorScreen")(nav))

    def _exercise_callbacks(self) -> dict:
        nav = self.navigator
        return {
            "menu_flash": lambda: nav.navigate_to("flash_menu"),
            "menu_words": lambda: nav.navigate_to("words_menu"),
            "menu_eyespan": lambda: nav.navigate_to("eyespan_menu"),
            "menu_priming": lambda: nav.navigate_to("priming_menu"),
            "menu_schulte": lambda: nav.navigate_to("schulte_menu"),
            "setup_pacer": lambda: nav.launch_exercise(
                _lazy("neural_speed_academy.exercises.pacer", "PacerExercise")),
            "setup_rsvp": lambda: nav.launch_exercise(
                _lazy("neural_speed_academy.exercises.rsvp", "RsvpExercise")),
            "setup_chunking": lambda: nav.launch_exercise(
                _lazy("neural_speed_academy.exercises.chunking", "ChunkingExercise")),
            "menu_sequence_memory": lambda: nav.navigate_to("sequence_memory_menu"),
            "menu_peripheral_flash": lambda: nav.navigate_to("peripheral_flash_menu"),
            "menu_rapid_decision": lambda: nav.navigate_to("rapid_decision_menu"),
            "menu_mot": lambda: nav.navigate_to("mot_menu"),
            "menu_split_attention": lambda: nav.navigate_to("split_attention_menu"),
            "menu_reaction_time": lambda: nav.navigate_to("reaction_time_menu"),
            "menu_slide_processing": lambda: nav.navigate_to("slide_processing_menu"),
            "start_sr": lambda: nav.launch_exercise(
                _lazy("neural_speed_academy.exercises.spaced_repetition",
                      "SpacedRepetitionExercise")),
            "show_paths": lambda: nav.navigate_to("paths"),
            "show_stats": lambda: nav.navigate_to("stats"),
        }

    _WINDOWED_MIN_W, _WINDOWED_MIN_H = 900, 650

    @staticmethod
    def _is_wayland() -> bool:
        """Detect if running under Wayland (move/position calls are no-ops)."""
        return os.environ.get("XDG_SESSION_TYPE") == "wayland" or \
               os.environ.get("WAYLAND_DISPLAY", "") != ""

    def _set_windowed(self) -> None:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt as QtCore_Qt
        self.window.setWindowFlags(
            QtCore_Qt.WindowType.Window
            | QtCore_Qt.WindowType.WindowCloseButtonHint
            | QtCore_Qt.WindowType.WindowMinMaxButtonsHint
            | QtCore_Qt.WindowType.WindowTitleHint
        )
        self.window.setMaximumSize(16777215, 16777215)
        self.window.setMinimumSize(self._WINDOWED_MIN_W, self._WINDOWED_MIN_H)
        # Size to 75% of available screen, but at least the minimum
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            w = max(int(geo.width() * 0.75), self._WINDOWED_MIN_W)
            h = max(int(geo.height() * 0.75), self._WINDOWED_MIN_H)
            w = min(w, geo.width() - 40)
            h = min(h, geo.height() - 40)
            self.window.resize(w, h)
        else:
            self.window.resize(self._WINDOWED_MIN_W, self._WINDOWED_MIN_H)
        self.window.showNormal()
        # Update screen metrics to match window size
        screen_metrics.update_from_window(self.window.width(), self.window.height())
        # Center on screen — skip on Wayland where move() is a no-op
        if screen and not self._is_wayland():
            geo = screen.availableGeometry()
            x = (geo.width() - self.window.width()) // 2 + geo.x()
            y = (geo.height() - self.window.height()) // 2 + geo.y()
            self.window.move(x, y)
        self.window.raise_()
        self.window.activateWindow()

    def _set_fullscreen(self) -> None:
        self.window.setMinimumSize(0, 0)
        self.window.setMaximumSize(16777215, 16777215)
        # #osx — showFullScreen() uses macOS native fullscreen animation
        # (slides to a new Space). This is slower than on Windows/Linux
        # and cannot be suppressed without FramelessWindowHint.
        # #linux — on Wayland, fullscreen is compositor-managed and may
        # not cover panels/docks on all desktops.
        self.window.showFullScreen()
        # Update screen metrics to match full screen
        screen_metrics.init_from_screen()

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

    def _try_handle_enter(self) -> bool:
        """Enter: click the continue/start button if visible.

        Returns True if handled (event should be consumed).
        """
        # Don't intercept when a text input or button has focus
        from PyQt6.QtWidgets import QTextEdit, QLineEdit, QPushButton
        focus = self.app.focusWidget()
        if isinstance(focus, (QTextEdit, QLineEdit, QPushButton)):
            return False

        widget = self.stack.currentWidget()
        if not widget:
            return False

        for btn in widget.findChildren(QPushButton):
            text = btn.text().upper()
            if text in ("CONTINUE", "CONTINUE TRAINING", "CREATE & START") and btn.isVisible():
                btn.click()
                return True
        return False

    def _try_handle_space(self) -> bool:
        """Space: pause/resume during exercises.

        Returns True if handled (event should be consumed).
        """
        # Don't intercept when a text input or button has focus
        from PyQt6.QtWidgets import QTextEdit, QLineEdit, QPushButton
        focus = self.app.focusWidget()
        if isinstance(focus, (QTextEdit, QLineEdit, QPushButton)):
            return False

        if self.navigator._current_name != "exercise":
            return False
        widget = self.stack.currentWidget()
        if widget and hasattr(widget, '_toggle_pause'):
            widget._toggle_pause()
            return True
        return False

    def run(self) -> None:
        # #osx — Ctrl maps to Cmd on macOS. QShortcut("Ctrl+Q") becomes
        # Cmd+Q, which is the standard macOS quit shortcut. F11 may be
        # captured by Mission Control unless the user disables it in
        # System Settings > Keyboard > Shortcuts.
        # #linux — F11 works on most DEs but some (e.g. tiling WMs)
        # may intercept it for their own fullscreen toggle.
        for key, handler in [
            ("F11", self._toggle_fullscreen),
            ("Escape", self._handle_escape),
            ("Ctrl+Q", lambda: self.app.quit()),
        ]:
            s = QShortcut(QKeySequence(key), self.window)
            s.setContext(Qt.ShortcutContext.ApplicationShortcut)
            s.activated.connect(handler)

        # Enter and Space handled via keyPressEvent to avoid
        # stealing events from QLineEdit, QTextEdit, QPushButton
        original_key_press = self.window.keyPressEvent

        def _key_press(event):
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if self._try_handle_enter():
                    return
            elif key == Qt.Key.Key_Space:
                if self._try_handle_space():
                    return
            original_key_press(event)

        self.window.keyPressEvent = _key_press

        self.navigator.navigate_to("main_menu")
        if theme_manager.fullscreen:
            self._set_fullscreen()
        else:
            self._set_windowed()
        try:
            sys.exit(self.app.exec())
        finally:
            self._restore_timer()


if __name__ == "__main__":
    NeuralSpeedAcademy().run()
