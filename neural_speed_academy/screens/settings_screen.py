"""
Settings screen for theme, FOV, and training text configuration.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QFrame,
    QMessageBox, QSlider,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area

from neural_speed_academy.theme import (
    COLORS, FOV_PRESETS, THEME_LABELS, make_qfont, font_css, btn_css,
    theme_manager,
)
from neural_speed_academy.i18n import tr


def _radio_style(c: dict) -> str:
    """QSS for radio buttons with visible indicator in all themes."""
    return (
        f"QRadioButton {{ color: {c['fg']}; background: transparent; "
        f"spacing: 8px; padding: 2px 4px; border-radius: 3px; }}"
        f"QRadioButton:hover {{ background-color: {c['card']}; }}"
        f"QRadioButton::indicator {{ width: 16px; height: 16px; "
        f"border: 2px solid {c['muted']}; border-radius: 8px; "
        f"background: transparent; }}"
        f"QRadioButton::indicator:checked {{ "
        f"border: 2px solid {c['accent']}; "
        f"background: {c['accent']}; }}"
        f"QRadioButton:focus {{ outline: 2px solid {c['accent']}; }}"
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
        cl.setContentsMargins(50, 20, 50, 20)
        cl.setSpacing(6)

        title = QLabel(tr("settings.settings"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(10)

        # --- Settings: 3 sections side by side ---
        rb_style = _radio_style(c)

        top_row = QHBoxLayout()
        top_row.setSpacing(40)
        top_row.addStretch(1)

        # -- COLOR PROFILE section (two sub-columns) --
        dark_profiles = [
            ("dark", THEME_LABELS["dark"]),
            ("twilight", THEME_LABELS["twilight"]),
            ("high_contrast", THEME_LABELS["high_contrast"]),
            ("mono", THEME_LABELS["mono"]),
            ("ember", THEME_LABELS["ember"]),
            ("dark_blue", THEME_LABELS["dark_blue"]),
        ]
        light_profiles = [
            ("silver", THEME_LABELS["silver"]),
            ("soft_light", THEME_LABELS["soft_light"]),
            ("focus", THEME_LABELS["focus"]),
            ("light", THEME_LABELS["light"]),
            ("light_blue", THEME_LABELS["light_blue"]),
        ]

        self._profile_group = QButtonGroup(self)

        profile_section = QVBoxLayout()
        profile_section.setSpacing(4)
        sec1 = QLabel(tr("settings.color_profile"))
        sec1.setFont(make_qfont("section_header"))
        sec1.setStyleSheet(f"color: {c['accent']};")
        profile_section.addWidget(sec1)

        theme_cols = QHBoxLayout()
        theme_cols.setSpacing(30)
        for col_label, profiles in [(tr("settings.dark"), dark_profiles), (tr("settings.light"), light_profiles)]:
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
        top_row.addLayout(profile_section, 2)

        # -- FIELD OF VIEW section --
        fov_section = QVBoxLayout()
        fov_section.setSpacing(4)
        sec2 = QLabel(tr("settings.field_of_view"))
        sec2.setFont(make_qfont("section_header"))
        sec2.setStyleSheet(f"color: {c['accent']};")
        fov_section.addWidget(sec2)
        fov_desc = QLabel(tr("settings.pacer_page_width_font"))
        fov_desc.setFont(make_qfont("btn_sm"))
        fov_desc.setStyleSheet(f"color: {c['muted']};")
        fov_section.addWidget(fov_desc)

        self._fov_group = QButtonGroup(self)
        for key, preset in FOV_PRESETS.items():
            rb = QRadioButton(tr(f"pacer.fov.{key}.full"))
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

        # -- DISPLAY MODE section --
        disp_section = QVBoxLayout()
        disp_section.setSpacing(4)
        sec_disp = QLabel(tr("settings.display_mode"))
        sec_disp.setFont(make_qfont("section_header"))
        sec_disp.setStyleSheet(f"color: {c['accent']};")
        disp_section.addWidget(sec_disp)
        disp_desc = QLabel(tr("settings.f11_to_toggle"))
        disp_desc.setFont(make_qfont("btn_sm"))
        disp_desc.setStyleSheet(f"color: {c['muted']};")
        disp_section.addWidget(disp_desc)

        self._disp_group = QButtonGroup(self)
        for key, label in [("fullscreen", tr("settings.fullscreen")), ("windowed", tr("settings.windowed"))]:
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

        top_row.addStretch(1)

        cl.addLayout(top_row)

        cl.addSpacing(15)

        # --- Font Scale ---
        scale_row = QHBoxLayout()
        scale_row.addStretch(1)

        scale_section = QVBoxLayout()
        scale_section.setSpacing(4)
        sec_font = QLabel(tr("settings.font_size"))
        sec_font.setFont(make_qfont("section_header"))
        sec_font.setStyleSheet(f"color: {c['accent']};")
        scale_section.addWidget(sec_font)

        SCALE_STEPS = [0.8, 0.9, 1.0, 1.1, 1.25, 1.5]
        SCALE_LABELS = ["80%", "90%", "100%", "110%", "125%", "150%"]

        current_scale = theme_manager.font_scale
        # Find closest step index
        current_idx = min(
            range(len(SCALE_STEPS)),
            key=lambda i: abs(SCALE_STEPS[i] - current_scale),
        )

        slider_row = QHBoxLayout()
        slider_row.setSpacing(12)

        self._font_slider = QSlider(Qt.Orientation.Horizontal)
        self._font_slider.setMinimum(0)
        self._font_slider.setMaximum(len(SCALE_STEPS) - 1)
        self._font_slider.setValue(current_idx)
        self._font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._font_slider.setTickInterval(1)
        self._font_slider.setFixedWidth(200)
        self._font_slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
            f"QSlider:focus {{ border: 2px solid {c['accent']}; border-radius: 4px; }}"
        )
        slider_row.addWidget(self._font_slider)

        self._scale_label = QLabel(SCALE_LABELS[current_idx])
        self._scale_label.setFont(make_qfont("btn_bold"))
        self._scale_label.setStyleSheet(f"color: {c['fg']};")
        self._scale_label.setFixedWidth(50)
        slider_row.addWidget(self._scale_label)

        def _on_scale_changed(idx: int) -> None:
            scale = SCALE_STEPS[idx]
            self._scale_label.setText(SCALE_LABELS[idx])
            theme_manager.font_scale = scale
            user = self.navigator.get_user()
            if user:
                user.font_scale = scale
                self.navigator.save_user()
            self.show_screen()

        self._font_slider.valueChanged.connect(_on_scale_changed)
        scale_section.addLayout(slider_row)

        scale_row.addLayout(scale_section)
        scale_row.addStretch(1)
        cl.addLayout(scale_row)

        cl.addSpacing(15)

        # --- Training Text (constrained width) ---
        text_wrapper = QHBoxLayout()
        text_wrapper.addStretch(1)

        text_section = QVBoxLayout()
        text_section.setSpacing(6)

        sec3 = QLabel(tr("settings.training_text"))
        sec3.setFont(make_qfont("section_header"))
        sec3.setStyleSheet(f"color: {c['accent']};")
        sec3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_section.addWidget(sec3)

        text_desc = QLabel(tr("settings.used_as_the_default_text_for_p"))
        text_desc.setFont(make_qfont("body"))
        text_desc.setStyleSheet(f"color: {c['muted']};")
        text_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_section.addWidget(text_desc)

        from neural_speed_academy.exercises.text_library_widget import TextLibraryWidget
        self._text_lib = TextLibraryWidget(
            self, editor_height=160, show_difficulty=True,
        )
        text_section.addWidget(self._text_lib)

        text_wrapper.addLayout(text_section, 8)
        text_wrapper.addStretch(1)
        cl.addLayout(text_wrapper)

        cl.addSpacing(15)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        save_btn = QPushButton(tr("settings.save"))
        save_btn.setStyleSheet(btn_css(c["accent"], c["btn_text"], padding="8px 30px"))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton(tr("settings.default_settings"))
        reset_btn.setStyleSheet(btn_css(c["card"], c["fg"], padding="8px 30px"))
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(reset_btn)

        cl.addLayout(btn_row)

        cl.addSpacing(20)

        # --- Keyboard Shortcuts Reference ---
        sec_keys = QLabel(tr("settings.keyboard_shortcuts"))
        sec_keys.setFont(make_qfont("section_header"))
        sec_keys.setStyleSheet(f"color: {c['accent']};")
        sec_keys.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(sec_keys)

        shortcuts = [
            ("Esc", tr("settings.shortcut.esc")),
            ("Enter", tr("settings.shortcut.enter")),
            ("Space", tr("settings.shortcut.space")),
            ("Ctrl+Enter", tr("settings.shortcut.ctrl_enter")),
            ("Ctrl+Q", tr("settings.shortcut.ctrl_q")),
            ("F11", tr("settings.shortcut.f11")),
        ]
        keys_wrapper = QHBoxLayout()
        keys_wrapper.addStretch(1)
        keys_col = QVBoxLayout()
        keys_col.setSpacing(4)
        for key, desc in shortcuts:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            key_lbl = QLabel(key)
            key_lbl.setFont(make_qfont("btn_bold"))
            key_lbl.setStyleSheet(
                f"color: {c['accent']}; background-color: {c['card']}; "
                f"padding: 2px 8px; border-radius: 3px;"
            )
            key_lbl.setFixedWidth(110)
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(key_lbl)
            row.addSpacing(10)
            desc_lbl = QLabel(desc)
            desc_lbl.setFont(make_qfont("body"))
            desc_lbl.setStyleSheet(f"color: {c['fg']};")
            row.addWidget(desc_lbl)
            row.addStretch()
            keys_col.addLayout(row)
        keys_wrapper.addLayout(keys_col, 3)
        keys_wrapper.addStretch(1)
        cl.addLayout(keys_wrapper)



    def _has_unsaved_changes(self) -> bool:
        """Check if any settings differ from the last saved state."""
        if theme_manager.profile != self._initial_profile:
            return True
        if theme_manager.fov != self._initial_fov:
            return True
        if theme_manager.fullscreen != self._initial_fullscreen:
            return True
        if hasattr(self, '_text_lib'):
            current_text = self._text_lib.text().strip() or theme_manager.training_text
            if current_text != self._initial_text:
                return True
        return False

    def _check_unsaved(self) -> bool:
        """Intercept navigation away. Returns True to allow, False to block."""
        if not self._has_unsaved_changes():
            return True

        c = COLORS
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("settings.unsaved_changes"))
        msg.setText(tr("settings.you_have_unsaved_changes_do_yo"))
        msg.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; color: {c['fg']}; }}"
            f"QLabel {{ color: {c['fg']}; }}"
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 6px 20px; border-radius: 4px; min-width: 80px; }}"
            f"QPushButton:focus {{ border: 2px solid {c['fg']}; }}"
        )
        save_btn = msg.addButton(tr("settings.save"), QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton(tr("settings.discard"), QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton(tr("settings.cancel"), QMessageBox.ButtonRole.RejectRole)
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
        theme_manager.training_text = self._text_lib.text()
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
