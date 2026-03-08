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
        il.addWidget(fov_box, alignment=Qt.AlignmentFlag.AlignCenter)

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

        self._text_edit = QTextEdit()
        self._text_edit.setFont(make_qfont("body"))
        self._text_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; border: none; "
            f"padding: 8px; border-radius: 4px; }}"
        )
        self._text_edit.setFixedHeight(180)
        self._text_edit.setPlainText(theme_manager.training_text)
        il.addWidget(self._text_edit)

        il.addSpacing(15)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        apply_btn = QPushButton("APPLY & SAVE")
        apply_btn.setFont(make_qfont("btn_bold"))
        apply_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 8px 30px; border-radius: 4px; }}"
        )
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self._apply_and_save)
        btn_row.addWidget(apply_btn)

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

    def _apply_and_save(self) -> None:
        for btn in self._profile_group.buttons():
            if btn.isChecked():
                theme_manager.set_profile(btn.property("profile_key"))
                break
        for btn in self._fov_group.buttons():
            if btn.isChecked():
                theme_manager.fov = btn.property("fov_key")
                break
        theme_manager.training_text = self._text_edit.toPlainText()
        theme_manager.save()
        self.navigator.navigate_to("main_menu")

    def _reset_defaults(self) -> None:
        theme_manager.reset_defaults()
        self.navigator.navigate_to("settings")
