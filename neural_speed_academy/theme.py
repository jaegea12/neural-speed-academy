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
    "card": "#233044",
    "fg": "#e2e8f0",
    "accent": "#22c55e",
    "action": "#60a5fa",
    "alert": "#fb923c",
    "highlight": "#e8b020",
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
    "card": "#dbe1eb",
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
    "muted": "#596980",
    "reader_bg": "#ffffff",
    "reader_fg": "#1e293b",
    # Difficulty tiers
    "diff_beginner": "#15803d",
    "diff_intermediate": "#2563eb",
    "diff_advanced": "#c2410c",
    "diff_elite": "#dc2626",
}

SILVER_COLORS = {
    # Cool neutral grey — clearly darker than Soft Light, lighter than Twilight.
    # Minimal color temperature bias for distraction-free reading.
    # All primary text pairs exceed WCAG AA 4.5:1.
    "bg": "#b0b0b8",
    "card": "#9a9aa4",
    "fg": "#1a1a22",
    "accent": "#144a2e",
    "action": "#2a4a7a",
    "alert": "#904810",
    "highlight": "#c4b050",
    "priming": "#1a6a5a",
    "grid_btn": "#a0a0aa",
    "grid_solved": "#80b088",
    "grid_text": "#1a1a22",
    "success": "#144a2e",
    "cross": "#707078",
    # Semantic roles
    "btn_text": "#f0f0f4",
    "text_on_card": "#1a1a22",
    "muted": "#32323c",
    "reader_bg": "#c8c8d0",
    "reader_fg": "#1a1a22",
    # Difficulty tiers
    "diff_beginner": "#144a2e",
    "diff_intermediate": "#2a4a7a",
    "diff_advanced": "#904810",
    "diff_elite": "#903028",
}

SOFT_LIGHT_COLORS = {
    "bg": "#faf7f2",
    "card": "#e2ded7",
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
    "muted": "#6d6957",
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
    "card": "#ddd4be",
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
    "muted": "#6c6252",
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
    "card": "#40404a",
    "fg": "#d4d0c8",
    "accent": "#7ab87a",
    "action": "#6a9ec4",
    "alert": "#d4884a",
    "highlight": "#c0a030",
    "priming": "#5aaa9a",
    "grid_btn": "#46464e",
    "grid_solved": "#2a5a2a",
    "grid_text": "#d4d0c8",
    "success": "#7ab87a",
    "cross": "#6a6a6e",
    # Semantic roles
    "btn_text": "#1e1e22",
    "text_on_card": "#e8e4dc",
    "muted": "#a5a199",
    "reader_bg": "#d4d0c8",
    "reader_fg": "#1e1e22",
    # Difficulty tiers
    "diff_beginner": "#7ab87a",
    "diff_intermediate": "#6a9ec4",
    "diff_advanced": "#d4884a",
    "diff_elite": "#c45a4a",
}

MONO_COLORS = {
    # Pure black/white/grey — zero color distraction.
    # Useful for users who find color overstimulating.
    "bg": "#121212",
    "card": "#2a2a2a",
    "fg": "#e0e0e0",
    "accent": "#ffffff",
    "action": "#b0b0b0",
    "alert": "#ff6b6b",
    "highlight": "#ffffff",
    "priming": "#c0c0c0",
    "grid_btn": "#2a2a2a",
    "grid_solved": "#4a4a4a",
    "grid_text": "#e0e0e0",
    "success": "#ffffff",
    "cross": "#666666",
    # Semantic roles
    "btn_text": "#121212",
    "text_on_card": "#e0e0e0",
    "muted": "#888888",
    "reader_bg": "#e0e0e0",
    "reader_fg": "#121212",
    # Difficulty tiers (greyscale gradient, light → dark)
    "diff_beginner": "#c0c0c0",
    "diff_intermediate": "#a0a0a0",
    "diff_advanced": "#8e8e8e",
    "diff_elite": "#7d7d7d",
}

EMBER_COLORS = {
    # Black and red — high energy, low blue light.
    "bg": "#0a0a0a",
    "card": "#2c1e1e",
    "fg": "#e0d0d0",
    "accent": "#cc3333",
    "action": "#cc6633",
    "alert": "#ff6633",
    "highlight": "#ff9944",
    "priming": "#cc5544",
    "grid_btn": "#2a1818",
    "grid_solved": "#4a1a1a",
    "grid_text": "#e0d0d0",
    "success": "#cc3333",
    "cross": "#5a4040",
    # Semantic roles
    "btn_text": "#ffffff",
    "text_on_card": "#e0d0d0",
    "muted": "#917777",
    "reader_bg": "#e0d0d0",
    "reader_fg": "#0a0a0a",
    # Difficulty tiers
    "diff_beginner": "#cc6633",
    "diff_intermediate": "#cc3333",
    "diff_advanced": "#aa2222",
    "diff_elite": "#ff4444",
}

