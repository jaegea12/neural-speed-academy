"""
Shared text library widget for exercises that accept user-provided text.

Provides a dropdown (built-in + custom texts), a text editor, and
save/delete controls. Used by Pacer, RSVP, Chunking, and Settings.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QInputDialog, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.theme import (
    COLORS, make_qfont, input_css, theme_manager, screen_metrics,
)
from neural_speed_academy.config import (
    TEXT_LIBRARY, TEXT_LIBRARY_DE, TEXT_LIBRARY_FR,
    TEXT_LIBRARY_ES, TEXT_LIBRARY_IT, TEXT_LIBRARY_PT,
)
from neural_speed_academy.i18n import tr, current_locale

# All text libraries keyed by locale code
_TEXT_LIBRARIES = {
    "en": (TEXT_LIBRARY, "English"),
    "de": (TEXT_LIBRARY_DE, "Deutsch"),
    "fr": (TEXT_LIBRARY_FR, "Français"),
    "es": (TEXT_LIBRARY_ES, "Español"),
    "it": (TEXT_LIBRARY_IT, "Italiano"),
    "pt": (TEXT_LIBRARY_PT, "Português"),
}

# Prefix for custom text entries in the dropdown
_CUSTOM_PREFIX = "\u2605 "


class TextLibraryWidget(QWidget):
    """Drop-in widget: text library dropdown + editor + save/delete buttons.

    Usage::

        lib = TextLibraryWidget(parent)
        layout.addWidget(lib)
        # later:
        text = lib.text()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        editor_height: int | None = None,
        editor_width: int | None = None,
        show_difficulty: bool = False,
    ):
        super().__init__(parent)
        self._show_difficulty = show_difficulty
        c = COLORS
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # ── Row: label + combo + save + delete ──
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addStretch()

        lbl = QLabel(tr("text.library.widget.text_library"))
        lbl.setFont(make_qfont("slider_label"))
        lbl.setStyleSheet(f"color: {c['fg']}; background: transparent;")
        row.addWidget(lbl)

        combo_css = (
            f"QComboBox {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; border: 2px solid transparent; "
            f"padding: 4px 8px; border-radius: 3px; }}"
            f"QComboBox:focus {{ border: 2px solid {c['accent']}; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; "
            f"selection-background-color: {c['accent']}; }}"
        )

        self._combo = QComboBox()
        self._combo.setFont(make_qfont("btn_sm"))
        self._combo.setStyleSheet(combo_css)
        self._combo.setMinimumWidth(260)
        self._populate()
        self._combo.currentTextChanged.connect(self._on_selected)
        row.addWidget(self._combo)

        btn_style = (
            f"background-color: {c['card']}; color: {c['fg']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )

        save_btn = QPushButton(tr("text.library.widget.save_as"))
        save_btn.setFont(make_qfont("btn_sm"))
        save_btn.setStyleSheet(btn_style)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_custom)
        row.addWidget(save_btn)

        self._del_btn = QPushButton(tr("text.library.widget.delete"))
        self._del_btn.setFont(make_qfont("btn_sm"))
        self._del_btn.setStyleSheet(
            f"background-color: {c['card']}; color: {c['alert']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )
        self._del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_btn.clicked.connect(self._delete_custom)
        self._del_btn.setVisible(False)
        row.addWidget(self._del_btn)

        row.addStretch()
        root.addLayout(row)

        # ── Difficulty label (shown when a library text is selected) ──
        self._diff_label = QLabel("")
        self._diff_label.setFont(make_qfont("btn_sm"))
        self._diff_label.setStyleSheet(f"color: {c['muted']}; background: transparent;")
        self._diff_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diff_label.setVisible(False)
        root.addWidget(self._diff_label)

        # ── Text editor ──
        self._editor = QTextEdit()
        self._editor.setFont(make_qfont("pacer_text"))
        self._editor.setStyleSheet(input_css(widget="QTextEdit"))

        fm = self._editor.fontMetrics()
        h = editor_height or (fm.lineSpacing() * 15 + 20)
        w = editor_width or screen_metrics.text_input_w
        self._editor.setFixedHeight(h)
        self._editor.setFixedWidth(w)
        self._editor.setPlainText(theme_manager.training_text)
        root.addWidget(self._editor, 0, Qt.AlignmentFlag.AlignCenter)

    # ── Public API ──

    def text(self) -> str:
        """Return the current editor text."""
        return self._editor.toPlainText()

    def set_text(self, text: str) -> None:
        """Set the editor text programmatically."""
        self._editor.setPlainText(text)

    def editor(self) -> QTextEdit:
        """Direct access to the underlying QTextEdit (for focus, etc.)."""
        return self._editor

    # ── Internals ──

    def _populate(self) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItem("")

        # Show active locale's texts first, then others
        locale = current_locale()
        ordered = []
        if locale in _TEXT_LIBRARIES:
            ordered.append((locale, *_TEXT_LIBRARIES[locale]))
        for code, (lib, label) in _TEXT_LIBRARIES.items():
            if code != locale:
                ordered.append((code, lib, label))

        for i, (code, lib, label) in enumerate(ordered):
            if i > 0:
                self._combo.insertSeparator(self._combo.count())
            header = f"── {label} ──"
            self._combo.addItem(header)
            self._combo.model().item(self._combo.count() - 1).setEnabled(False)
            for name in lib:
                if self._show_difficulty:
                    difficulty = lib[name][0]
                    self._combo.addItem(f"{name}  [{difficulty}]")
                else:
                    self._combo.addItem(name)

        # Custom texts
        custom = theme_manager.custom_texts
        if custom:
            self._combo.insertSeparator(self._combo.count())
            for name in sorted(custom):
                self._combo.addItem(f"{_CUSTOM_PREFIX}{name}")

        self._combo.blockSignals(False)

    def _on_selected(self, display_name: str) -> None:
        if not display_name:
            self._del_btn.setVisible(False)
            self._diff_label.setVisible(False)
            return

        # Skip separator labels
        if display_name.startswith("──"):
            return

        # Custom text
        if display_name.startswith(_CUSTOM_PREFIX):
            real_name = display_name[len(_CUSTOM_PREFIX):]
            text = theme_manager.custom_texts.get(real_name, "")
            self._del_btn.setVisible(True)
            self._diff_label.setVisible(False)
            if text:
                self._editor.setPlainText(text)
            return

        # Built-in text (strip difficulty suffix if present)
        lib_name = display_name.split("  [")[0]
        entry = None
        for _code, (lib, _label) in _TEXT_LIBRARIES.items():
            entry = lib.get(lib_name)
            if entry:
                break
        self._del_btn.setVisible(False)
        if entry:
            difficulty, text = entry
            self._editor.setPlainText(text)
            if self._show_difficulty:
                self._diff_label.setText(tr("text.library.widget.difficulty", level=difficulty))
                self._diff_label.setVisible(True)
            else:
                self._diff_label.setVisible(False)
        else:
            self._diff_label.setVisible(False)

    def _save_custom(self) -> None:
        text = self._editor.toPlainText().strip()
        if not text:
            QMessageBox.information(self, tr("text.library.widget.empty"), tr("text.library.widget.enter_some_text_first"))
            return

        # Pre-fill with current custom name if one is selected
        current = self._combo.currentText()
        prefill = ""
        if current.startswith(_CUSTOM_PREFIX):
            prefill = current[len(_CUSTOM_PREFIX):]

        name, ok = QInputDialog.getText(
            self, tr("text.library.widget.save_custom_text"),
            tr("text.library.widget.name_label"), text=prefill,
        )
        if not ok or not name.strip():
            return

        name = name.strip()
        # Prevent overwriting built-in texts
        if any(name in lib for _code, (lib, _label) in _TEXT_LIBRARIES.items()):
            QMessageBox.warning(
                self, tr("text.library.widget.reserved_name"),
                tr("text.library.widget.reserved_name_msg", name=name),
            )
            return

        theme_manager.save_custom_text(name, text)
        self._populate()
        # Select the newly saved entry
        target = f"{_CUSTOM_PREFIX}{name}"
        idx = self._combo.findText(target)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)

    def _delete_custom(self) -> None:
        current = self._combo.currentText()
        if not current.startswith(_CUSTOM_PREFIX):
            return
        real_name = current[len(_CUSTOM_PREFIX):]

        reply = QMessageBox.question(
            self, tr("text.library.widget.delete_custom_text"),
            tr("text.library.widget.delete_confirm", name=real_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            theme_manager.delete_custom_text(real_name)
            self._populate()
            self._del_btn.setVisible(False)
