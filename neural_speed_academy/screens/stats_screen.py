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
    QSizePolicy, QGridLayout, QProgressBar,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css


class _ConsistencyCalendar(QWidget):
    """GitHub-style heatmap showing training activity over the last 12 weeks."""

    WEEKS = 12
    CELL = 14
    GAP = 3

    def __init__(
        self, active_dates: set[str],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._active = active_dates  # set of "YYYY-MM-DD" strings
        total_w = self.WEEKS * (self.CELL + self.GAP) + 40  # +40 for day labels
        total_h = 7 * (self.CELL + self.GAP) + 25  # +25 for month labels
        self.setFixedHeight(total_h)
        self.setMinimumWidth(total_w)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

    def paintEvent(self, event) -> None:
        c = COLORS
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cell, gap = self.CELL, self.GAP
        label_w = 30  # space for day-of-week labels
        month_h = 18  # space for month labels at top

        # Compute date grid: 12 weeks ending today
        today = datetime.now().date()
        # Start from the Monday of (today - 11 weeks)
        start = today - timedelta(days=today.weekday()) - timedelta(weeks=self.WEEKS - 1)

        # Draw month labels
        painter.setPen(QColor(c["muted"]))
        painter.setFont(QFont("Segoe UI", 8))
        prev_month = -1
        for week in range(self.WEEKS):
            day = start + timedelta(weeks=week)
            if day.month != prev_month:
                x = label_w + week * (cell + gap)
                painter.drawText(x, 12, day.strftime("%b"))
                prev_month = day.month

        # Draw day-of-week labels (Mon, Wed, Fri)
        day_labels = {0: "M", 2: "W", 4: "F"}
        for dow, label in day_labels.items():
            y = month_h + dow * (cell + gap) + cell - 2
            painter.drawText(2, y, label)

        # Draw cells
        empty_color = QColor(c["card"])
        active_color = QColor(c["accent"])
        # Intermediate intensity for days with fewer sessions
        mid_color = QColor(c["accent"])
        mid_color.setAlpha(100)

        for week in range(self.WEEKS):
            for dow in range(7):
                day = start + timedelta(weeks=week, days=dow)
                if day > today:
                    continue
                x = label_w + week * (cell + gap)
                y = month_h + dow * (cell + gap)

                day_str = day.strftime("%Y-%m-%d")
                if day_str in self._active:
                    painter.setBrush(active_color)
                else:
                    painter.setBrush(empty_color)

                painter.setPen(Qt.PenStyle.NoPen)
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

        title = QLabel("PERFORMANCE ANALYTICS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(15)

        self._build_summary(cl, user)
        self._build_consistency(cl, user)
        self._build_personal_bests(cl, user)
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
            ("TOTAL XP", str(user.xp), c["accent"]),
            ("LEVEL", str(level), c["action"]),
            ("STREAK", f"{user.streak} day{'s' if user.streak != 1 else ''}", c["highlight"]),
            ("SESSIONS", str(len(user.history)), c["text_on_card"]),
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
            f"border: none; border-radius: 4px; }}"
            f"QProgressBar::chunk {{ background-color: {c['accent']}; "
            f"border-radius: 4px; }}"
        )
        bar_row.addWidget(progress)

        xp_label = QLabel(f"{xp_in_level}/1000 XP to Level {level + 1}")
        xp_label.setFont(make_qfont("btn_sm"))
        xp_label.setStyleSheet(f"color: {c['muted']};")
        bar_row.addWidget(xp_label)
        cl.addLayout(bar_row)

        layout.addWidget(card)
        layout.addSpacing(15)

    # ── Consistency calendar ──

    def _build_consistency(self, layout: QVBoxLayout, user) -> None:
        c = COLORS
        header = QLabel("TRAINING CONSISTENCY")
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        # Extract unique training dates from history
        active_dates: set[str] = set()
        for entry in user.history:
            # Timestamps are "YYYY-MM-DD HH:MM"
            date_part = entry.timestamp[:10]
            if len(date_part) == 10:
                active_dates.add(date_part)

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; "
            f"padding: 12px;"
        )
        cl = QVBoxLayout(card)

        # Summary line
        today = datetime.now().date()
        start = today - timedelta(weeks=12)
        recent_count = sum(
            1 for d in active_dates
            if d >= start.strftime("%Y-%m-%d")
        )
        total_days = (today - start).days + 1
        pct = round(recent_count / total_days * 100) if total_days else 0
        summary = QLabel(
            f"{recent_count} active days in the last 12 weeks ({pct}%)"
        )
        summary.setFont(make_qfont("body"))
        summary.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(summary)
        cl.addSpacing(4)

        calendar = _ConsistencyCalendar(active_dates)
        cl.addWidget(calendar)

        layout.addWidget(card)
        layout.addSpacing(15)

    # ── Personal bests ──

    def _build_personal_bests(self, layout: QVBoxLayout, user) -> None:
        if not user.personal_bests:
            return
        c = COLORS
        header = QLabel("PERSONAL BESTS")
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
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(10, 6, 10, 6)
            cl.setSpacing(8)

            name_lbl = QLabel(exercise)
            name_lbl.setFont(make_qfont("btn_sm"))
            name_lbl.setStyleSheet(f"color: {c['muted']};")
            cl.addWidget(name_lbl)

            cl.addStretch()

            score_lbl = QLabel(
                f"{data['score']}/{data['total']}  ({data['pct']}%)"
            )
            score_lbl.setFont(make_qfont("btn_bold"))
            score_lbl.setStyleSheet(f"color: {c['text_on_card']};")
            cl.addWidget(score_lbl)

            grid.addWidget(cell, row_idx, col_idx)

        layout.addLayout(grid)
        layout.addSpacing(15)

    # ── Progress charts ──

    def _build_progress_charts(self, layout: QVBoxLayout, user) -> None:
        if not user.history:
            return
        c = COLORS

        header = QLabel("PROGRESS")
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
            pct = (score / total * 100) if total > 0 else 0
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
            btn = QPushButton(ex_name)
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
            if btn.text() == exercise_name:
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

        chart = _ProgressChart(exercise_name, data)
        self._chart_container.addWidget(chart)

    # ── History table ──

    def _build_history(self, layout: QVBoxLayout, user) -> None:
        c = COLORS

        # Header row with export buttons inline
        header_row = QHBoxLayout()
        header = QLabel("SESSION HISTORY")
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        header_row.addWidget(header)
        header_row.addStretch()

        if user.history:
            count_lbl = QLabel(f"{len(user.history)} sessions")
            count_lbl.setFont(make_qfont("body"))
            count_lbl.setStyleSheet(f"color: {c['muted']};")
            header_row.addWidget(count_lbl)

        layout.addLayout(header_row)

        if not user.history:
            lbl = QLabel("No sessions yet. Start training!")
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
            f"color: {c['text_on_card']}; border: none; "
            f"gridline-color: {c['bg']}; {font_css('treeview')} "
            f"alternate-background-color: {alt_color.name()}; }}"
            f"QHeaderView::section {{ background-color: {c['action']}; "
            f"color: {c['btn_text']}; border: none; padding: 6px; "
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
            table.setItem(i, 1, QTableWidgetItem(entry.exercise))
            table.setItem(i, 2, QTableWidgetItem(entry.result))

        table.setMinimumHeight(300)
        layout.addWidget(table)
        layout.addSpacing(15)

    # ── Export ──

    def _build_export(self, layout: QVBoxLayout, user) -> None:
        c = COLORS
        header = QLabel("EXPORT DATA")
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        row = QHBoxLayout()
        row.setSpacing(8)
        for text, cb in [
            ("EXPORT CSV", lambda: self._export_csv(user)),
            ("EXPORT JSON", lambda: self._export_json(user)),
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

    def _export_csv(self, user) -> None:
        if not user.history:
            QMessageBox.information(
                self, "No Data", "No session history to export."
            )
            return
        default_name = f"nsa_{user.name}_{datetime.now():%Y%m%d}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_name, "CSV files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Exercise", "Result"])
                for entry in user.history:
                    writer.writerow([
                        entry.timestamp, entry.exercise, entry.result,
                    ])
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
            QMessageBox.information(
                self, "Exported",
                f"Data saved to:\n{os.path.basename(path)}",
            )
        except OSError as e:
            QMessageBox.critical(
                self, "Export Error", f"Could not save file:\n{e}"
            )

    def _export_json(self, user) -> None:
        default_name = f"nsa_{user.name}_{datetime.now():%Y%m%d}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", default_name, "JSON files (*.json)"
        )
        if not path:
            return
        try:
            data = {
                "name": user.name,
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
                    }
                    for e in user.history
                ],
                "exported_at": datetime.now().isoformat(),
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self, "Exported",
                f"Data saved to:\n{os.path.basename(path)}",
            )
        except OSError as e:
            QMessageBox.critical(
                self, "Export Error", f"Could not save file:\n{e}"
            )
