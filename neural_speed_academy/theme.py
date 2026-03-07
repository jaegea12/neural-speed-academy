"""
UI theme constants for Neural Speed Academy.
Supports multiple color profiles with runtime switching.
"""
from __future__ import annotations


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
}

THEME_PROFILES = {
    "dark": DARK_COLORS,
    "light": LIGHT_COLORS,
    "soft_light": SOFT_LIGHT_COLORS,
    "high_contrast": HIGH_CONTRAST_COLORS,
}

# --- Font Definitions ---

FONTS = {
    "header": ("Segoe UI", 26, "bold"),
    "sub": ("Segoe UI", 12),
    "body": ("Segoe UI", 11),
    "flash": ("Consolas", 90, "bold"),
    "pacer": ("Georgia", 22),
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


class ThemeManager:
    """Manages the active color profile and notifies listeners on change."""

    def __init__(self, profile: str = "dark"):
        self._profile = profile
        self._listeners: list = []

    @property
    def profile(self) -> str:
        return self._profile

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

    @staticmethod
    def available_profiles() -> list:
        return list(THEME_PROFILES.keys())


# Global theme manager instance
theme_manager = ThemeManager("dark")


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
