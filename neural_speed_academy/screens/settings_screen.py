"""
Settings screen for theme, FOV, and training text configuration.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QComboBox, QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.config import TEXT_LIBRARY
from neural_speed_academy.theme import (
    COLORS, FOV_PRESETS, THEME_LABELS, make_qfont, font_css, theme_manager,
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
        self.add_nav_bar(intercept_back=self._check_unsaved)

        # Snapshot saved state on first build only; preserve across theme rebuilds
        if not hasattr(self, '_initial_profile'):
            self._initial_profile = theme_manager.profile
            self._initial_fov = theme_manager.fov
            self._initial_fullscreen = theme_manager.fullscreen
            self._initial_text = theme_manager.training_text

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.setContentsMargins(20, 20, 20, 20)

        # Use available width instead of fixed
        inner = QFrame()
        inner.setStyleSheet("background: transparent;")
        il = QVBoxLayout(inner)
        il.setSpacing(6)
        il.setContentsMargins(20, 0, 20, 0)

        title = QLabel("SETTINGS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(title)
        il.addSpacing(10)

        # --- Top row: Color Profile | FOV | Display Mode side by side ---
        top_row = QHBoxLayout()
        top_row.setSpacing(30)

        rb_style = _radio_style(c)

        # -- Color Profile column --
        profile_section = QVBoxLayout()
        profile_section.setSpacing(4)

        sec1 = QLabel("COLOR PROFILE")
        sec1.setFont(make_qfont("section_header"))
        sec1.setStyleSheet(f"color: {c['accent']};")
        il.addWidget(sec1, alignment=Qt.AlignmentFlag.AlignCenter)

        dark_profiles = [
            ("dark", THEME_LABELS["dark"]),
            ("twilight", THEME_LABELS["twilight"]),
            ("high_contrast", THEME_LABELS["high_contrast"]),
            ("mono", THEME_LABELS["mono"]),
        ]
        light_profiles = [
            ("silver", THEME_LABELS["silver"]),
            ("soft_light", THEME_LABELS["soft_light"]),
            ("focus", THEME_LABELS["focus"]),
            ("light", THEME_LABELS["light"]),
        ]

        self._profile_group = QButtonGroup(self)

        theme_cols = QHBoxLayout()
        theme_cols.setSpacing(20)
        for col_label, profiles in [("DARK", dark_profiles), ("LIGHT", light_profiles)]:
            col = QVBoxLayout()
            col.setSpacing(3)
            header = QLabel(col_label)
            header.setFont(make_qfont("btn_sm"))
            header.setStyleSheet(f"color: {c['muted']};")
            col.addWidget(header)
            for key, label in profiles:
                rb = QRadioButton(label)
                rb.setFont(make_qfont("btn"))
                rb.setStyleSheet(rb_style)
                rb.setProperty("profile_key", key)
                if key == theme_manager.profile:
                    rb.setChecked(True)
                self._profile_group.addButton(rb)
                col.addWidget(rb)
            col.addStretch()
            theme_cols.addLayout(col)
        profile_section.addLayout(theme_cols)
        self._profile_group.buttonClicked.connect(self._on_profile_changed)
        top_row.addLayout(profile_section, 3)

        # -- FOV column --
        fov_section = QVBoxLayout()
        fov_section.setSpacing(4)
        sec2 = QLabel("FIELD OF VIEW")
        sec2.setFont(make_qfont("section_header"))
        sec2.setStyleSheet(f"color: {c['accent']};")
        fov_section.addWidget(sec2)
        fov_desc = QLabel("Pacer page width & font")
        fov_desc.setFont(make_qfont("btn_sm"))
        fov_desc.setStyleSheet(f"color: {c['muted']};")
        fov_section.addWidget(fov_desc)

        self._fov_group = QButtonGroup(self)
        for key, preset in FOV_PRESETS.items():
            rb = QRadioButton(preset["label"])
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(rb_style)
            rb.setProperty("fov_key", key)
            if key == theme_manager.fov:
                rb.setChecked(True)
            self._fov_group.addButton(rb)
            fov_section.addWidget(rb)
        self._fov_group.buttonClicked.connect(self._on_fov_changed)
        fov_section.addStretch()
        top_row.addLayout(fov_section, 1)

        # -- Display Mode column --
        disp_section = QVBoxLayout()
        disp_section.setSpacing(4)
        sec_disp = QLabel("DISPLAY MODE")
        sec_disp.setFont(make_qfont("section_header"))
        sec_disp.setStyleSheet(f"color: {c['accent']};")
        disp_section.addWidget(sec_disp)
        disp_desc = QLabel("F11 to toggle")
        disp_desc.setFont(make_qfont("btn_sm"))
        disp_desc.setStyleSheet(f"color: {c['muted']};")
        disp_section.addWidget(disp_desc)

        self._disp_group = QButtonGroup(self)
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
            disp_section.addWidget(rb)
        self._disp_group.buttonClicked.connect(self._on_display_changed)
        disp_section.addStretch()
        top_row.addLayout(disp_section, 1)

        il.addLayout(top_row)

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

        il.addSpacing(20)

        # --- Keyboard Shortcuts Reference ---
        sec_keys = QLabel("KEYBOARD SHORTCUTS")
        sec_keys.setFont(make_qfont("section_header"))
        sec_keys.setStyleSheet(f"color: {c['accent']};")
        sec_keys.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(sec_keys)

        shortcuts = [
            ("Esc", "Go back / Main menu / Quit"),
            ("Enter", "Continue (training path, results)"),
            ("Space", "Pause / Resume exercise"),
            ("Ctrl+Enter", "Start exercise from config screen"),
            ("Ctrl+Q", "Quit application"),
            ("F11", "Toggle fullscreen"),
        ]
        for key, desc in shortcuts:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            key_lbl = QLabel(key)
            key_lbl.setFont(make_qfont("btn_bold"))
            key_lbl.setStyleSheet(
                f"color: {c['accent']}; background-color: {c['card']}; "
                f"padding: 2px 8px; border-radius: 3px;"
            )
            key_lbl.setFixedWidth(120)
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(key_lbl)
            desc_lbl = QLabel(desc)
            desc_lbl.setFont(make_qfont("body"))
            desc_lbl.setStyleSheet(f"color: {c['fg']};")
            row.addWidget(desc_lbl)
            row.addStretch()
            il.addLayout(row)

        cl.addWidget(inner)

    def _has_unsaved_changes(self) -> bool:
        """Check if any settings differ from the last saved state."""
        if theme_manager.profile != self._initial_profile:
            return True
        if theme_manager.fov != self._initial_fov:
            return True
        if theme_manager.fullscreen != self._initial_fullscreen:
            return True
        if hasattr(self, '_text_edit'):
            current_text = self._text_edit.toPlainText().strip() or theme_manager.training_text
            if current_text != self._initial_text:
                return True
        return False

    def _check_unsaved(self) -> bool:
        """Intercept navigation away. Returns True to allow, False to block."""
        if not self._has_unsaved_changes():
            return True

        c = COLORS
        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("You have unsaved changes. Do you want to save before leaving?")
        msg.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; color: {c['fg']}; }}"
            f"QLabel {{ color: {c['fg']}; }}"
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 20px; border-radius: 4px; min-width: 80px; }}"
        )
        save_btn = msg.addButton("Save", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton("Discard", QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == save_btn:
            self._save()
            return True
        elif clicked == discard_btn:
            # Revert unsaved changes
            theme_manager.set_profile(self._initial_profile)
            theme_manager.fov = self._initial_fov
            theme_manager.fullscreen = self._initial_fullscreen
            return True
        else:
            return False

    def _load_library_text(self, name: str) -> None:
        entry = TEXT_LIBRARY.get(name)
        if entry:
            _difficulty, text = entry
            self._text_edit.setPlainText(text)

    def _on_profile_changed(self, btn) -> None:
        profile = btn.property("profile_key")
        theme_manager.set_profile(profile)
        # Save to user profile if logged in
        user = self.navigator.get_user()
        if user:
            user.theme = profile
            self.navigator.save_user()
        # Rebuild in-place to reflect new colors without polluting nav history
        self.show_screen()

    def _on_fov_changed(self, btn) -> None:
        theme_manager.fov = btn.property("fov_key")

    def _on_display_changed(self, btn) -> None:
        is_fs = btn.property("disp_key") == "fullscreen"
        theme_manager.fullscreen = is_fs
        theme_manager.save()
        # Delegate to the app's window management
        app = self.navigator._app
        if app:
            if is_fs:
                app._set_fullscreen()
            else:
                app._set_windowed()

    def _save(self) -> None:
        theme_manager.training_text = self._text_edit.toPlainText()
        theme_manager.save()
        # Update snapshot so back-navigation won't warn again
        self._initial_profile = theme_manager.profile
        self._initial_fov = theme_manager.fov
        self._initial_fullscreen = theme_manager.fullscreen
        self._initial_text = theme_manager.training_text

    def _reset_defaults(self) -> None:
        theme_manager.reset_defaults()
        # Reset the snapshot since defaults were saved
        self._initial_profile = theme_manager.profile
        self._initial_fov = theme_manager.fov
        self._initial_fullscreen = theme_manager.fullscreen
        self._initial_text = theme_manager.training_text
        self.show_screen()
