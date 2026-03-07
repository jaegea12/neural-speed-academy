"""
UI theme constants for Neural Speed Academy.
"""
from __future__ import annotations

# --- Original Color Scheme ---
# COLORS = {
#     "bg": "#1e293b",          # Deep Slate Blue
#     "card": "#334155",        # Lighter Slate
#     "fg": "#f1f5f9",          # Soft White
#     "accent": "#10b981",      # Emerald Green
#     "action": "#3b82f6",      # Soft Blue
#     "alert": "#f59e0b",       # Amber
#     "highlight": "#fef3c7",   # Pale Yellow
#     "priming": "#00FFCC",     # Cyan for eye priming
#     "grid_btn": "#475569",    # Grid button default
#     "grid_solved": "#375e53", # Subtle green for solved
#     "success": "#10b981",     # Green for start/success actions
#     "cross": "#475569",       # Subtle color for fixation cross
# }

# --- Improved Dark Mode (Better Contrast) ---
COLORS = {
    "bg": "#0f172a",          # Darker navy (less blue glare)
    "card": "#1e293b",        # Slate for cards
    "fg": "#e2e8f0",          # Warm white (easier on eyes)
    "btn_fg": "#ffffff",      # Pure white for button text
    "btn_bg": "#3b82f6",      # Blue button background (high contrast)
    "accent": "#22c55e",      # Brighter green (better visibility)
    "action": "#60a5fa",      # Lighter blue (more readable)
    "alert": "#fb923c",       # Orange (clearer warning)
    "highlight": "#fde047",   # Yellow (better flash visibility)
    "priming": "#2dd4bf",     # Teal (softer than cyan)
    "grid_btn": "#3b82f6",    # Blue for menu buttons (matches btn_bg)
    "grid_solved": "#166534", # Darker green for solved
    "success": "#22c55e",     # Match accent
    "cross": "#64748b",       # More visible cross
}

FONTS = {
    "header": ("Segoe UI", 26, "bold"),
    "sub": ("Segoe UI", 12),
    "body": ("Segoe UI", 11),
    "flash": ("Consolas", 90, "bold"),
    "pacer": ("Georgia", 22),
}
