"""
Multiple Object Tracking (MOT) exercise.

Dots move on screen. Some are highlighted as targets, then all become
identical. User tracks targets mentally and identifies them after
movement stops. Used in professional esports and sports vision training.
"""
from __future__ import annotations

import math
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider,
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.config import MOT_CONFIG, USER_DATA_CONFIG
from neural_speed_academy.i18n import tr


class _Dot:
    """A single moving dot in the MOT arena."""

    def __init__(self, x: float, y: float, radius: float, is_target: bool):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_target = is_target
        self.selected = False
        # Velocity in pixels per frame
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle)
        self.vy = math.sin(angle)

    def move(self, speed: float, bounds: QRectF, dots: list["_Dot"]) -> None:
        """Move the dot, bounce off walls and repel from other dots."""
        self.x += self.vx * speed
        self.y += self.vy * speed

        # Bounce off walls
        if self.x - self.radius < bounds.left():
            self.x = bounds.left() + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > bounds.right():
            self.x = bounds.right() - self.radius
            self.vx = -abs(self.vx)

        if self.y - self.radius < bounds.top():
            self.y = bounds.top() + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > bounds.bottom():
            self.y = bounds.bottom() - self.radius
            self.vy = -abs(self.vy)

        # Repel from other dots to prevent overlap
        for other in dots:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            dist = math.sqrt(dx * dx + dy * dy)
            min_dist = self.radius + other.radius + 4
            if dist < min_dist and dist > 0:
                # Push apart
                overlap = (min_dist - dist) / 2
                nx = dx / dist
                ny = dy / dist
                self.x += nx * overlap
                self.y += ny * overlap
                # Deflect velocity slightly
                self.vx += nx * 0.3
                self.vy += ny * 0.3

        # Normalize velocity to prevent acceleration from repulsion
        mag = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if mag > 0:
            self.vx /= mag
            self.vy /= mag

        # Add slight random perturbation for natural movement
        self.vx += random.uniform(-0.05, 0.05)
        self.vy += random.uniform(-0.05, 0.05)
        mag = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if mag > 0:
            self.vx /= mag
            self.vy /= mag

    def contains(self, px: float, py: float) -> bool:
        dx = self.x - px
        dy = self.y - py
        return (dx * dx + dy * dy) <= (self.radius + 5) ** 2


