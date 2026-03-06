import tkinter as tk
from typing import Optional

from neural_speed_academy.theme import COLORS
from neural_speed_academy.state import UserProfile
from neural_speed_academy.repositories.user_repository import JsonUserRepository
from neural_speed_academy.navigation.navigator import Navigator
from neural_speed_academy.screens.login_screen import LoginScreen
from neural_speed_academy.screens.dashboard_screen import DashboardScreen
from neural_speed_academy.screens.stats_screen import StatsScreen
from neural_speed_academy.screens.menu_screens import (
    FlashMenuScreen,
    WordsMenuScreen,
    EyespanMenuScreen,
)
from neural_speed_academy.exercises.flash import FlashExercise
from neural_speed_academy.exercises.schulte import SchulteExercise
from neural_speed_academy.exercises.priming import PrimingExercise
from neural_speed_academy.exercises.pacer import PacerExercise


class SpeedReadingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Speed Academy | Comprehensive Edition")
        try: 
            self.root.state('zoomed') 
        except: 
            self.root.geometry("1280x800")
        self.root.configure(bg=COLORS["bg"])
        
        # Repository for user data persistence
        self.user_repo = JsonUserRepository()
        
        # Navigator for screen management
        self.navigator = Navigator(self.root, self.user_repo)
        
        # Exercise instances
        self.flash_exercise = FlashExercise(self.root, self.navigator)
        self.schulte_exercise = SchulteExercise(self.root, self.navigator)
        self.priming_exercise = PrimingExercise(self.root, self.navigator)
        self.pacer_exercise = PacerExercise(self.root, self.navigator)
        
        self._register_screens()
        
        # Start with login screen
        self.navigator.to_login()

    def _register_screens(self) -> None:
        """Register all screens with the navigator."""
        # Exercise callbacks for dashboard
        exercise_callbacks = {
            "menu_flash": lambda: self.navigator.navigate_to("flash_menu"),
            "menu_words": lambda: self.navigator.navigate_to("words_menu"),
            "start_priming": self.priming_exercise.start,
            "menu_eyespan": lambda: self.navigator.navigate_to("eyespan_menu"),
            "start_schulte": self.schulte_exercise.start,
            "setup_pacer": self.pacer_exercise.start,
            "show_stats": lambda: self.navigator.navigate_to("stats"),
        }
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReadingApp(root)
    root.mainloop()