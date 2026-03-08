"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css


class StatsScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        user = self.navigator.get_user()
        if not user:
            lbl = QLabel("No user logged in")
            lbl.setFont(make_qfont("header"))
            lbl.setStyleSheet(f"color: {c['alert']};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(lbl, 1)
            return

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(50, 20, 50, 30)

        title = QLabel("PERFORMANCE ANALYTICS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(15)

        self._build_summary(cl, user)
        self._build_personal_bests(cl, user)
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
            btn.setFont(make_qfont("btn_bold"))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['action']}; "
                f"color: {c['btn_text']}; border: none; "
                f"padding: 6px 20px; border-radius: 4px; }}"
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