class _MotArena(QWidget):
    """Custom widget that renders and animates the MOT dots."""

    PHASE_HIGHLIGHT = "highlight"
    PHASE_TRACKING = "tracking"
    PHASE_SELECTION = "selection"
    PHASE_RESULT = "result"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.dots: list[_Dot] = []
        self.phase: str = self.PHASE_HIGHLIGHT
        self.speed: float = 3.0
        self._on_selection_done: callable = None
        self._num_targets: int = 0
        self._selections_remaining: int = 0

        # #win #linux #osx — QTimer(16ms) targets ~60 FPS but actual
        # interval depends on OS timer resolution. Windows defaults to
        # ~15.6ms granularity (adequate). Linux/macOS are typically 1ms.
        # On slow machines or under compositor load, frames may drop.
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 FPS
        self._timer.timeout.connect(self._tick)

        self.setMinimumSize(400, 400)
        self.setMouseTracking(True)

    def setup(
        self,
        num_targets: int,
        num_distractors: int,
        speed: float,
        dot_radius: int,
        on_selection_done: callable,
    ) -> None:
        self._num_targets = num_targets
        self._selections_remaining = num_targets
        self.speed = speed
        self._on_selection_done = on_selection_done
        self.dots = []

        padding = MOT_CONFIG["arena_padding"]
        w = self.width() - 2 * padding
        h = self.height() - 2 * padding

        if w < 100 or h < 100:
            w, h = 400, 400

        total = num_targets + num_distractors
        placed: list[_Dot] = []

        for i in range(total):
            is_target = i < num_targets
            # Try to place without overlap
            for _ in range(100):
                x = random.uniform(padding + dot_radius, padding + w - dot_radius)
                y = random.uniform(padding + dot_radius, padding + h - dot_radius)
                too_close = False
                for other in placed:
                    dx = x - other.x
                    dy = y - other.y
                    if math.sqrt(dx * dx + dy * dy) < dot_radius * 3:
                        too_close = True
                        break
                if not too_close:
                    break
            dot = _Dot(x, y, dot_radius, is_target)
            placed.append(dot)

        self.dots = placed
        self.phase = self.PHASE_HIGHLIGHT
        self.update()

    def start_tracking(self) -> None:
        self.phase = self.PHASE_TRACKING
        self._timer.start()
        self.update()

    def stop_tracking(self) -> None:
        self._timer.stop()
        self.phase = self.PHASE_SELECTION
        self._selections_remaining = self._num_targets
        # Reset selections
        for dot in self.dots:
            dot.selected = False
        self.update()

    def show_results(self) -> None:
        self.phase = self.PHASE_RESULT
        self._timer.stop()
        self.update()

    def _tick(self) -> None:
        bounds = QRectF(
            MOT_CONFIG["arena_padding"],
            MOT_CONFIG["arena_padding"],
            self.width() - 2 * MOT_CONFIG["arena_padding"],
            self.height() - 2 * MOT_CONFIG["arena_padding"],
        )
        for dot in self.dots:
            dot.move(self.speed, bounds, self.dots)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = COLORS

        # Background
        painter.fillRect(self.rect(), QColor(c["bg"]))

        # Arena border
        padding = MOT_CONFIG["arena_padding"]
        arena_rect = QRectF(
            padding, padding,
            self.width() - 2 * padding,
            self.height() - 2 * padding,
        )
        painter.setPen(QPen(QColor(c["muted"]), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(arena_rect, 8, 8)

        for dot in self.dots:
            if self.phase == self.PHASE_HIGHLIGHT:
                if dot.is_target:
                    painter.setBrush(QBrush(QColor(c["accent"])))
                    painter.setPen(QPen(QColor(c["accent"]).darker(120), 2))
                else:
                    painter.setBrush(QBrush(QColor(c["muted"])))
                    painter.setPen(QPen(QColor(c["muted"]).darker(120), 1))

            elif self.phase == self.PHASE_TRACKING:
                # All dots look identical
                painter.setBrush(QBrush(QColor(c["fg"])))
                painter.setPen(QPen(QColor(c["fg"]).darker(120), 1))

            elif self.phase == self.PHASE_SELECTION:
                if dot.selected:
                    painter.setBrush(QBrush(QColor(c["accent"])))
                    painter.setPen(QPen(QColor(c["accent"]).darker(120), 2))
                else:
                    painter.setBrush(QBrush(QColor(c["fg"])))
                    painter.setPen(QPen(QColor(c["fg"]).darker(120), 1))

            elif self.phase == self.PHASE_RESULT:
                if dot.is_target and dot.selected:
                    # Correct
                    painter.setBrush(QBrush(QColor(c["success"])))
                    painter.setPen(QPen(QColor(c["success"]).darker(120), 2))
                elif dot.is_target and not dot.selected:
                    # Missed target
                    painter.setBrush(QBrush(QColor(c["alert"])))
                    painter.setPen(QPen(QColor(c["alert"]).darker(120), 2))
                elif not dot.is_target and dot.selected:
                    # Wrong selection
                    painter.setBrush(QBrush(QColor("#ef4444")))
                    painter.setPen(QPen(QColor("#ef4444").darker(120), 2))
                else:
                    painter.setBrush(QBrush(QColor(c["muted"])))
                    painter.setPen(QPen(QColor(c["muted"]).darker(120), 1))

            painter.drawEllipse(
                QPointF(dot.x, dot.y), dot.radius, dot.radius,
            )

        painter.end()

    def mousePressEvent(self, event) -> None:
        if self.phase != self.PHASE_SELECTION:
            return

        px = event.position().x()
        py = event.position().y()

        for dot in self.dots:
            if dot.contains(px, py) and not dot.selected:
                dot.selected = True
                self._selections_remaining -= 1
                self.update()

                if self._selections_remaining <= 0:
                    if self._on_selection_done:
                        self._on_selection_done()
                return


class MotExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._num_targets: int = 3
        self._num_distractors: int = 5
        self._speed: int = 3
        self._duration: int = 6
        self._total_rounds: int = 5
        self._current_round: int = 0
        self._total_correct: int = 0
        self._total_possible: int = 0
        self._arena: _MotArena | None = None

    @property
    def name(self) -> str:
        return "MOT"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True

        cfg = MOT_CONFIG
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._num_targets = kwargs.get("targets", cfg["default_targets"])
        self._num_distractors = kwargs.get("distractors", cfg["default_distractors"])
        self._speed = kwargs.get("speed", cfg["default_speed"])
        self._duration = kwargs.get("duration", cfg["default_duration"])
        self._total_rounds = kwargs.get("rounds", cfg["default_rounds"])

        # Skip config screen when launched from preset menu
        if kwargs:
            self._current_round = 0
            self._total_correct = 0
            self._total_possible = 0
            self._show_countdown(self._run_round)
            return

        self.add_nav_bar(show_stop=False)

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 10, 40, 10)
        cl.setSpacing(6)

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton(tr("chunking.guide"))
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("mot"))
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel(tr("mot.multiple_object_tracking"))
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(8)

        # Targets
        tgt_row = QHBoxLayout()
        tgt_row.addStretch()
        tgt_lbl = QLabel(tr("mot.targets"))
        tgt_lbl.setFont(make_qfont("slider_label"))
        tgt_lbl.setStyleSheet(f"color: {c['fg']};")
        tgt_row.addWidget(tgt_lbl)

        self._tgt_slider = QSlider(Qt.Orientation.Horizontal)
        self._tgt_slider.setRange(cfg["min_targets"], cfg["max_targets"])
        self._tgt_slider.setValue(self._num_targets)
        self._tgt_slider.setFixedWidth(200)
        self._tgt_slider.setStyleSheet(slider_groove)

        self._tgt_display = QLabel(str(self._num_targets))
        self._tgt_display.setFont(make_qfont("counter"))
        self._tgt_display.setStyleSheet(f"color: {c['accent']};")
        self._tgt_display.setFixedWidth(30)
        self._tgt_slider.valueChanged.connect(
            lambda v: self._tgt_display.setText(str(v))
        )
        tgt_row.addWidget(self._tgt_slider)
        tgt_row.addWidget(self._tgt_display)
        tgt_row.addStretch()
        cl.addLayout(tgt_row)

        # Distractors
        dist_row = QHBoxLayout()
        dist_row.addStretch()
        dist_lbl = QLabel(tr("mot.distractors"))
        dist_lbl.setFont(make_qfont("slider_label"))
        dist_lbl.setStyleSheet(f"color: {c['fg']};")
        dist_row.addWidget(dist_lbl)

        self._dist_slider = QSlider(Qt.Orientation.Horizontal)
        self._dist_slider.setRange(cfg["min_distractors"], cfg["max_distractors"])
        self._dist_slider.setValue(self._num_distractors)
        self._dist_slider.setFixedWidth(200)
        self._dist_slider.setStyleSheet(slider_groove)

        self._dist_display = QLabel(str(self._num_distractors))
        self._dist_display.setFont(make_qfont("counter"))
        self._dist_display.setStyleSheet(f"color: {c['accent']};")
        self._dist_display.setFixedWidth(30)
        self._dist_slider.valueChanged.connect(
            lambda v: self._dist_display.setText(str(v))
        )
        dist_row.addWidget(self._dist_slider)
        dist_row.addWidget(self._dist_display)
        dist_row.addStretch()
        cl.addLayout(dist_row)

        # Speed
        spd_row = QHBoxLayout()
        spd_row.addStretch()
        spd_lbl = QLabel(tr("mot.speed"))
        spd_lbl.setFont(make_qfont("slider_label"))
        spd_lbl.setStyleSheet(f"color: {c['fg']};")
        spd_row.addWidget(spd_lbl)

        self._spd_slider = QSlider(Qt.Orientation.Horizontal)
        self._spd_slider.setRange(cfg["min_speed"], cfg["max_speed"])
        self._spd_slider.setValue(self._speed)
        self._spd_slider.setFixedWidth(200)
        self._spd_slider.setStyleSheet(slider_groove)

        self._spd_display = QLabel(str(self._speed))
        self._spd_display.setFont(make_qfont("counter"))
        self._spd_display.setStyleSheet(f"color: {c['accent']};")
        self._spd_display.setFixedWidth(30)
        self._spd_slider.valueChanged.connect(
            lambda v: self._spd_display.setText(str(v))
        )
        spd_row.addWidget(self._spd_slider)
        spd_row.addWidget(self._spd_display)
        spd_row.addStretch()
        cl.addLayout(spd_row)

        # Duration
        dur_row = QHBoxLayout()
        dur_row.addStretch()
        dur_lbl = QLabel(tr("mot.duration_s"))
        dur_lbl.setFont(make_qfont("slider_label"))
        dur_lbl.setStyleSheet(f"color: {c['fg']};")
        dur_row.addWidget(dur_lbl)

        self._dur_slider = QSlider(Qt.Orientation.Horizontal)
        self._dur_slider.setRange(cfg["min_duration"], cfg["max_duration"])
        self._dur_slider.setValue(self._duration)
        self._dur_slider.setFixedWidth(200)
        self._dur_slider.setStyleSheet(slider_groove)

        self._dur_display = QLabel(str(self._duration))
        self._dur_display.setFont(make_qfont("counter"))
        self._dur_display.setStyleSheet(f"color: {c['accent']};")
        self._dur_display.setFixedWidth(30)
        self._dur_slider.valueChanged.connect(
            lambda v: self._dur_display.setText(str(v))
        )
        dur_row.addWidget(self._dur_slider)
        dur_row.addWidget(self._dur_display)
        dur_row.addStretch()
        cl.addLayout(dur_row)

        # Rounds
        rnd_row = QHBoxLayout()
        rnd_row.addStretch()
        rnd_lbl = QLabel(tr("mot.rounds"))
        rnd_lbl.setFont(make_qfont("slider_label"))
        rnd_lbl.setStyleSheet(f"color: {c['fg']};")
        rnd_row.addWidget(rnd_lbl)

        self._rnd_slider = QSlider(Qt.Orientation.Horizontal)
        self._rnd_slider.setRange(3, 10)
        self._rnd_slider.setValue(self._total_rounds)
        self._rnd_slider.setFixedWidth(200)
        self._rnd_slider.setStyleSheet(slider_groove)

        self._rnd_display = QLabel(str(self._total_rounds))
        self._rnd_display.setFont(make_qfont("counter"))
        self._rnd_display.setStyleSheet(f"color: {c['accent']};")
        self._rnd_display.setFixedWidth(30)
        self._rnd_slider.valueChanged.connect(
            lambda v: self._rnd_display.setText(str(v))
        )
        rnd_row.addWidget(self._rnd_slider)
        rnd_row.addWidget(self._rnd_display)
        rnd_row.addStretch()
        cl.addLayout(rnd_row)

        # Start button
        cl.addSpacing(8)
        start_btn = QPushButton(tr("mot.start"))
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(tr("mot.ctrl_enter_to_start"))
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(hint)

        # Ctrl+Enter shortcut
        shortcut = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return), self
        )
        shortcut.activated.connect(self._start_from_ui)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _start_from_ui(self) -> None:
        self._num_targets = self._tgt_slider.value()
        self._num_distractors = self._dist_slider.value()
        self._speed = self._spd_slider.value()
        self._duration = self._dur_slider.value()
        self._total_rounds = self._rnd_slider.value()
        self._current_round = 0
        self._total_correct = 0
        self._total_possible = 0
        self._show_countdown(self._run_round)

    # ── Round loop ──

    def _run_round(self) -> None:
        self._current_round += 1
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._round_lbl = QLabel(
            f"Round {self._current_round}/{self._total_rounds}"
        )
        self._round_lbl.setFont(make_qfont("counter"))
        self._round_lbl.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._round_lbl)

        top.addStretch()

        self._phase_lbl = QLabel(tr("mot.memorize_the_targets"))
        self._phase_lbl.setFont(make_qfont("btn_bold"))
        self._phase_lbl.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._phase_lbl)

        top.addStretch()

        self._score_lbl = QLabel(
            f"Score: {self._total_correct}/{self._total_possible}"
        )
        self._score_lbl.setFont(make_qfont("counter"))
        self._score_lbl.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._score_lbl)

        exit_btn = QPushButton(tr("chunking.u2716"))
        exit_btn.setAccessibleName(tr("chunking.close"))
        exit_btn.setToolTip(tr("chunking.close"))
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            btn_css(c["alert"], c["text_on_card"], padding="4px 8px",
                    radius=3, font_key="exit_btn")
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)

        self._layout.addLayout(top)

        # Arena
        self._arena = _MotArena()
        self._layout.addWidget(self._arena, 1)

        # Defer setup until arena has a size
        self._after(100, self._setup_arena)

    def _setup_arena(self) -> None:
        if not self._running or not self._arena:
            return
        self._arena.setup(
            num_targets=self._num_targets,
            num_distractors=self._num_distractors,
            speed=self._speed,
            dot_radius=MOT_CONFIG["dot_radius"],
            on_selection_done=self._on_selection_done,
        )
        # Highlight phase
        self._after(MOT_CONFIG["highlight_ms"], self._start_tracking)

    def _start_tracking(self) -> None:
        if not self._running or not self._arena:
            return
        c = COLORS
        self._phase_lbl.setText(tr("mot.track_the_targets"))
        self._phase_lbl.setStyleSheet(f"color: {c['accent']};")
        self._arena.start_tracking()
        self._after(self._duration * 1000, self._stop_tracking)

    def _stop_tracking(self) -> None:
        if not self._running or not self._arena:
            return
        c = COLORS
        self._phase_lbl.setText(
            f"SELECT {self._num_targets} TARGETS"
        )
        self._phase_lbl.setStyleSheet(f"color: {c['fg']};")
        self._arena.stop_tracking()

    def _on_selection_done(self) -> None:
        if not self._running or not self._arena:
            return

        # Score this round
        correct = sum(
            1 for d in self._arena.dots if d.is_target and d.selected
        )
        self._total_correct += correct
        self._total_possible += self._num_targets

        c = COLORS
        self._score_lbl.setText(
            f"Score: {self._total_correct}/{self._total_possible}"
        )

        # Show result overlay
        self._arena.show_results()
        self._phase_lbl.setText(
            f"{correct}/{self._num_targets} correct"
        )
        all_correct = correct == self._num_targets
        color = c["success"] if all_correct else c["alert"]
        self._phase_lbl.setStyleSheet(f"color: {color};")

        # Next round or final results
        if self._current_round >= self._total_rounds:
            self._after(1500, self._show_final_results)
        else:
            self._after(1500, self._run_round)

    # ── Results ──

    def _show_final_results(self) -> None:
        self._running = False
        score = self._total_correct
        total = self._total_possible
        pct = round(score / total * 100) if total > 0 else 0
        xp = score * USER_DATA_CONFIG["xp_per_correct"]

        result = ExerciseResult(
            exercise_name="MOT",
            score=score,
            total=total,
            xp_gained=xp,
            metadata={
                "targets": self._num_targets,
                "distractors": self._num_distractors,
                "speed": self._speed,
                "duration_s": self._duration,
                "rounds": self._total_rounds,
                "accuracy_pct": pct,
            },
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result,
            is_personal_best=is_pb,
            details=(
                f"{tr('result.targets', count=self._num_targets)}  |  "
                f"{tr('result.distractors', count=self._num_distractors)}  |  "
                f"{tr('result.speed', speed=self._speed)}\n"
                f"{tr('result.accuracy', pct=pct)}"
            ),
        )

    def _stop(self) -> None:
        self._running = False
        if self._arena:
            self._arena._timer.stop()
        self.navigator.finish_exercise()
