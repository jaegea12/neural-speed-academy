"""
Slide Creator screen — create and edit custom slide sets.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QSpinBox, QFrame, QFileDialog,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.repositories.slide_repository import (
    SlideSet, Slide, SlideQuestion, SlideSetRepository,
)
from neural_speed_academy.i18n import tr

_repo = SlideSetRepository()


class SlideCreatorScreen(BaseScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._current_set: SlideSet | None = None
        self._current_slide_idx: int = -1
        self._dirty: bool = False

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar(intercept_back=self._confirm_discard)

        # Main two-panel layout
        body = QHBoxLayout()
        body.setContentsMargins(16, 10, 16, 10)
        body.setSpacing(12)

        # ── Left panel: slide set list ──
        left = QVBoxLayout()
        left.setSpacing(6)

        header = QLabel(tr("slide.creator.slide_sets"))
        header.setFont(make_qfont("menu_header"))
        header.setStyleSheet(f"color: {c['accent']};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(header)

        self._set_list = QListWidget()
        self._set_list.setStyleSheet(
            f"QListWidget {{ background: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; border-radius: 4px; "
            f"padding: 4px; }}"
            f"QListWidget::item {{ padding: 6px; }}"
            f"QListWidget::item:selected {{ background: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )
        self._set_list.setFont(make_qfont("body"))
        self._set_list.currentRowChanged.connect(self._on_set_selected)
        left.addWidget(self._set_list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        new_btn = QPushButton(tr("slide.creator.new_set"))
        new_btn.setStyleSheet(btn_css(c["accent"], c["btn_text"], padding="6px 12px"))
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._new_set)
        btn_row.addWidget(new_btn)

        del_btn = QPushButton(tr("text.library.widget.delete"))
        del_btn.setStyleSheet(btn_css(c["alert"], c["btn_text"], padding="6px 12px"))
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self._delete_set)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)

        io_row = QHBoxLayout()
        io_row.setSpacing(6)
        import_btn = QPushButton(tr("slide.creator.import"))
        import_btn.setStyleSheet(btn_css(c["card"], c["fg"], padding="6px 12px"))
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.clicked.connect(self._import_set)
        io_row.addWidget(import_btn)

        export_btn = QPushButton(tr("slide.creator.export"))
        export_btn.setStyleSheet(btn_css(c["card"], c["fg"], padding="6px 12px"))
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_set)
        io_row.addWidget(export_btn)
        left.addLayout(io_row)

        body.addLayout(left, 1)

        # ── Vertical separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {c['muted']};")
        body.addWidget(sep)

        # ── Right panel: editor ──
        right = QVBoxLayout()
        right.setSpacing(8)

        # Set name
        name_row = QHBoxLayout()
        name_lbl = QLabel(tr("slide.creator.set_name"))
        name_lbl.setFont(make_qfont("body"))
        name_lbl.setStyleSheet(f"color: {c['fg']};")
        name_row.addWidget(name_lbl)
        self._name_edit = QLineEdit()
        self._name_edit.setFont(make_qfont("body"))
        self._name_edit.setStyleSheet(self._input_style())
        self._name_edit.setPlaceholderText("Enter slide set name")
        self._name_edit.textChanged.connect(lambda: self._mark_dirty())
        name_row.addWidget(self._name_edit, 1)
        right.addLayout(name_row)

        # Slide list + add/remove
        slide_header_row = QHBoxLayout()
        slide_lbl = QLabel(tr("slide.creator.slides"))
        slide_lbl.setFont(make_qfont("menu_header"))
        slide_lbl.setStyleSheet(f"color: {c['accent']};")
        slide_header_row.addWidget(slide_lbl)
        slide_header_row.addStretch()

        add_slide_btn = QPushButton(tr("slide.creator.slide"))
        add_slide_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="4px 10px", font_key="btn_sm")
        )
        add_slide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_slide_btn.clicked.connect(self._add_slide)
        slide_header_row.addWidget(add_slide_btn)

        rm_slide_btn = QPushButton(tr("slide.creator.remove_slide"))
        rm_slide_btn.setStyleSheet(
            btn_css(c["alert"], c["btn_text"], padding="4px 10px", font_key="btn_sm")
        )
        rm_slide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_slide_btn.clicked.connect(self._remove_slide)
        slide_header_row.addWidget(rm_slide_btn)
        right.addLayout(slide_header_row)

        self._slide_list = QListWidget()
        self._slide_list.setFixedHeight(100)
        self._slide_list.setStyleSheet(
            f"QListWidget {{ background: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; border-radius: 4px; padding: 4px; }}"
            f"QListWidget::item {{ padding: 4px; }}"
            f"QListWidget::item:selected {{ background: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )
        self._slide_list.setFont(make_qfont("body"))
        self._slide_list.currentRowChanged.connect(self._on_slide_selected)
        right.addWidget(self._slide_list)

        # ── Slide detail editor ──
        self._detail_frame = QFrame()
        self._detail_frame.setStyleSheet(
            f"QFrame {{ background: {c['card']}; border-radius: 6px; padding: 10px; }}"
        )
        detail = QVBoxLayout(self._detail_frame)
        detail.setSpacing(6)

        # Slide title
        title_row = QHBoxLayout()
        title_lbl = QLabel(tr("slide.creator.title"))
        title_lbl.setFont(make_qfont("body"))
        title_lbl.setStyleSheet(f"color: {c['text_on_card']};")
        title_row.addWidget(title_lbl)
        self._slide_title = QLineEdit()
        self._slide_title.setFont(make_qfont("body"))
        self._slide_title.setStyleSheet(self._input_style())
        self._slide_title.setPlaceholderText("Slide title")
        self._slide_title.textChanged.connect(self._save_slide_edits)
        title_row.addWidget(self._slide_title, 1)
        detail.addLayout(title_row)

        # Bullets
        bullets_lbl = QLabel(tr("slide.creator.bullet_points_one_per_line"))
        bullets_lbl.setFont(make_qfont("body"))
        bullets_lbl.setStyleSheet(f"color: {c['text_on_card']};")
        detail.addWidget(bullets_lbl)

        self._bullets_edit = QTextEdit()
        self._bullets_edit.setFont(make_qfont("body"))
        self._bullets_edit.setStyleSheet(self._input_style())
        self._bullets_edit.setPlaceholderText(
            "One fact per line, e.g.:\n"
            "Weight: 1.4 kg (about 2% of body weight)\n"
            "Contains approximately 86 billion neurons"
        )
        self._bullets_edit.setFixedHeight(120)
        self._bullets_edit.textChanged.connect(self._save_slide_edits)
        detail.addWidget(self._bullets_edit)

        # Questions section
        q_header_row = QHBoxLayout()
        q_lbl = QLabel(tr("slide.creator.questions"))
        q_lbl.setFont(make_qfont("body"))
        q_lbl.setStyleSheet(f"color: {c['text_on_card']};")
        q_header_row.addWidget(q_lbl)
        q_header_row.addStretch()

        add_q_btn = QPushButton(tr("slide.creator.question"))
        add_q_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="3px 8px", font_key="btn_sm")
        )
        add_q_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_q_btn.clicked.connect(self._add_question)
        q_header_row.addWidget(add_q_btn)
        detail.addLayout(q_header_row)

        self._questions_container = QVBoxLayout()
        self._questions_container.setSpacing(6)
        detail.addLayout(self._questions_container)

        detail.addStretch()
        right.addWidget(self._detail_frame, 1)

        # Save button
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton(tr("slide.creator.save_set"))
        save_btn.setFont(make_qfont("btn_lg"))
        save_btn.setStyleSheet(
            btn_css(c["success"], c["btn_text"], padding="10px 40px")
        )
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_set)
        save_row.addWidget(save_btn)
        save_row.addStretch()
        right.addLayout(save_row)

        body.addLayout(right, 3)

        self._layout.addLayout(body, 1)

        # Load existing sets
        self._refresh_set_list()
        self._show_editor(False)

        # If editing a specific set (passed via kwargs)
        edit_set = kwargs.get("edit_set")
        if edit_set and isinstance(edit_set, SlideSet):
            self._load_set(edit_set)

    # ── Styles ──

    def _input_style(self) -> str:
        c = COLORS
        return (
            f"background: {c['bg']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; border-radius: 3px; "
            f"padding: 4px 6px;"
        )

    # ── Set list management ──

    def _refresh_set_list(self) -> None:
        self._set_list.blockSignals(True)
        self._set_list.clear()
        self._sets = _repo.list_sets()
        for ss in self._sets:
            item = QListWidgetItem(f"{ss.name}  ({len(ss.slides)} slides)")
            self._set_list.addItem(item)
        self._set_list.blockSignals(False)

    def _on_set_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._sets):
            return
        if self._dirty and not self._confirm_discard():
            return
        self._load_set(self._sets[row])

    def _load_set(self, ss: SlideSet) -> None:
        self._current_set = ss
        self._name_edit.blockSignals(True)
        self._name_edit.setText(ss.name)
        self._name_edit.blockSignals(False)
        self._refresh_slide_list()
        self._show_editor(True)
        self._dirty = False
        if ss.slides:
            self._slide_list.setCurrentRow(0)
        else:
            self._current_slide_idx = -1
            self._clear_slide_detail()

    def _new_set(self) -> None:
        if self._dirty and not self._confirm_discard():
            return
        ss = SlideSet(name="New Slide Set")
        ss.slides.append(Slide(title="Slide 1", bullets=[""], questions=[]))
        self._current_set = ss
        self._name_edit.blockSignals(True)
        self._name_edit.setText(ss.name)
        self._name_edit.blockSignals(False)
        self._refresh_slide_list()
        self._show_editor(True)
        self._slide_list.setCurrentRow(0)
        self._dirty = True
        self._name_edit.setFocus()
        self._name_edit.selectAll()

    def _delete_set(self) -> None:
        row = self._set_list.currentRow()
        if row < 0 or row >= len(self._sets):
            return
        ss = self._sets[row]
        reply = QMessageBox.question(
            self, "Delete Slide Set",
            f"Delete \"{ss.name}\"? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        _repo.delete_set(ss)
        if self._current_set and self._current_set.filename == ss.filename:
            self._current_set = None
            self._current_slide_idx = -1
            self._show_editor(False)
            self._dirty = False
        self._refresh_set_list()

    # ── Slide list management ──

    def _refresh_slide_list(self) -> None:
        self._slide_list.blockSignals(True)
        self._slide_list.clear()
        if self._current_set:
            for i, slide in enumerate(self._current_set.slides):
                label = slide.title or f"Slide {i + 1}"
                self._slide_list.addItem(label)
        self._slide_list.blockSignals(False)

    def _on_slide_selected(self, row: int) -> None:
        if not self._current_set or row < 0:
            self._current_slide_idx = -1
            self._clear_slide_detail()
            return
        if row >= len(self._current_set.slides):
            return
        self._current_slide_idx = row
        self._load_slide_detail(self._current_set.slides[row])

    def _add_slide(self) -> None:
        if not self._current_set:
            return
        idx = len(self._current_set.slides) + 1
        self._current_set.slides.append(
            Slide(title=f"Slide {idx}", bullets=[""], questions=[])
        )
        self._refresh_slide_list()
        self._slide_list.setCurrentRow(len(self._current_set.slides) - 1)
        self._mark_dirty()

    def _remove_slide(self) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        if len(self._current_set.slides) <= 1:
            return  # keep at least one slide
        self._current_set.slides.pop(self._current_slide_idx)
        self._refresh_slide_list()
        new_row = min(self._current_slide_idx, len(self._current_set.slides) - 1)
        self._slide_list.setCurrentRow(new_row)
        self._mark_dirty()

    # ── Slide detail editor ──

    def _load_slide_detail(self, slide: Slide) -> None:
        self._slide_title.blockSignals(True)
        self._slide_title.setText(slide.title)
        self._slide_title.blockSignals(False)

        self._bullets_edit.blockSignals(True)
        self._bullets_edit.setPlainText("\n".join(slide.bullets))
        self._bullets_edit.blockSignals(False)

        self._rebuild_questions(slide.questions)

    def _clear_slide_detail(self) -> None:
        self._slide_title.blockSignals(True)
        self._slide_title.clear()
        self._slide_title.blockSignals(False)
        self._bullets_edit.blockSignals(True)
        self._bullets_edit.clear()
        self._bullets_edit.blockSignals(False)
        self._clear_questions_ui()

    def _save_slide_edits(self) -> None:
        """Sync UI edits back to the current slide data."""
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        slide.title = self._slide_title.text().strip()
        raw = self._bullets_edit.toPlainText()
        slide.bullets = [b for b in raw.split("\n") if b.strip()]

        # Update slide list label
        self._slide_list.blockSignals(True)
        item = self._slide_list.item(self._current_slide_idx)
        if item:
            item.setText(slide.title or f"Slide {self._current_slide_idx + 1}")
        self._slide_list.blockSignals(False)
        self._mark_dirty()

    # ── Question editor ──

    def _clear_questions_ui(self) -> None:
        while self._questions_container.count():
            item = self._questions_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _rebuild_questions(self, questions: list[SlideQuestion]) -> None:
        self._clear_questions_ui()
        for i, q in enumerate(questions):
            self._add_question_widget(i, q)

    def _add_question_widget(self, idx: int, q: SlideQuestion) -> None:
        c = COLORS
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {c['bg']}; border: 1px solid {c['muted']}; "
            f"border-radius: 4px; padding: 6px; }}"
        )
        fl = QVBoxLayout(frame)
        fl.setSpacing(4)
        fl.setContentsMargins(8, 6, 8, 6)

        # Question header + delete
        q_top = QHBoxLayout()
        q_num = QLabel(f"Q{idx + 1}:")
        q_num.setFont(make_qfont("btn_sm"))
        q_num.setStyleSheet(f"color: {c['accent']}; border: none;")
        q_top.addWidget(q_num)

        q_text = QLineEdit(q.text)
        q_text.setFont(make_qfont("body"))
        q_text.setStyleSheet(self._input_style())
        q_text.setPlaceholderText("Question text")
        q_text.textChanged.connect(lambda t, i=idx: self._update_question_text(i, t))
        q_top.addWidget(q_text, 1)

        del_q = QPushButton("✖")
        del_q.setFixedSize(24, 24)
        del_q.setStyleSheet(
            f"background: {c['alert']}; color: {c['btn_text']}; "
            f"border: none; border-radius: 3px; font-size: 12px;"
        )
        del_q.setCursor(Qt.CursorShape.PointingHandCursor)
        del_q.clicked.connect(lambda _, i=idx: self._remove_question(i))
        q_top.addWidget(del_q)
        fl.addLayout(q_top)

        # 4 answer choices + correct answer selector
        for ci in range(4):
            choice_row = QHBoxLayout()
            choice_row.setSpacing(4)

            radio = QPushButton("●" if ci == q.answer else "○")
            radio.setFixedSize(24, 24)
            radio.setStyleSheet(
                f"background: transparent; color: "
                f"{c['success'] if ci == q.answer else c['muted']}; "
                f"border: none; font-size: 14px;"
            )
            radio.setCursor(Qt.CursorShape.PointingHandCursor)
            radio.clicked.connect(
                lambda _, qi=idx, ai=ci: self._set_correct_answer(qi, ai)
            )
            choice_row.addWidget(radio)

            choice_text = QLineEdit(q.choices[ci] if ci < len(q.choices) else "")
            choice_text.setFont(make_qfont("btn_sm"))
            choice_text.setStyleSheet(self._input_style())
            choice_text.setPlaceholderText(f"Choice {ci + 1}")
            choice_text.textChanged.connect(
                lambda t, qi=idx, ai=ci: self._update_choice(qi, ai, t)
            )
            choice_row.addWidget(choice_text, 1)
            fl.addLayout(choice_row)

        self._questions_container.addWidget(frame)

    def _add_question(self) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        q = SlideQuestion(
            text="", choices=["", "", "", ""], answer=0,
        )
        slide.questions.append(q)
        self._rebuild_questions(slide.questions)
        self._mark_dirty()

    def _remove_question(self, idx: int) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        if 0 <= idx < len(slide.questions):
            slide.questions.pop(idx)
            self._rebuild_questions(slide.questions)
            self._mark_dirty()

    def _update_question_text(self, q_idx: int, text: str) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        if 0 <= q_idx < len(slide.questions):
            slide.questions[q_idx].text = text
            self._mark_dirty()

    def _update_choice(self, q_idx: int, c_idx: int, text: str) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        if 0 <= q_idx < len(slide.questions):
            q = slide.questions[q_idx]
            while len(q.choices) <= c_idx:
                q.choices.append("")
            q.choices[c_idx] = text
            self._mark_dirty()

    def _set_correct_answer(self, q_idx: int, answer_idx: int) -> None:
        if not self._current_set or self._current_slide_idx < 0:
            return
        slide = self._current_set.slides[self._current_slide_idx]
        if 0 <= q_idx < len(slide.questions):
            slide.questions[q_idx].answer = answer_idx
            self._rebuild_questions(slide.questions)
            self._mark_dirty()

    # ── Save / dirty tracking ──

    def _mark_dirty(self) -> None:
        self._dirty = True

    def _save_set(self) -> None:
        if not self._current_set:
            return
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, tr("slide.creator.missing_name"), tr("slide.creator.please_enter_a_name_for_the_sl"))
            return
        self._current_set.name = name

        # Validate: at least one slide with a title and bullet
        valid_slides = []
        for s in self._current_set.slides:
            if s.title.strip() and any(b.strip() for b in s.bullets):
                # Clean up empty bullets
                s.bullets = [b for b in s.bullets if b.strip()]
                # Clean up questions with empty text
                s.questions = [
                    q for q in s.questions
                    if q.text.strip() and any(c.strip() for c in q.choices)
                ]
                valid_slides.append(s)

        if not valid_slides:
            QMessageBox.warning(
                self, "Empty Set",
                "Add at least one slide with a title and bullet point.",
            )
            return

        self._current_set.slides = valid_slides
        _repo.save_set(self._current_set)
        self._dirty = False
        self._refresh_set_list()

        # Re-select the saved set
        for i, ss in enumerate(self._sets):
            if ss.filename == self._current_set.filename:
                self._set_list.setCurrentRow(i)
                break

    def _show_editor(self, visible: bool) -> None:
        self._name_edit.setVisible(visible)
        # Find the name label
        self._slide_list.setVisible(visible)
        self._detail_frame.setVisible(visible)

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "You have unsaved changes. Discard them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._dirty = False
            return True
        return False

    # ── Import / Export ──

    def _import_set(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Slide Set", "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            ss = _repo.import_file(path)
            self._refresh_set_list()
            # Select the imported set
            for i, s in enumerate(self._sets):
                if s.filename == ss.filename:
                    self._set_list.setCurrentRow(i)
                    break
            QMessageBox.information(
                self, "Imported",
                f"Imported \"{ss.name}\" ({len(ss.slides)} slides).",
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Import Failed",
                f"Could not import file:\n{e}",
            )

    def _export_set(self) -> None:
        row = self._set_list.currentRow()
        if row < 0 or row >= len(self._sets):
            QMessageBox.information(
                self, "No Set Selected",
                "Select a slide set to export.",
            )
            return
        ss = self._sets[row]
        default_name = f"{ss.name}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Slide Set", default_name,
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            _repo.export_file(ss, path)
            QMessageBox.information(
                self, "Exported",
                f"Exported \"{ss.name}\" to:\n{path}",
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Export Failed",
                f"Could not export file:\n{e}",
            )
