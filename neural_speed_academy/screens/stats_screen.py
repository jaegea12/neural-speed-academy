"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css


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
        cl.setContentsMargins(20, 20, 20, 30)

        title = QLabel("PERFORMANCE ANALYTICS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(15)

        self._build_summary(cl, user)
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
        cl = QHBoxLayout(card)

        stats = [
            ("TOTAL XP", str(user.xp)),
            ("LEVEL", str(user.xp // 1000 + 1)),
            ("STREAK", f"{user.streak} day{'s' if user.streak != 1 else ''}"),
            ("SESSIONS", str(len(user.history))),
        ]
        for label, value in stats:
            cell = QVBoxLayout()
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel(value)
            v.setFont(make_qfont("sub"))
            v.setStyleSheet(f"color: {c['accent']};")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(v)
            l = QLabel(label)
            l.setFont(make_qfont("btn_sm"))
            l.setStyleSheet(f"color: {c['muted']};")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(l)
            cl.addLayout(cell)

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

        row = QHBoxLayout()
        for exercise, data in user.personal_bests.items():
            cell = QFrame()
            cell.setStyleSheet(
                f"background-color: {c['card']}; border-radius: 4px; "
                f"padding: 10px 14px;"
            )
            cl = QVBoxLayout(cell)
            cl.setSpacing(2)
            for text, font_key, color in [
                (exercise, "btn_sm", c["muted"]),
                (f"{data['score']}/{data['total']}", "sub", c["text_on_card"]),
                (f"{data['pct']}%", "btn_sm", c["accent"]),
                (data.get("date", ""), "btn_sm", c["muted"]),
            ]:
                lbl = QLabel(text)
                lbl.setFont(make_qfont(font_key))
                lbl.setStyleSheet(f"color: {color};")
                cl.addWidget(lbl)
            row.addWidget(cell)
        row.addStretch()
        layout.addLayout(row)
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

        # Exercise selector buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self._chart_container = QVBoxLayout()
        self._chart_data = exercises

        first_key = None
        for ex_name in exercises:
            if first_key is None:
                first_key = ex_name
            btn = QPushButton(ex_name)
            btn.setStyleSheet(
                btn_css(c["card"], c["text_on_card"],
                        padding="6px 14px", font_key="btn_sm")
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, name=ex_name: self._show_chart(name)
            )
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addLayout(self._chart_container)
        layout.addSpacing(15)

        # Show first exercise chart by default
        if first_key:
            self._show_chart(first_key)

    def _show_chart(self, exercise_name: str) -> None:
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
        header = QLabel("SESSION HISTORY")
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['fg']};")
        layout.addWidget(header)

        if not user.history:
            lbl = QLabel("No sessions yet. Start training!")
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {c['muted']};")
            layout.addWidget(lbl)
            return

        table = QTableWidget(len(user.history), 3)
        table.setHorizontalHeaderLabels(["Time", "Exercise", "Result"])
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setStyleSheet(
            f"QTableWidget {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; border: none; "
            f"gridline-color: {c['bg']}; {font_css('treeview')} }}"
            f"QHeaderView::section {{ background-color: {c['action']}; "
            f"color: {c['btn_text']}; border: none; padding: 4px; "
            f"{font_css('treeview_heading')} }}"
        )
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)

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
        for text, cb in [
            ("EXPORT CSV", lambda: self._export_csv(user)),
            ("EXPORT JSON", lambda: self._export_json(user)),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                btn_css(c["action"], c["btn_text"], padding="6px 20px")
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