DARK_BLUE_COLORS = {
    # Deep navy background with bright blue accents.
    "bg": "#0d1520",
    "card": "#1c2a3d",
    "fg": "#d8e4f0",
    "accent": "#3b82f6",
    "action": "#60a5fa",
    "alert": "#f59e0b",
    "highlight": "#38bdf8",
    "priming": "#22d3ee",
    "grid_btn": "#1e3350",
    "grid_solved": "#1e3a5f",
    "grid_text": "#d8e4f0",
    "success": "#34d399",
    "cross": "#4b6a8a",
    # Semantic roles
    "btn_text": "#0d1520",
    "text_on_card": "#e8f0fa",
    "muted": "#7a9abb",
    "reader_bg": "#d8e4f0",
    "reader_fg": "#0d1520",
    # Difficulty tiers
    "diff_beginner": "#34d399",
    "diff_intermediate": "#60a5fa",
    "diff_advanced": "#f59e0b",
    "diff_elite": "#ef4444",
}

LIGHT_BLUE_COLORS = {
    # Pale sky background with navy accents.
    "bg": "#f0f5fc",
    "card": "#d4e0f0",
    "fg": "#1a2744",
    "accent": "#1d4ed8",
    "action": "#2563eb",
    "alert": "#b45309",
    "highlight": "#0ea5e9",
    "priming": "#0891b2",
    "grid_btn": "#bdd0e8",
    "grid_solved": "#93c5fd",
    "grid_text": "#1a2744",
    "success": "#059669",
    "cross": "#7c96b8",
    # Semantic roles
    "btn_text": "#ffffff",
    "text_on_card": "#1a2744",
    "muted": "#4a6080",
    "reader_bg": "#ffffff",
    "reader_fg": "#1a2744",
    # Difficulty tiers
    "diff_beginner": "#059669",
    "diff_intermediate": "#2563eb",
    "diff_advanced": "#b45309",
    "diff_elite": "#dc2626",
}

THEME_PROFILES = {
    "dark": DARK_COLORS,
    "light": LIGHT_COLORS,
    "high_contrast": HIGH_CONTRAST_COLORS,
    "focus": FOCUS_COLORS,
    "twilight": TWILIGHT_COLORS,
    "soft_light": SOFT_LIGHT_COLORS,
    "silver": SILVER_COLORS,
    "mono": MONO_COLORS,
    "ember": EMBER_COLORS,
    "dark_blue": DARK_BLUE_COLORS,
    "light_blue": LIGHT_BLUE_COLORS,
}

# Human-readable labels for the settings screen
THEME_LABELS = {
    "dark": "Dark",
    "light": "Light",
    "high_contrast": "High Contrast",
    "focus": "Warm / Focus",
    "twilight": "Twilight",
    "soft_light": "Soft Light",
    "silver": "Silver",
    "mono": "Monochrome",
    "ember": "Ember (Black/Red)",
    "dark_blue": "Dark Blue",
    "light_blue": "Light Blue",
}

# --- Font Definitions ---

