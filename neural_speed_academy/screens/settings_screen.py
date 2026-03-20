"""
Settings screen for theme, FOV, and training text configuration.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.config import TEXT_LIBRARY
from neural_speed_academy.theme import (
    COLORS, FOV_PRESETS, make_qfont, font_css, theme_manager,
)


def _radio_style(c: dict) -> str:
    """QSS for radio buttons with visible indicator in all themes."""
    return (
        f"QRadioButton {{ color: {c['fg']}; background: transparent; spacing: 8px; }}"
        f"QRadioButton::indicator {{ width: 16px; height: 16px; "
        f"border: 2px solid {c['muted']}; border-radius: 8px; "
        f"background: transparent; }}"
        f"QRadioButton::indicator:checked {{ "
        f"border: 2px solid {c['accent']}; "
        f"background: {c['accent']}; }}"
    )


class SettingsScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.setContentsMargins(40, 20, 40, 20)

        # Fixed-width inner container for centered look
        inner = QFrame()
        inner.setFixedWidth(750)
        inner.setStyleSheet("background: transparent;")
        il = QVBoxLayout(inner)
        il.setSpacing(6)

        title = QLabel("SETTINGS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(title)
        il.addSpacing(20)

        # --- Color Profile ---
        sec1 = QLabel("COLOR PROFILE")
        sec1.setFont(make_qfont("section_header"))
        sec1.setStyleSheet(f"color: {c['accent']};")
        sec1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(sec1)

        profiles = {
            "dark": "Dark",
            "twilight": "Twilight",
            "soft_light": "Soft Light",
            "focus": "Focus (Low Fatigue)",
            "light": "Light",
            "high_contrast": "High Contrast",
        }

        rb_style = _radio_style(c)
        self._profile_group = QButtonGroup(self)
        profile_box = QFrame()
        profile_box.setFixedWidth(250)
        profile_box.setStyleSheet("background: transparent;")
        pbl = QVBoxLayout(profile_box)
        pbl.setContentsMargins(0, 0, 0, 0)
        pbl.setSpacing(4)
        for key, label in profiles.items():
            rb = QRadioButton(label)
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(rb_style)
            rb.setProperty("profile_key", key)
            if key == theme_manager.profile:
                rb.setChecked(True)
            self._profile_group.addButton(rb)
            pbl.addWidget(rb)
        self._profile_group.buttonClicked.connect(self._on_profile_changed)
        il.addWidget(profile_box, alignment=Qt.AlignmentFlag.AlignCenter)

        il.addSpacing(15)

        # --- FOV ---
        sec2 = QLabel("FIELD OF VIEW")
        sec2.setFont(make_qfont("section_header"))
        sec2.setStyleSheet(f"color: {c['accent']};")
        sec2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(sec2)

        fov_desc = QLabel("Controls page width and font size in the Pacer exercise")
        fov_desc.setFont(make_qfont("body"))
        fov_desc.setStyleSheet(f"color: {c['muted']};")
        fov_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(fov_desc)

        self._fov_group = QButtonGroup(self)
        fov_box = QFrame()
        fov_box.setFixedWidth(250)
        fov_box.setStyleSheet("background: transparent;")
        fbl = QVBoxLayout(fov_box)
        fbl.setContentsMargins(0, 0, 0, 0)
        fbl.setSpacing(4)
        for key, preset in FOV_PRESETS.items():
            rb = QRadioButton(preset["label"])
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(rb_style)
            rb.setProperty("fov_key", key)
            if key == theme_manager.fov:
                rb.setChecked(True)
            self._fov_group.addButton(rb)
            fbl.addWidget(rb)
        self._fov_group.buttonClicked.connect(self._on_fov_changed)
        il.addWidget(fov_box, alignment=Qt.AlignmentFlag.AlignCenter)

        il.addSpacing(15)

        # --- Display Mode ---
        sec_disp = QLabel("DISPLAY MODE")
        sec_disp.setFont(make_qfont("section_header"))
        sec_disp.setStyleSheet(f"color: {c['accent']};")
        sec_disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(sec_disp)

        disp_desc = QLabel("Press F11 at any time to toggle fullscreen")
        disp_desc.setFont(make_qfont("body"))
        disp_desc.setStyleSheet(f"color: {c['muted']};")
        disp_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(disp_desc)

        self._disp_group = QButtonGroup(self)
        disp_box = QFrame()
        disp_box.setFixedWidth(250)
        disp_box.setStyleSheet("background: transparent;")
        dbl = QVBoxLayout(disp_box)
        dbl.setContentsMargins(0, 0, 0, 0)
        dbl.setSpacing(4)
        for key, label in [("fullscreen", "Fullscreen"), ("windowed", "Windowed")]:
            rb = QRadioButton(label)
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(rb_style)
            rb.setProperty("disp_key", key)
            is_fs = theme_manager.fullscreen
            rb.setChecked(
                (key == "fullscreen" and is_fs) or
                (key == "windowed" and not is_fs)
            )
            self._disp_group.addButton(rb)
            dbl.addWidget(rb)
        self._disp_group.buttonClicked.connect(self._on_display_changed)
        il.addWidget(disp_box, alignment=Qt.AlignmentFlag.AlignCenter)

        il.addSpacing(15)

        # --- Training Text ---
        sec3 = QLabel("TRAINING TEXT")
        sec3.setFont(make_qfont("section_header"))
        sec3.setStyleSheet(f"color: {c['accent']};")
        sec3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(sec3)

        text_desc = QLabel("Used as the default text for Pacer, RSVP, and Chunking exercises")
        text_desc.setFont(make_qfont("body"))
        text_desc.setStyleSheet(f"color: {c['muted']};")
        text_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(text_desc)

        # Library selector
        lib_row = QHBoxLayout()
        lib_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lib_label = QLabel("Load from library:")
        lib_label.setFont(make_qfont("btn_sm"))
        lib_label.setStyleSheet(f"color: {c['fg']}; background: transparent;")
        lib_row.addWidget(lib_label)

        self._lib_combo = QComboBox()
        self._lib_combo.setFont(make_qfont("btn_sm"))
        self._lib_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; border: none; "
            f"padding: 4px 8px; border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; "
            f"selection-background-color: {c['accent']}; }}"
        )
        self._lib_combo.addItem("")
        for name in TEXT_LIBRARY:
            self._lib_combo.addItem(name)
        self._lib_combo.currentTextChanged.connect(self._load_library_text)
        lib_row.addWidget(self._lib_combo)
        il.addLayout(lib_row)

        from neural_speed_academy.theme import input_css
        self._text_edit = QTextEdit()
        self._text_edit.setFont(make_qfont("body"))
        self._text_edit.setStyleSheet(input_css(widget="QTextEdit"))
        self._text_edit.setFixedHeight(180)
        self._text_edit.setPlainText(theme_manager.training_text)
        il.addWidget(self._text_edit)

        il.addSpacing(15)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        save_btn = QPushButton("SAVE")
        save_btn.setFont(make_qfont("btn_bold"))
        save_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 8px 30px; border-radius: 4px; }}"
        )
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton("DEFAULT SETTINGS")
        reset_btn.setFont(make_qfont("btn_bold"))
        reset_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['fg']}; border: none; "
            f"padding: 8px 30px; border-radius: 4px; }}"
        )
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(reset_btn)

        il.addLayout(btn_row)
        cl.addWidget(inner)

    def _load_library_text(self, name: str) -> None:
        entry = TEXT_LIBRARY.get(name)
        if entry:
            _difficulty, text = entry
            self._text_edit.setPlainText(text)

    def _on_profile_changed(self, btn) -> None:
        theme_manager.set_profile(btn.property("profile_key"))
        # Rebuild to reflect new colors
        self.navigator.navigate_to("settings")

    def _on_fov_changed(self, btn) -> None:
        theme_manager.fov = btn.property("fov_key")

    def _on_display_changed(self, btn) -> None:
        is_fs = btn.property("disp_key") == "fullscreen"
        theme_manager.fullscreen = is_fs
        theme_manager.save()
        window = self.window()
        if window:
            if is_fs:
                window.setMinimumSize(0, 0)
                window.setMaximumSize(16777215, 16777215)
                window.showFullScreen()
            else:
                window.setMaximumSize(16777215, 16777215)
                window.setMinimumSize(1024, 768)
                window.resize(1024, 768)
                window.showNormal()

    def _save(self) -> None:
        theme_manager.training_text = self._text_edit.toPlainText()
        theme_manager.save()

    def _reset_defaults(self) -> None:
        theme_manager.reset_defaults()
        self.navigator.navigate_to("settings")
