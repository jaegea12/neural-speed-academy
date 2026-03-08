"""
UI theme constants for Neural Speed Academy.
Supports multiple color profiles with runtime switching.
Settings are persisted to a JSON file independent of user profiles.
"""
from __future__ import annotations

import json
import os


# --- Color Profiles ---

DARK_COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "fg": "#e2e8f0",
    "accent": "#22c55e",
    "action": "#60a5fa",
    "alert": "#fb923c",
    "highlight": "#fde047",
    "priming": "#2dd4bf",
    "grid_btn": "#3b82f6",
    "grid_solved": "#166534",
    "success": "#22c55e",
    "cross": "#64748b",
    # Semantic roles
    "btn_text": "#0f172a",
    "text_on_card": "#ffffff",
    "muted": "#94a3b8",
    "reader_bg": "#e2e8f0",
    "reader_fg": "#0f172a",
    # Difficulty tiers (beginner → advanced → elite)
    "diff_beginner": "#22c55e",
    "diff_intermediate": "#60a5fa",
    "diff_advanced": "#fb923c",
    "diff_elite": "#ef4444",
}

LIGHT_COLORS = {
    "bg": "#f8fafc",
    "card": "#e2e8f0",
    "fg": "#1e293b",
    "accent": "#16a34a",
    "action": "#2563eb",
    "alert": "#ea580c",
    "highlight": "#fbbf24",
    "priming": "#0d9488",
    "grid_btn": "#3b82f6",
    "grid_solved": "#86efac",
    "success": "#16a34a",
    "cross": "#94a3b8",
    # Semantic roles
    "btn_text": "#ffffff",
    "text_on_card": "#1e293b",
    "muted": "#64748b",
    "reader_bg": "#ffffff",
    "reader_fg": "#1e293b",
    # Difficulty tiers
    "diff_beginner": "#16a34a",
    "diff_intermediate": "#2563eb",
    "diff_advanced": "#ea580c",
    "diff_elite": "#dc2626",
}

SOFT_LIGHT_COLORS = {
    "bg": "#faf7f2",
    "card": "#ede9e3",
    "fg": "#3d3929",
    "accent": "#5a8a5e",
    "action": "#5b7fa5",
    "alert": "#c47a3a",
    "highlight": "#e8d48b",
    "priming": "#5a9e8f",
    "grid_btn": "#7a9bb5",
    "grid_solved": "#b5d4b8",
    "success": "#5a8a5e",
    "cross": "#a8a08e",
    # Semantic roles
    "btn_text": "#faf7f2",
    "text_on_card": "#3d3929",
    "muted": "#8a8475",
    "reader_bg": "#f5f0e8",
    "reader_fg": "#3d3929",
    # Difficulty tiers
    "diff_beginner": "#5a8a5e",
    "diff_intermediate": "#5b7fa5",
    "diff_advanced": "#c47a3a",
    "diff_elite": "#b54a3a",
}

HIGH_CONTRAST_COLORS = {
    "bg": "#000000",
    "card": "#1a1a1a",
    "fg": "#ffffff",
    "accent": "#00ff7f",
    "action": "#00bfff",
    "alert": "#ff6347",
    "highlight": "#ffff00",
    "priming": "#00ffff",
    "grid_btn": "#0066cc",
    "grid_solved": "#006400",
    "success": "#00ff7f",
    "cross": "#aaaaaa",
    # Semantic roles
    "btn_text": "#000000",
    "text_on_card": "#ffffff",
    "muted": "#bbbbbb",
    "reader_bg": "#ffffff",
    "reader_fg": "#000000",
    # Difficulty tiers
    "diff_beginner": "#00ff7f",
    "diff_intermediate": "#00bfff",
    "diff_advanced": "#ff6347",
    "diff_elite": "#ff0000",
}

THEME_PROFILES = {
    "dark": DARK_COLORS,
    "light": LIGHT_COLORS,
    "soft_light": SOFT_LIGHT_COLORS,
    "high_contrast": HIGH_CONTRAST_COLORS,
}

# --- Font Definitions ---

FONTS = {
    "title": ("Segoe UI", 36, "bold"),
    "header": ("Segoe UI", 26, "bold"),
    "sub": ("Segoe UI", 12),
    "body": ("Segoe UI", 11),
    "flash": ("Consolas", 90, "bold"),
    "rsvp": ("Segoe UI", 48, "bold"),
    "pacer": ("Georgia", 16),
    "btn": ("Segoe UI", 11),
    "btn_bold": ("Segoe UI", 12, "bold"),
    "btn_lg": ("Segoe UI", 16, "bold"),
    "btn_sm": ("Segoe UI", 10, "bold"),
    "section_header": ("Segoe UI", 14, "bold"),
    "counter": ("Segoe UI", 12, "bold"),
    "grid_btn": ("Segoe UI", 16, "bold"),
    "input": ("Segoe UI", 24),
    "input_sm": ("Segoe UI", 12),
    "cross": ("Arial", 50),
    "priming_dot": ("Arial", 30),
    "exit_btn": ("Arial", 14),
    "slider_label": ("Segoe UI", 12),
    "pacer_text": ("Georgia", 12),
    "nav_stats": ("Segoe UI", 11, "bold"),
    "menu_header": ("Segoe UI", 10, "bold"),
    "menu_btn": ("Segoe UI", 10),
    "treeview": ("Segoe UI", 10),
    "treeview_heading": ("Segoe UI", 10, "bold"),
}