FONTS = {
    "title": ("Segoe UI", 36, "bold"),
    "title_lg": ("Segoe UI", 48, "bold"),
    "header": ("Segoe UI", 26, "bold"),
    "sub": ("Segoe UI", 12),
    "tagline": ("Segoe UI", 16),
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

# FOV presets: pct = percentage of screen width, pad/font in reference pixels
FOV_PRESETS = {
    "narrow":   {"pct": 0.30, "pad_x": 50, "pad_y": 45, "font_size": 18, "label": "Narrow (Beginner)"},
    "standard": {"pct": 0.42, "pad_x": 60, "pad_y": 50, "font_size": 16, "label": "Standard"},
    "wide":     {"pct": 0.55, "pad_x": 70, "pad_y": 50, "font_size": 15, "label": "Wide (Advanced)"},
    "full":     {"pct": 0.70, "pad_x": 80, "pad_y": 50, "font_size": 14, "label": "Full (Expert)"},
    "ultra":    {"pct": 0.95, "pad_x": 90, "pad_y": 50, "font_size": 13, "label": "Ultra (Full Screen)"},
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

    # Map FOV keys to default Schulte cell size indices
    _FOV_TO_CELL = {"narrow": 0, "standard": 1, "wide": 2, "full": 3, "ultra": 3}

    def __init__(self, profile: str = DEFAULT_PROFILE):
        self._profile = profile
        self._training_text = DEFAULT_TRAINING_TEXT
        self._fov = DEFAULT_FOV
        self._font_scale: float = 1.0
        self._fullscreen: bool = True
        self._schulte_grid_size: int | None = None  # None = use config default
        self._schulte_cell_idx: int | None = None   # None = derive from FOV
        self._custom_texts: dict[str, str] = {}     # name -> text
        self._locale: str = "en"
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
    def font_scale(self) -> float:
        return self._font_scale

    @font_scale.setter
    def font_scale(self, value: float) -> None:
        self._font_scale = max(0.8, min(1.5, value))

    @property
    def fullscreen(self) -> bool:
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        self._fullscreen = value

    @property
    def schulte_grid_size(self) -> int:
        from neural_speed_academy.config import SCHULTE_CONFIG
        return self._schulte_grid_size if self._schulte_grid_size is not None else SCHULTE_CONFIG["grid_size"]

    @schulte_grid_size.setter
    def schulte_grid_size(self, value: int) -> None:
        self._schulte_grid_size = max(3, min(7, value))

    @property
    def schulte_cell_idx(self) -> int:
        if self._schulte_cell_idx is not None:
            return self._schulte_cell_idx
        return self._FOV_TO_CELL.get(self._fov, 1)

    @schulte_cell_idx.setter
    def schulte_cell_idx(self, value: int) -> None:
        self._schulte_cell_idx = max(0, min(3, value))

    @property
    def fov_config(self) -> dict:
        """Return the active FOV preset values."""
        return FOV_PRESETS.get(self._fov, FOV_PRESETS[DEFAULT_FOV])

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        from neural_speed_academy.i18n import load_locale
        load_locale(value)

    @property
    def custom_texts(self) -> dict[str, str]:
        """User-saved custom texts (name -> text)."""
        return dict(self._custom_texts)

    def save_custom_text(self, name: str, text: str) -> None:
        """Save a named custom text and persist to disk."""
        self._custom_texts[name.strip()] = text.strip()
        self.save()

    def delete_custom_text(self, name: str) -> None:
        """Delete a named custom text and persist to disk."""
        self._custom_texts.pop(name, None)
        self.save()

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
                "font_scale": self._font_scale,
                "fullscreen": self._fullscreen,
                "locale": self._locale,
            }
            if self._schulte_grid_size is not None:
                data["schulte_grid_size"] = self._schulte_grid_size
            if self._schulte_cell_idx is not None:
                data["schulte_cell_idx"] = self._schulte_cell_idx
            if self._custom_texts:
                data["custom_texts"] = self._custom_texts
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
            if "font_scale" in data:
                self._font_scale = max(0.8, min(1.5, float(data["font_scale"])))
            if "fullscreen" in data:
                self._fullscreen = bool(data["fullscreen"])
            sg = data.get("schulte_grid_size")
            if sg is not None:
                self._schulte_grid_size = int(sg)
            sc = data.get("schulte_cell_idx")
            if sc is not None:
                self._schulte_cell_idx = int(sc)
            ct = data.get("custom_texts")
            if isinstance(ct, dict):
                self._custom_texts = {k: v for k, v in ct.items()
                                      if isinstance(k, str) and isinstance(v, str)}
            locale = data.get("locale", "en")
            if isinstance(locale, str) and len(locale) >= 2:
                self._locale = locale
                from neural_speed_academy.i18n import load_locale
                load_locale(locale)
        except (IOError, json.JSONDecodeError, TypeError):
            pass

    def reset_defaults(self) -> None:
        """Reset to default settings and save."""
        self.set_profile(DEFAULT_PROFILE)
        self._training_text = DEFAULT_TRAINING_TEXT
        self._fov = DEFAULT_FOV
        self._font_scale = 1.0
        # Preserve custom texts across resets
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

    def update_from_window(self, width: int, height: int) -> None:
        """Update dimensions to match the actual window size."""
        self._w = width
        self._h = height
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
        fov_cells = {"narrow": 90, "standard": 110, "wide": 120, "full": 130, "ultra": 140}
        fov = theme_manager.fov if theme_manager else "standard"
        return self.s(fov_cells.get(fov, 110))

    @property
    def reader_w(self) -> int:
        """Pacer reader page width from FOV percentage, capped to screen."""
        fov = theme_manager.fov_config if theme_manager else FOV_PRESETS["standard"]
        return min(int(self._w * fov["pct"]), self._w - 40)

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
        page_w = min(int(self._w * fov["pct"]), self._w - 40)
        return {
            "page_width": page_w,
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
    size = int(spec[1] * theme_manager.font_scale)
    weight = "bold" if len(spec) > 2 and spec[2] == "bold" else "normal"
    return f'font-family: "{family}"; font-size: {size}pt; font-weight: {weight};'


def make_qfont(key: str):
    """Create a QFont from a FONTS key."""
    from PyQt6.QtGui import QFont
    spec = FONTS[key]
    size = int(spec[1] * theme_manager.font_scale)
    font = QFont(spec[0], size)
    if len(spec) > 2 and spec[2] == "bold":
        font.setBold(True)
    return font


def _luminance(hex_color: str) -> float:
    """Relative luminance of a hex color (0.0–1.0)."""
    vals = []
    for i in (1, 3, 5):
        s = int(hex_color[i:i + 2], 16) / 255.0
        vals.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]


def _color_shift(hex_color: str, amount: int) -> str:
    """Lighten (positive) or darken (negative) a hex color."""
    r = max(0, min(255, int(hex_color[1:3], 16) + amount))
    g = max(0, min(255, int(hex_color[3:5], 16) + amount))
    b = max(0, min(255, int(hex_color[5:7], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def input_css(*, widget: str = "QLineEdit") -> str:
    """Generate QSS for text input fields with a subtle border."""
    c = COLORS
    return (
        f"{widget} {{ background-color: {c['card']}; "
        f"color: {c['text_on_card']}; "
        f"border: 1px solid {c['muted']}; "
        f"padding: 8px; border-radius: 4px; }}"
        f"{widget}:focus {{ border: 1px solid {c['accent']}; }}"
    )


def btn_css(bg: str, fg: str, *, padding: str = "12px",
            radius: int = 4, min_width: int = 0,
            font_key: str = "btn_bold") -> str:
    """Generate QPushButton QSS with hover and pressed states."""
    # Shift hover away from the screen background to avoid blending.
    # If the shift hits the ceiling/floor (e.g. #ffffff can't lighten),
    # reverse direction so hover is always visible.
    bg_lum = _luminance(COLORS["bg"])
    btn_lum = _luminance(bg)
    if btn_lum < bg_lum:
        hover_bg = _color_shift(bg, -25)
        press_bg = _color_shift(bg, -40)
    else:
        hover_bg = _color_shift(bg, 25)
        press_bg = _color_shift(bg, -20)
    # If shift had no effect (color capped), go the other way
    if hover_bg == bg:
        hover_bg = _color_shift(bg, -25)
        press_bg = _color_shift(bg, -40)
    mw = f"min-width: {min_width}px; " if min_width else ""
    c = COLORS
    return (
        f"QPushButton {{ {font_css(font_key)} background-color: {bg}; "
        f"color: {fg}; border: 2px solid transparent; padding: {padding}; "
        f"border-radius: {radius}px; {mw}}}"
        f"QPushButton:hover {{ background-color: {hover_bg}; }}"
        f"QPushButton:pressed {{ background-color: {press_bg}; }}"
        f"QPushButton:focus {{ border: 2px solid {c['accent']}; }}"
    )


def global_focus_css() -> str:
    """App-wide QSS for visible focus indicators.

    Only effective for widgets that don't set their own border in inline QSS.
    Widgets with inline styles must use 'border: 2px solid transparent' instead
    of 'border: 2px solid transparent' so the :focus border can take effect.
    """
    c = COLORS
    accent = c["accent"]
    return (
        f"QPushButton:focus {{ border: 2px solid {accent}; }}"
        f"QSlider:focus {{ border: 2px solid {accent}; border-radius: 4px; }}"
        f"QComboBox:focus {{ border: 2px solid {accent}; }}"
        f"QCheckBox:focus {{ outline: 2px solid {accent}; }}"
        f"QRadioButton:focus {{ outline: 2px solid {accent}; }}"
        f"QTableWidget:focus {{ border: 2px solid {accent}; }}"
        f"QTextEdit:focus {{ border: 2px solid {accent}; }}"
        f"QLineEdit:focus {{ border: 2px solid {accent}; }}"
    )

