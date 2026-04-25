"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

import csv
import json
import os
import re
from datetime import date, datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QSizePolicy, QGridLayout, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css, _UI_FONT
from neural_speed_academy.i18n import tr, exercise_display_name


class _ConsistencyCalendar(QWidget):
    """Traditional calendar grid showing training days.

    Displays the last 3 months as side-by-side mini calendars with
    weekday headers, day numbers, grid lines, and highlighted active days.
    """

    CELL = 22
    MONTHS = 3

    def __init__(
        self, active_dates: set[str],
        first_date: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._active = active_dates
        self._today = datetime.now().date()

        # Build list of months to display (current + previous N-1)
        self._months: list[date] = []
        cur = self._today.replace(day=1)
        for _ in range(self.MONTHS):
            self._months.insert(0, cur)
            cur = (cur - timedelta(days=1)).replace(day=1)

        cell = self.CELL
        header_h = 16   # month name
        dow_h = 14       # weekday row
        gap = 14         # between months
        month_w = 7 * cell
        total_w = self.MONTHS * month_w + (self.MONTHS - 1) * gap
        # Max 6 week-rows per month
        grid_h = 6 * cell
        total_h = header_h + dow_h + grid_h + 4
        self.setFixedSize(max(total_w, 200), total_h)

    def paintEvent(self, event) -> None:
        c = COLORS
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cell = self.CELL
        header_h = 16
        dow_h = 14
        gap = 14
        month_w = 7 * cell

        active_color = QColor(c["accent"])
        grid_color = QColor(c["muted"])
        grid_color.setAlpha(50)
        today_border = QColor(c["accent"])

        dow_labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

        for mi, month_start in enumerate(self._months):
            ox = mi * (month_w + gap)

            # Month + year label
            font_header = QFont(_UI_FONT, 9)
            font_header.setBold(True)
            painter.setFont(font_header)
            painter.setPen(QColor(c["fg"]))
            label = month_start.strftime("%B %Y")
            painter.drawText(ox, 0, month_w, header_h,
                             Qt.AlignmentFlag.AlignCenter, label)

            # Weekday headers
            font_dow = QFont(_UI_FONT, 7)
            painter.setFont(font_dow)
            painter.setPen(QColor(c["muted"]))
            for d, lbl in enumerate(dow_labels):
                x = ox + d * cell
                painter.drawText(x, header_h, cell, dow_h,
                                 Qt.AlignmentFlag.AlignCenter, lbl)

            # Grid top
            grid_top = header_h + dow_h

            # Days in this month
            import calendar as cal_mod
            _, days_in_month = cal_mod.monthrange(
                month_start.year, month_start.month
            )
            first_dow = month_start.weekday()  # 0=Mon

            font_day = QFont(_UI_FONT, 8)
            painter.setFont(font_day)

            for day_num in range(1, days_in_month + 1):
                d = date(month_start.year, month_start.month, day_num)
                col = (first_dow + day_num - 1) % 7
                row = (first_dow + day_num - 1) // 7
                x = ox + col * cell
                y = grid_top + row * cell

                day_str = d.strftime("%Y-%m-%d")
                is_active = day_str in self._active
                is_today = d == self._today
                is_future = d > self._today

                # Cell background
                if is_active:
                    painter.setBrush(active_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(x, y, cell, cell)
                else:
                    painter.setBrush(Qt.BrushStyle.NoBrush)

                # Grid lines
                painter.setPen(QPen(grid_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(x, y, cell, cell)

                # Today ring
                if is_today:
                    painter.setPen(QPen(today_border, 2))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawRect(x + 1, y + 1, cell - 2, cell - 2)

                # Day number
                if is_future:
                    painter.setPen(QColor(c["muted"]))
                elif is_active:
                    painter.setPen(QColor(c["btn_text"]))
                else:
                    painter.setPen(QColor(c["fg"]))
                painter.drawText(x, y, cell, cell,
                                 Qt.AlignmentFlag.AlignCenter,
                                 str(day_num))

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
        painter.setFont(QFont(_UI_FONT, 11, QFont.Weight.Bold))
        painter.drawText(margin_l, 20, self._title)

        if len(self._data) < 2:
            painter.setPen(QColor(c["muted"]))
            painter.setFont(QFont(_UI_FONT, 10))
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
        painter.setFont(QFont(_UI_FONT, 8))
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
        painter.setFont(QFont(_UI_FONT, 8))
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

        # Calendar widget (weekday labels are drawn inside)
        calendar = _ConsistencyCalendar(active_dates, first_date)
        cl.addWidget(calendar, alignment=Qt.AlignmentFlag.AlignCenter)

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
        # #osx — native file dialog may not pre-fill the filename on
        # some macOS versions; user sees an empty save field.
        # #linux — on Wayland the dialog may appear behind the main
        # window if the compositor doesn't handle transient windows.
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