DEFAULT_PROFILE = "dark"
DEFAULT_FOV = "standard"

# FOV presets: (page_width, pad_x, pad_y, font_size)
FOV_PRESETS = {
    "narrow":   {"page_width": 480, "pad_x": 50, "pad_y": 45, "font_size": 18, "label": "Narrow (Beginner)"},
    "standard": {"page_width": 620, "pad_x": 60, "pad_y": 50, "font_size": 16, "label": "Standard"},
    "wide":     {"page_width": 780, "pad_x": 70, "pad_y": 50, "font_size": 14, "label": "Wide (Advanced)"},
    "full":     {"page_width": 940, "pad_x": 80, "pad_y": 50, "font_size": 13, "label": "Full (Expert)"},
}
DEFAULT_TRAINING_TEXT = (
    "Speed reading is the process of rapidly recognizing and absorbing phrases "
    "or sentences on a page all at once rather than identifying individual words. "
    "The amount of information that we process seems to be growing by the day, "
    "whether it is emails, reports, websites, or books. We are likely to feel "
    "pressured to get through this information more quickly so that we can stay "
    "informed and make better decisions. Most people read at an average rate of "
    "250 words per minute, though some are naturally quicker than others. But the "
    "ability to speed read could mean that you double this rate. We do not "
    "necessarily read each letter in a word or each word in a sentence. Instead, "
    "we use context and prior knowledge to fill in the gaps. The key to speed "
    "reading is to train your eyes and brain to process information more "
    "efficiently. This involves reducing subvocalization, expanding your visual "
    "span, and minimizing regression. With practice, you can learn to take in "
    "more words per fixation and move through text more fluidly. The goal is not "
    "just to read faster but to maintain or improve comprehension while doing so."
)
SETTINGS_FILE = "nsa_settings.json"


class ThemeManager:
    """Manages app-level settings: color profile and shared training text.

    Settings are stored in a JSON file independent of user profiles.
    """

    def __init__(self, profile: str = DEFAULT_PROFILE):
        self._profile = profile
        self._training_text = DEFAULT_TRAINING_TEXT
        self._fov = DEFAULT_FOV
        self._listeners: list = []

    @property
    def profile(self) -> str:
        return self._profile

    @property
    def training_text(self) -> str:
        return self._training_text

    @training_text.setter
    def training_text(self, value: str) -> None:
        self._training_text = value.strip() or DEFAULT_TRAINING_TEXT

    @property
    def fov(self) -> str:
        return self._fov

    @fov.setter
    def fov(self, value: str) -> None:
        if value in FOV_PRESETS:
            self._fov = value

    @property
    def fov_config(self) -> dict:
        """Return the active FOV preset values."""
        return FOV_PRESETS.get(self._fov, FOV_PRESETS[DEFAULT_FOV])

    @property
    def colors(self) -> dict:
        return THEME_PROFILES.get(self._profile, DARK_COLORS)

    def set_profile(self, profile: str) -> None:
        if profile not in THEME_PROFILES:
            return
        self._profile = profile
        for listener in self._listeners:
            listener(profile)

    def on_change(self, callback) -> None:
        """Register a callback for theme changes."""
        self._listeners.append(callback)

    def save(self) -> None:
        """Persist current settings to disk."""
        try:
            data = {
                "profile": self._profile,
                "training_text": self._training_text,
                "fov": self._fov,
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass

    def load(self) -> None:
        """Load settings from disk. Falls back to defaults on error."""
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            profile = data.get("profile", DEFAULT_PROFILE)
            if profile in THEME_PROFILES:
                self.set_profile(profile)
            text = data.get("training_text", "")
            if text:
                self._training_text = text
            fov = data.get("fov", DEFAULT_FOV)
            if fov in FOV_PRESETS:
                self._fov = fov
        except (IOError, json.JSONDecodeError, TypeError):
            pass

    def reset_defaults(self) -> None:
        """Reset to default settings and save."""
        self.set_profile(DEFAULT_PROFILE)
        self._training_text = DEFAULT_TRAINING_TEXT
        self._fov = DEFAULT_FOV
        self.save()

    @staticmethod
    def available_profiles() -> list:
        return list(THEME_PROFILES.keys())


# Global theme manager instance
theme_manager = ThemeManager(DEFAULT_PROFILE)


def get_colors() -> dict:
    """Get the active color palette."""
    return theme_manager.colors


# Module-level COLORS dict for backward compatibility.
# Updated in place when the theme changes so all existing
# imports of COLORS see the new values.
COLORS = dict(DARK_COLORS)


def _sync_colors(profile: str) -> None:
    """Update the module-level COLORS dict in place when theme changes."""
    COLORS.clear()
    COLORS.update(THEME_PROFILES[profile])


theme_manager.on_change(_sync_colors)
