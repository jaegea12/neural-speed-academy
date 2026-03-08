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
    "grid_btn": "#334155",
    "grid_solved": "#166534",
    "grid_text": "#e2e8f0",
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
    "accent": "#15803d",
    "action": "#2563eb",
    "alert": "#c2410c",
    "highlight": "#fbbf24",
    "priming": "#0d9488",
    "grid_btn": "#cbd5e1",
    "grid_solved": "#86efac",
    "grid_text": "#1e293b",
    "success": "#15803d",
    "cross": "#94a3b8",
    # Semantic roles
    "btn_text": "#ffffff",
    "text_on_card": "#1e293b",
    "muted": "#64748b",
    "reader_bg": "#ffffff",
    "reader_fg": "#1e293b",
    # Difficulty tiers
    "diff_beginner": "#15803d",
    "diff_intermediate": "#2563eb",
    "diff_advanced": "#c2410c",
    "diff_elite": "#dc2626",
}

SOFT_LIGHT_COLORS = {
    "bg": "#faf7f2",
    "card": "#ede9e3",
    "fg": "#3d3929",
    "accent": "#4a7a4e",
    "action": "#4a6a8a",
    "alert": "#9e5e20",
    "highlight": "#e8d48b",
    "priming": "#4a8e7e",
    "grid_btn": "#d6cfc4",
    "grid_solved": "#b5d4b8",
    "grid_text": "#3d3929",
    "success": "#4a7a4e",
    "cross": "#a8a08e",
    # Semantic roles
    "btn_text": "#faf7f2",
    "text_on_card": "#3d3929",
    "muted": "#74705e",
    "reader_bg": "#f5f0e8",
    "reader_fg": "#3d3929",
    # Difficulty tiers
    "diff_beginner": "#4a7a4e",
    "diff_intermediate": "#4a6a8a",
    "diff_advanced": "#9e5e20",
    "diff_elite": "#a04030",
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
    "grid_btn": "#2a2a2a",
    "grid_solved": "#006400",
    "grid_text": "#ffffff",
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

FOCUS_COLORS = {
    # Warm sepia palette optimized for extended reading.
    # Based on e-reader research (Benedetto et al., 2013): warm backgrounds
    # reduce blue light exposure and visual fatigue. All text pairs exceed
    # WCAG AA 4.5:1 contrast ratio.
    "bg": "#f4ecd8",
    "card": "#e8dfc8",
    "fg": "#2c2416",
    "accent": "#486828",
    "action": "#3a5e7a",
    "alert": "#985018",
    "highlight": "#d4b85c",
    "priming": "#3a7a6a",
    "grid_btn": "#d8cfb8",
    "grid_solved": "#a0c4a0",
    "grid_text": "#2c2416",
    "success": "#486828",
    "cross": "#8a8070",
    # Semantic roles
    "btn_text": "#f4ecd8",
    "text_on_card": "#2c2416",
    "muted": "#6e6454",
    "reader_bg": "#f4ecd8",
    "reader_fg": "#2c2416",
    # Difficulty tiers
    "diff_beginner": "#486828",
    "diff_intermediate": "#3a5e7a",
    "diff_advanced": "#985018",
    "diff_elite": "#8a3028",
}

TWILIGHT_COLORS = {
    # Medium-dark warm gray — between Dark and Soft Light.
    # Reduced blue emission for evening use while maintaining
    # readability. All primary text pairs exceed WCAG AA 4.5:1.
    "bg": "#2a2a30",
    "card": "#383840",
    "fg": "#d4d0c8",
    "accent": "#7ab87a",
    "action": "#6a9ec4",
    "alert": "#d4884a",
    "highlight": "#d4c46a",
    "priming": "#5aaa9a",
    "grid_btn": "#46464e",
    "grid_solved": "#2a5a2a",
    "grid_text": "#d4d0c8",
    "success": "#7ab87a",
    "cross": "#6a6a6e",
    # Semantic roles
    "btn_text": "#1e1e22",
    "text_on_card": "#e8e4dc",
    "muted": "#9a968e",
    "reader_bg": "#d4d0c8",
    "reader_fg": "#1e1e22",
    # Difficulty tiers
    "diff_beginner": "#7ab87a",
    "diff_intermediate": "#6a9ec4",
    "diff_advanced": "#d4884a",
    "diff_elite": "#c45a4a",
}

THEME_PROFILES = {
    "dark": DARK_COLORS,
    "twilight": TWILIGHT_COLORS,
    "soft_light": SOFT_LIGHT_COLORS,
    "focus": FOCUS_COLORS,
    "light": LIGHT_COLORS,
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
    "btn_sm": ("Segoe UI", 11, "bold"),
    "section_header": ("Segoe UI", 14, "bold"),
    "counter": ("Segoe UI", 12, "bold"),
    "grid_btn": ("Segoe UI", 20, "bold"),
    "input": ("Segoe UI", 24),
    "input_sm": ("Segoe UI", 12),
    "cross": ("Arial", 50),
    "priming_dot": ("Arial", 30),
    "exit_btn": ("Arial", 14),
    "slider_label": ("Segoe UI", 12),
    "pacer_text": ("Georgia", 12),
    "nav_stats": ("Segoe UI", 11, "bold"),
    "menu_header": ("Segoe UI", 13, "bold"),
    "menu_btn": ("Segoe UI", 12),
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


# --- PyQt6 helpers ---

class ScreenMetrics:
    """Computes layout dimensions scaled to the actual screen size.
    All values are designed for 1920x1080 and scaled proportionally."""

    REF_W = 1920
    REF_H = 1080

    def __init__(self) -> None:
        self._w = self.REF_W
        self._h = self.REF_H
        self._sx = 1.0
        self._sy = 1.0

    def init_from_screen(self) -> None:
        """Call after QApplication is created."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self._w = geo.width()
            self._h = geo.height()
        self._sx = self._w / self.REF_W
        self._sy = self._h / self.REF_H

    @property
    def screen_w(self) -> int:
        return self._w

    @property
    def screen_h(self) -> int:
        return self._h

    def sw(self, ref_px: int) -> int:
        """Scale a width value."""
        return int(ref_px * self._sx)

    def sh(self, ref_px: int) -> int:
        """Scale a height value."""
        return int(ref_px * self._sy)

    def s(self, ref_px: int) -> int:
        """Scale uniformly (uses the smaller factor to avoid overflow)."""
        return int(ref_px * min(self._sx, self._sy))

    # ── Pre-computed layout values ──

    @property
    def text_input_w(self) -> int:
        """Text input width (~57% of screen)."""
        return self.sw(1100)

    @property
    def text_input_h(self) -> int:
        """Text input height for 15 lines (scaled)."""
        return self.sh(290)

    @property
    def dashboard_btn_w(self) -> int:
        return self.sw(360)

    @property
    def menu_btn_w(self) -> int:
        return self.sw(340)

    @property
    def schulte_cell(self) -> int:
        """Schulte grid cell size scaled to screen."""
        fov_cells = {"narrow": 90, "standard": 110, "wide": 120, "full": 130}
        fov = theme_manager.fov if theme_manager else "standard"
        return self.s(fov_cells.get(fov, 110))

    @property
    def reader_w(self) -> int:
        """Pacer reader page width from FOV, scaled."""
        fov = theme_manager.fov_config if theme_manager else FOV_PRESETS["standard"]
        return self.sw(fov["page_width"])

    @property
    def reader_h(self) -> int:
        """Pacer reader page height — A4-ish, capped to screen."""
        w = self.reader_w
        return min(int(w * 1.35), self._h - 120)

    @property
    def nav_bar_h(self) -> int:
        return self.sh(56)

    def fov_scaled(self) -> dict:
        """Return the active FOV preset with dimensions scaled to screen."""
        fov = theme_manager.fov_config if theme_manager else FOV_PRESETS["standard"]
        return {
            "page_width": self.sw(fov["page_width"]),
            "pad_x": self.sw(fov["pad_x"]),
            "pad_y": self.sh(fov["pad_y"]),
            "font_size": max(10, self.s(fov["font_size"])),
            "label": fov.get("label", ""),
        }


screen_metrics = ScreenMetrics()


def font_css(key: str) -> str:
    """Return QSS font-family, font-size, font-weight declarations."""
    spec = FONTS[key]
    family = spec[0]
    size = spec[1]
    weight = "bold" if len(spec) > 2 and spec[2] == "bold" else "normal"
    return f'font-family: "{family}"; font-size: {size}pt; font-weight: {weight};'


def make_qfont(key: str):
    """Create a QFont from a FONTS key."""
    from PyQt6.QtGui import QFont
    spec = FONTS[key]
    font = QFont(spec[0], spec[1])
    if len(spec) > 2 and spec[2] == "bold":
        font.setBold(True)
    return font
