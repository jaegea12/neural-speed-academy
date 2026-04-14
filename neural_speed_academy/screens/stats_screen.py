"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QSizePolicy, QGridLayout, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css
from neural_speed_academy.i18n import tr, exercise_display_name


class _ConsistencyCalendar(QWidget):
    """GitHub-style heatmap that grows with the user's training history.

    Shows from the user's first training date (or current month if new)
    up to today.  Horizontally scrollable when the history exceeds the
    visible width.
    """

    CELL = 12
    GAP = 2
    MONTH_GAP = 8  # extra horizontal space between months

    def __init__(
        self, active_dates: set[str],
        first_date: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._active = active_dates  # set of "YYYY-MM-DD" strings

        today = datetime.now().date()

        # Determine start: first day of the month of the earliest session,
        # or first day of the current month for new users.
        if first_date:
            try:
                earliest = datetime.strptime(first_date, "%Y-%m-%d").date()
            except ValueError:
                earliest = today
        else:
            earliest = today
        self._start = earliest.replace(day=1)
        # Align to Monday of that week
        self._start -= timedelta(days=self._start.weekday())

        self._today = today
        # Show at least 12 weeks so the calendar never looks cramped
        min_weeks = 12
        actual_weeks = ((today - self._start).days // 7) + 1
        self._num_weeks = max(actual_weeks, min_weeks)
        # Adjust start if we expanded to meet the minimum
        if self._num_weeks > actual_weeks:
            self._start = today - timedelta(days=today.weekday()) - timedelta(weeks=self._num_weeks - 1)

        # Compute total width
        self._week_xs: list[int] = []
        self._compute_positions()

        total_w = (self._week_xs[-1] if self._week_xs else 0) + self.CELL + 10
        total_h = 7 * (self.CELL + self.GAP) + 24
        self.setFixedSize(max(total_w, 200), total_h)

    def _compute_positions(self) -> None:
        cell, gap = self.CELL, self.GAP
        x = 0
        for week in range(self._num_weeks):
            if week > 0:
                prev_day = self._start + timedelta(weeks=week - 1)
                curr_day = self._start + timedelta(weeks=week)
                if curr_day.month != prev_day.month:
                    x += self.MONTH_GAP
            self._week_xs.append(x)
            x += cell + gap

    def paintEvent(self, event) -> None:
        c = COLORS
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cell, gap = self.CELL, self.GAP
        month_h = 16

        # Month labels — skip if too close to the previous label
        font = QFont("Segoe UI", 7)
        painter.setPen(QColor(c["muted"]))
        painter.setFont(font)
        fm = painter.fontMetrics()
        prev_month = -1
        prev_label_end = -1
        for week in range(self._num_weeks):
            day = self._start + timedelta(weeks=week)
            if day.month != prev_month:
                label = day.strftime("%b")
                if day.month == 1 or week == 0:
                    label = day.strftime("%b '%y")
                x = self._week_xs[week]
                label_w = fm.horizontalAdvance(label)
                # Only draw if it won't overlap the previous label
                if x > prev_label_end + 4:
                    painter.drawText(x, 11, label)
                    prev_label_end = x + label_w
                prev_month = day.month

        # Cell colours
        bg_color = QColor(c["bg"])
        border_color = QColor(c["muted"])
        border_color.setAlpha(50)
        active_color = QColor(c["accent"])

        for week in range(self._num_weeks):
            for dow in range(7):
                day = self._start + timedelta(weeks=week, days=dow)
                if day > self._today:
                    continue
                x = self._week_xs[week]
                y = month_h + dow * (cell + gap)

                day_str = day.strftime("%Y-%m-%d")
                if day_str in self._active:
                    painter.setBrush(active_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                else:
                    painter.setBrush(bg_color)
                    painter.setPen(QPen(border_color, 1))

                painter.drawRoundedRect(x, y, cell, cell, 2, 2)

        painter.end()


class _ProgressChart(QWidget):
    """Simple line chart drawn with QPainter showing score % over time."""

    def __init__(
        self, title: str, data: list[tuple[str, float]],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._title = title
        self._data = data  # [(timestamp, pct), ...]
        self.setFixedHeight(220)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

    def paintEvent(self, event) -> None:
        c = COLORS
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin_l, margin_r, margin_t, margin_b = 50, 20, 30, 35
        chart_w = w - margin_l - margin_r
        chart_h = h - margin_t - margin_b

        # Background
        painter.fillRect(0, 0, w, h, QColor(c["card"]))

        # Title
        painter.setPen(QColor(c["text_on_card"]))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(margin_l, 20, self._title)

        if len(self._data) < 2:
            painter.setPen(QColor(c["muted"]))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(
                QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter,
                "Need at least 2 sessions to show progress"
            )
            painter.end()
            return

        # Axes
        axis_pen = QPen(QColor(c["muted"]), 1)
        painter.setPen(axis_pen)
        # Y axis
        painter.drawLine(margin_l, margin_t, margin_l, h - margin_b)
        # X axis
        painter.drawLine(margin_l, h - margin_b, w - margin_r, h - margin_b)

        # Y labels (0%, 50%, 100%)
        painter.setFont(QFont("Segoe UI", 8))
        for pct in [0, 50, 100]:
            y = margin_t + chart_h * (1 - pct / 100)
            painter.setPen(QColor(c["muted"]))
            painter.drawText(5, int(y) + 4, f"{pct}%")
            # Grid line
            grid_pen = QPen(QColor(c["muted"]), 1, Qt.PenStyle.DotLine)
            painter.setPen(grid_pen)
            painter.drawLine(margin_l, int(y), w - margin_r, int(y))

        # Data points
        n = len(self._data)
        points: list[QPointF] = []
        for i, (ts, pct) in enumerate(self._data):
            x = margin_l + (i / max(n - 1, 1)) * chart_w
            y = margin_t + chart_h * (1 - pct / 100)
            points.append(QPointF(x, y))

        # Line
        line_pen = QPen(QColor(c["accent"]), 2)
        painter.setPen(line_pen)
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

        # Trend line (linear regression)
        if n >= 3:
            pcts = [pct for _, pct in self._data]
            x_vals = list(range(n))
            x_mean = sum(x_vals) / n
            y_mean = sum(pcts) / n
            num = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, pcts))
            den = sum((x - x_mean) ** 2 for x in x_vals)
            if den > 0:
                slope = num / den
                intercept = y_mean - slope * x_mean
                t_start = max(0.0, min(100.0, intercept))
                t_end = max(0.0, min(100.0, slope * (n - 1) + intercept))
                tx0 = margin_l
                ty0 = margin_t + chart_h * (1 - t_start / 100)
                tx1 = margin_l + chart_w
                ty1 = margin_t + chart_h * (1 - t_end / 100)
                trend_color = QColor(c["action"])
                trend_color.setAlpha(140)
                trend_pen = QPen(trend_color, 1.5, Qt.PenStyle.DashLine)
                painter.setPen(trend_pen)
                painter.drawLine(QPointF(tx0, ty0), QPointF(tx1, ty1))

        # Dots
        painter.setBrush(QColor(c["accent"]))
        painter.setPen(Qt.PenStyle.NoPen)
        for p in points:
            painter.drawEllipse(p, 4, 4)

        # X labels (first and last timestamp)
        painter.setPen(QColor(c["muted"]))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(margin_l, h - 5, self._data[0][0])
        last_ts = self._data[-1][0]
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(last_ts)
        painter.drawText(w - margin_r - tw, h - 5, last_ts)

        painter.end()


class StatsScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        user = self.navigator.get_user()
        if not user:
            self.navigator.require_login("stats")
            return

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(60, 20, 60, 30)

        title = QLabel(tr("stats.performance_analytics"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(15)

        self._build_summary(cl, user)
        self._build_consistency(cl, user)
        self._build_personal_bests(cl, user)
        self._build_insights(cl, user)
        self._build_progress_charts(cl, user)
        self._build_history(cl, user)
        self._build_export(cl, user)

    # ── Summary card ──

    def _build_summary(self, layout: QVBoxLayout, user) -> None:
        c = COLORS
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; "
            f"padding: 20px;"
        )
        cl = QVBoxLayout(card)

        # Top row: 4 stat cells
        stats_row = QHBoxLayout()
        level = user.xp // 1000 + 1
        stats = [
            (tr("stats.total_xp"), str(user.xp), c["accent"]),
            (tr("stats.level"), str(level), c["action"]),
            (tr("stats.streak"), tr("stats.streak_days", count=user.streak), c["highlight"]),
            (tr("stats.sessions"), str(len(user.history)), c["text_on_card"]),
        ]
        for label, value, color in stats:
            cell = QVBoxLayout()
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel(value)
            v.setFont(make_qfont("section_header"))
            v.setStyleSheet(f"color: {color};")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(v)
            l = QLabel(label)
            l.setFont(make_qfont("btn_sm"))
            l.setStyleSheet(f"color: {c['muted']};")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(l)
            stats_row.addLayout(cell)
        cl.addLayout(stats_row)

        # XP progress bar to next level
        cl.addSpacing(10)
        xp_in_level = user.xp % 1000
        bar_row = QHBoxLayout()
        progress = QProgressBar()
        progress.setRange(0, 1000)
        progress.setValue(xp_in_level)
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        progress.setStyleSheet(
            f"QProgressBar {{ background-color: {c['bg']}; "
            f"border: 2px solid transparent; border-radius: 4px; }}"
            f"QProgressBar::chunk {{ background-color: {c['accent']}; "
            f"border-radius: 4px; }}"
        )
        bar_row.addWidget(progress)

        xp_label = QLabel(tr("stats.xp_to_next", current=xp_in_level, level=level + 1))
        xp_label.setFont(make_qfont("btn_sm"))
        xp_label.setStyleSheet(f"color: {c['muted']};")
        bar_row.addWidget(xp_label)
        cl.addLayout(bar_row)

        layout.addWidget(card)
        layout.addSpacing(15)

    # ── Consistency calendar ──

    def _build_consistency(self, layout: QVBoxLayout, user) -> None:
        c = COLORS
        header = QLabel(tr("stats.training_consistency"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        # Extract unique training dates from history
        active_dates: set[str] = set()
        first_date: str | None = None
        for entry in user.history:
            date_part = entry.timestamp[:10]
            if len(date_part) == 10:
                active_dates.add(date_part)
                if first_date is None or date_part < first_date:
                    first_date = date_part

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; "
            f"padding: 12px;"
        )
        cl = QVBoxLayout(card)

        # Summary line
        total_count = len(active_dates)
        summary = QLabel(tr("stats.active_days_total", count=total_count))
        summary.setFont(make_qfont("body"))
        summary.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(summary)
        cl.addSpacing(4)

        # Day-of-week labels (fixed) + scrollable calendar
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Fixed day labels column
        cell, gap = _ConsistencyCalendar.CELL, _ConsistencyCalendar.GAP
        day_col = QWidget()
        day_col.setFixedWidth(22)
        day_col.setFixedHeight(7 * (cell + gap) + 16)
        day_col.setStyleSheet(f"background-color: {c['card']};")
        day_labels_layout = QVBoxLayout(day_col)
        day_labels_layout.setContentsMargins(0, 16, 2, 0)
        day_labels_layout.setSpacing(0)
        for label in ["M", "T", "W", "T", "F", "S", "S"]:
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 7))
            lbl.setStyleSheet(f"color: {c['muted']};")
            lbl.setFixedHeight(cell + gap)
            lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
            day_labels_layout.addWidget(lbl)
        day_labels_layout.addStretch()
        row.addWidget(day_col)

        # Scrollable calendar
        calendar = _ConsistencyCalendar(active_dates, first_date)
        scroll = QScrollArea()
        scroll.setWidget(calendar)
        scroll.setWidgetResizable(False)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setFixedHeight(calendar.height() + 14)
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {c['card']}; border: none; }}"
            f"QScrollBar:horizontal {{ height: 8px; "
            f"background: {c['card']}; border-radius: 4px; }}"
            f"QScrollBar::handle:horizontal {{ background: {c['muted']}; "
            f"border-radius: 4px; min-width: 30px; }}"
            f"QScrollBar::add-line:horizontal, "
            f"QScrollBar::sub-line:horizontal {{ width: 0; }}"
        )
        # Scroll to the right (most recent) after layout is computed
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: scroll.horizontalScrollBar().setValue(
            scroll.horizontalScrollBar().maximum()
        ))
        row.addWidget(scroll, 1)

        cl.addLayout(row)

        layout.addWidget(card)
        layout.addSpacing(15)

    # ── Personal bests ──

    @staticmethod
    def _pb_display(exercise: str, data: dict) -> tuple[str, str]:
        """Return (primary_text, secondary_text) for a personal best entry.

        Chooses exercise-appropriate metrics from stored metadata.
        """
        pct = min(data.get("pct", 0), 100.0)
        score = data.get("score", 0)
        total = data.get("total", 0)
        meta = data.get("metadata", {})

        primary = f"{score}/{total}  ({pct}%)"

        if exercise == "REACTION TIME":
            rt = meta.get("median_rt_ms")
            if rt:
                primary = f"{rt} ms median"
            acc = meta.get("accuracy_pct")
            return primary, f"{acc}% accuracy" if acc is not None else ""

        if exercise == "Schulte Grid":
            t = meta.get("duration_s")
            errs = meta.get("errors", 0)
            if t:
                primary = f"{t}s"
            return primary, f"{errs} error{'s' if errs != 1 else ''}"

        if exercise == "RAPID DECISION":
            t = meta.get("duration_s")
            time_str = f" in {t}s" if t else ""
            primary = f"{score}/{total}{time_str}"
            return primary, f"{pct}% completed"

        # Reading exercises — show WPM when available
        if exercise in ("PACER", "RSVP", "CHUNKING"):
            wpm = meta.get("wpm") or meta.get("wpm_actual")
            secondary = f"{wpm} WPM" if wpm else ""
            primary = f"{score}/{total}  ({pct}%)"
            return primary, secondary

        # Default: accuracy-based exercises
        return primary, ""

    def _build_personal_bests(self, layout: QVBoxLayout, user) -> None:
        if not user.personal_bests:
            return
        c = COLORS
        header = QLabel(tr("dashboard.personal_bests"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(6)

        items = list(user.personal_bests.items())
        cols = 3
        for i, (exercise, data) in enumerate(items):
            row_idx, col_idx = divmod(i, cols)
            cell = QFrame()
            cell.setStyleSheet(
                f"background-color: {c['card']}; border-radius: 4px;"
            )
            cl = QVBoxLayout(cell)
            cl.setContentsMargins(10, 8, 10, 8)
            cl.setSpacing(2)

            # Exercise name
            name_lbl = QLabel(exercise_display_name(exercise))
            name_lbl.setFont(make_qfont("btn_sm"))
            name_lbl.setStyleSheet(f"color: {c['muted']};")
            cl.addWidget(name_lbl)

            # Primary metric
            primary, secondary = self._pb_display(exercise, data)
            primary_lbl = QLabel(primary)
            primary_lbl.setFont(make_qfont("btn_bold"))
            primary_lbl.setStyleSheet(f"color: {c['text_on_card']};")
            cl.addWidget(primary_lbl)

            # Secondary metric (if available)
            if secondary:
                sec_lbl = QLabel(secondary)
                sec_lbl.setFont(make_qfont("body"))
                sec_lbl.setStyleSheet(f"color: {c['muted']};")
                cl.addWidget(sec_lbl)

            grid.addWidget(cell, row_idx, col_idx)

        layout.addLayout(grid)
        layout.addSpacing(15)

    # ── Insights (tiered analytics) ──

    def _build_insights(self, layout: QVBoxLayout, user) -> None:
        if not user.history:
            return
        c = COLORS

        header = QLabel(tr("stats.insights"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        # Parse all scored history entries
        scored: list[tuple[str, str, float]] = []  # (date, exercise, pct)
        by_exercise: dict[str, list[float]] = {}
        for entry in user.history:
            m = re.match(r"(\d+)/(\d+)", entry.result)
            if not m:
                continue
            s, t = int(m.group(1)), int(m.group(2))
            if t == 0:
                continue
            pct = min(s / t * 100, 100.0)
            date_part = entry.timestamp[:10]
            scored.append((date_part, entry.exercise, pct))
            by_exercise.setdefault(entry.exercise, []).append(pct)

        if not scored:
            return

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; "
            f"padding: 16px;"
        )
        cl = QVBoxLayout(card)
        cl.setSpacing(10)

        # ── Immediate: last session vs average ──
        last_date, last_ex, last_pct = scored[0]
        ex_scores = by_exercise.get(last_ex, [last_pct])
        avg = sum(ex_scores) / len(ex_scores)
        diff = last_pct - avg

        last_lbl = QLabel(tr("stats.last_session"))
        last_lbl.setFont(make_qfont("btn_sm"))
        last_lbl.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(last_lbl)

        if diff > 0:
            trend_text = f"▲ {abs(diff):.0f}% above your average"
            trend_color = c["accent"]
        elif diff < -1:
            trend_text = f"▼ {abs(diff):.0f}% below your average"
            trend_color = c["alert"]
        else:
            trend_text = "≈ At your average level"
            trend_color = c["muted"]

        detail = QLabel(
            f"{last_ex}: {last_pct:.0f}%  —  {trend_text}"
        )
        detail.setFont(make_qfont("body"))
        detail.setStyleSheet(f"color: {trend_color};")
        cl.addWidget(detail)

        n_sessions = len(scored)

        # ── Short-term: 7-day comparison (≥5 sessions) ──
        if n_sessions >= 5:
            self._add_separator(cl, c)

            today = datetime.now().date()
            week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            two_weeks = (today - timedelta(days=14)).strftime("%Y-%m-%d")

            this_week = [p for d, _, p in scored if d >= week_ago]
            last_week = [p for d, _, p in scored if two_weeks <= d < week_ago]

            short_lbl = QLabel(tr("stats.7_day_trend"))
            short_lbl.setFont(make_qfont("btn_sm"))
            short_lbl.setStyleSheet(f"color: {c['muted']};")
            cl.addWidget(short_lbl)

            if this_week:
                tw_avg = sum(this_week) / len(this_week)
                parts = [f"This week: {tw_avg:.0f}% avg ({len(this_week)} sessions)"]
                if last_week:
                    lw_avg = sum(last_week) / len(last_week)
                    delta = tw_avg - lw_avg
                    arrow = "▲" if delta > 0 else "▼" if delta < -1 else "≈"
                    parts.append(
                        f"Last week: {lw_avg:.0f}% avg  ({arrow} {abs(delta):.0f}%)"
                    )
                for text in parts:
                    lbl = QLabel(text)
                    lbl.setFont(make_qfont("body"))
                    lbl.setStyleSheet(f"color: {c['text_on_card']};")
                    cl.addWidget(lbl)

        # ── Long-term: strengths/weaknesses (≥20 sessions, ≥14 days) ──
        if n_sessions >= 20:
            dates = {d for d, _, _ in scored}
            if len(dates) >= 7:
                self._add_separator(cl, c)

                long_lbl = QLabel(tr("stats.strengths_weaknesses"))
                long_lbl.setFont(make_qfont("btn_sm"))
                long_lbl.setStyleSheet(f"color: {c['muted']};")
                cl.addWidget(long_lbl)

                # Find strongest and weakest exercises (min 3 attempts)
                qualified = {
                    ex: scores for ex, scores in by_exercise.items()
                    if len(scores) >= 3
                }
                if qualified:
                    avgs = {
                        ex: sum(s) / len(s) for ex, s in qualified.items()
                    }
                    strongest = max(avgs, key=avgs.get)
                    weakest = min(avgs, key=avgs.get)

                    row = QHBoxLayout()
                    for label, ex, color in [
                        ("Strongest", strongest, c["accent"]),
                        ("Weakest", weakest, c["alert"]),
                    ]:
                        cell_l = QVBoxLayout()
                        tag = QLabel(label.upper())
                        tag.setFont(make_qfont("btn_sm"))
                        tag.setStyleSheet(f"color: {c['muted']};")
                        cell_l.addWidget(tag)
                        val = QLabel(f"{exercise_display_name(ex)}  ({avgs[ex]:.0f}%)")
                        val.setFont(make_qfont("btn_bold"))
                        val.setStyleSheet(f"color: {color};")
                        cell_l.addWidget(val)
                        row.addLayout(cell_l)
                    row.addStretch()
                    cl.addLayout(row)

                    # Improvement rates for exercises with ≥5 attempts
                    improving = {}
                    for ex, scores in qualified.items():
                        if len(scores) >= 5:
                            first_half = scores[len(scores)//2:]
                            second_half = scores[:len(scores)//2]
                            early = sum(first_half) / len(first_half)
                            recent = sum(second_half) / len(second_half)
                            improving[ex] = recent - early

                    if improving:
                        most_improved = max(improving, key=improving.get)
                        imp_val = improving[most_improved]
                        if imp_val > 2:
                            imp_lbl = QLabel(
                                f"Most improved: {most_improved} "
                                f"(+{imp_val:.0f}% from early sessions)"
                            )
                            imp_lbl.setFont(make_qfont("body"))
                            imp_lbl.setStyleSheet(f"color: {c['accent']};")
                            cl.addWidget(imp_lbl)

        layout.addWidget(card)
        layout.addSpacing(15)

    @staticmethod
    def _add_separator(layout: QVBoxLayout, c: dict) -> None:
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {c['bg']};")
        layout.addWidget(sep)

    # ── Progress charts ──

    def _build_progress_charts(self, layout: QVBoxLayout, user) -> None:
        if not user.history:
            return
        c = COLORS

        header = QLabel(tr("stats.progress"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        # Group history by exercise, preserving chronological order (oldest first)
        exercises: dict[str, list[tuple[str, float]]] = {}
        for entry in reversed(user.history):
            m = re.match(r"(\d+)/(\d+)", entry.result)
            if not m:
                continue
            score, total = int(m.group(1)), int(m.group(2))
            pct = min(score / total * 100, 100.0) if total > 0 else 0
            exercises.setdefault(entry.exercise, []).append(
                (entry.timestamp, pct)
            )

        if not exercises:
            return

        # Exercise selector buttons with active state tracking
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        self._chart_container = QVBoxLayout()
        self._chart_data = exercises
        self._chart_buttons: list[QPushButton] = []
        self._active_chart: str = ""

        first_key = None
        for ex_name in exercises:
            if first_key is None:
                first_key = ex_name
            btn = QPushButton(exercise_display_name(ex_name))
            btn.setProperty("exercise_key", ex_name)
            btn.setStyleSheet(
                btn_css(c["card"], c["text_on_card"],
                        padding="4px 10px", font_key="btn_sm")
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, name=ex_name: self._show_chart(name)
            )
            self._chart_buttons.append(btn)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addLayout(self._chart_container)
        layout.addSpacing(15)

        if first_key:
            self._show_chart(first_key)

    def _show_chart(self, exercise_name: str) -> None:
        c = COLORS
        self._active_chart = exercise_name

        # Update button styles — highlight active
        for btn in self._chart_buttons:
            if btn.property("exercise_key") == exercise_name:
                btn.setStyleSheet(
                    btn_css(c["accent"], c["btn_text"],
                            padding="4px 10px", font_key="btn_sm")
                )
            else:
                btn.setStyleSheet(
                    btn_css(c["card"], c["text_on_card"],
                            padding="4px 10px", font_key="btn_sm")
                )

        # Clear previous chart
        while self._chart_container.count():
            item = self._chart_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        data = self._chart_data.get(exercise_name, [])
        if not data:
            return

        chart = _ProgressChart(exercise_display_name(exercise_name), data)
        self._chart_container.addWidget(chart)

    # ── History table ──

    def _build_history(self, layout: QVBoxLayout, user) -> None:
        c = COLORS

        # Header row with export buttons inline
        header_row = QHBoxLayout()
        header = QLabel(tr("stats.session_history"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        header_row.addWidget(header)
        header_row.addStretch()

        if user.history:
            count_lbl = QLabel(tr("stats.session_count", count=len(user.history)))
            count_lbl.setFont(make_qfont("body"))
            count_lbl.setStyleSheet(f"color: {c['muted']};")
            header_row.addWidget(count_lbl)

        layout.addLayout(header_row)

        if not user.history:
            lbl = QLabel(tr("stats.no_sessions_yet_start_training"))
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {c['muted']};")
            layout.addWidget(lbl)
            return

        # Alternating row color derived from card
        alt_color = QColor(c["card"])
        alt_color = alt_color.lighter(115) if alt_color.lightness() < 128 else alt_color.darker(108)

        table = QTableWidget(len(user.history), 3)
        table.setHorizontalHeaderLabels(["Time", "Exercise", "Result"])
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setStyleSheet(
            f"QTableWidget {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; border: 2px solid transparent; "
            f"gridline-color: {c['bg']}; {font_css('treeview')} "
            f"alternate-background-color: {alt_color.name()}; }}"
            f"QHeaderView::section {{ background-color: {c['action']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; padding: 6px; "
            f"{font_css('treeview_heading')} }}"
            f"QTableWidget::item {{ padding: 4px 8px; }}"
        )
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

        for i, entry in enumerate(user.history):
            table.setItem(i, 0, QTableWidgetItem(entry.timestamp))
            table.setItem(i, 1, QTableWidgetItem(exercise_display_name(entry.exercise)))
            table.setItem(i, 2, QTableWidgetItem(entry.result))

        table.setMinimumHeight(300)
        layout.addWidget(table)
        layout.addSpacing(15)

    # ── Export ──

    def _build_export(self, layout: QVBoxLayout, user) -> None:
        from PyQt6.QtWidgets import QCheckBox
        c = COLORS
        header = QLabel(tr("stats.export_data"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        desc = QLabel(tr("stats.export_desc"))
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['muted']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(6)

        # Anonymize checkbox
        self._anon_check = QCheckBox(tr("stats.anonymize"))
        self._anon_check.setFont(make_qfont("body"))
        self._anon_check.setStyleSheet(
            f"QCheckBox {{ color: {c['fg']}; spacing: 8px; }}"
            f"QCheckBox::indicator {{ width: 18px; height: 18px; "
            f"border: 2px solid {c['muted']}; border-radius: 3px; "
            f"background: {c['card']}; }}"
            f"QCheckBox::indicator:checked {{ background: {c['accent']}; "
            f"border-color: {c['accent']}; }}"
        )
        layout.addWidget(self._anon_check)

        layout.addSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(8)
        for text, cb in [
            (tr("stats.export_csv"), lambda: self._export_csv(user)),
            (tr("stats.export_json"), lambda: self._export_json(user)),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                btn_css(c["action"], c["btn_text"],
                        padding="6px 20px", font_key="btn_sm")
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(cb)
            row.addWidget(btn)
        row.addStretch()
        layout.addLayout(row)

    def _export_name(self, user) -> str:
        """Return display name or anonymized participant ID."""
        if self._anon_check.isChecked():
            import hashlib
            h = hashlib.sha256(user.name.encode()).hexdigest()[:8]
            return f"P-{h.upper()}"
        return user.name

    @staticmethod
    def _collect_metadata_keys(history) -> list[str]:
        """Gather all unique metadata keys across history entries."""
        keys: dict[str, None] = {}
        for entry in history:
            if entry.metadata:
                for k in entry.metadata:
                    keys[k] = None
        return list(keys)

    def _export_csv(self, user) -> None:
        if not user.history:
            QMessageBox.information(
                self, tr("stats.no_data"), tr("stats.no_data_to_export")
            )
            return
        name = self._export_name(user)
        default_name = f"nsa_{name}_{datetime.now():%Y%m%d}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("stats.export_csv"), default_name, "CSV files (*.csv)"
        )
        if not path:
            return
        try:
            meta_keys = self._collect_metadata_keys(user.history)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Header
                writer.writerow(
                    ["Participant", "Timestamp", "Exercise", "Result"]
                    + [f"meta_{k}" for k in meta_keys]
                )
                for entry in user.history:
                    row = [name, entry.timestamp, entry.exercise, entry.result]
                    for k in meta_keys:
                        val = entry.metadata.get(k, "") if entry.metadata else ""
                        row.append(val)
                    writer.writerow(row)

                # Personal bests sheet
                if user.personal_bests:
                    writer.writerow([])
                    writer.writerow(["Personal Bests"])
                    writer.writerow([
                        "Exercise", "Score", "Total", "Percentage", "Date",
                    ])
                    for exercise, data in user.personal_bests.items():
                        writer.writerow([
                            exercise, data["score"], data["total"],
                            f"{data['pct']}%", data.get("date", ""),
                        ])

                # Summary
                writer.writerow([])
                writer.writerow(["Summary"])
                writer.writerow(["Participant", name])
                writer.writerow(["Total XP", user.xp])
                writer.writerow(["Level", user.xp // 1000 + 1])
                writer.writerow(["Sessions", len(user.history)])
                writer.writerow(["Exported", datetime.now().isoformat()])

            QMessageBox.information(
                self, tr("stats.exported"),
                tr("stats.exported_msg",
                   file=os.path.basename(path),
                   sessions=len(user.history),
                   fields=len(meta_keys)),
            )
        except OSError as e:
            QMessageBox.critical(
                self, tr("stats.export_error"), tr("stats.export_error_msg", error=e)
            )

    def _export_json(self, user) -> None:
        name = self._export_name(user)
        default_name = f"nsa_{name}_{datetime.now():%Y%m%d}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("stats.export_json"), default_name, "JSON files (*.json)"
        )
        if not path:
            return
        try:
            data = {
                "participant": name,
                "xp": user.xp,
                "level": user.xp // 1000 + 1,
                "streak": user.streak,
                "sessions": len(user.history),
                "personal_bests": user.personal_bests,
                "history": [
                    {
                        "timestamp": e.timestamp,
                        "exercise": e.exercise,
                        "result": e.result,
                        "metadata": e.metadata if e.metadata else {},
                    }
                    for e in user.history
                ],
                "exported_at": datetime.now().isoformat(),
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self, tr("stats.exported"),
                tr("stats.exported_json_msg",
                   file=os.path.basename(path),
                   sessions=len(user.history)),
            )
        except OSError as e:
            QMessageBox.critical(
                self, tr("stats.export_error"), tr("stats.export_error_msg", error=e)
            )
