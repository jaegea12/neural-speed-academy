"""
JSON file-based storage for custom slide sets.

Each slide set is stored as a separate .json file in the
nsa_slide_sets/ directory. Files are portable and can be
shared via import/export.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

SLIDE_SETS_DIR = "nsa_slide_sets"


@dataclass
class SlideQuestion:
    text: str
    choices: list[str]
    answer: int  # index into choices

    def to_tuple(self) -> tuple:
        """Convert to the (text, choices, correct_idx) format used by the exercise."""
        return (self.text, list(self.choices), self.answer)

    @classmethod
    def from_dict(cls, d: dict) -> SlideQuestion:
        return cls(
            text=d["text"],
            choices=list(d["choices"]),
            answer=int(d["answer"]),
        )

    def to_dict(self) -> dict:
        return {"text": self.text, "choices": self.choices, "answer": self.answer}


@dataclass
class Slide:
    title: str
    bullets: list[str]
    questions: list[SlideQuestion] = field(default_factory=list)

    def to_tuple(self) -> tuple:
        """Convert to the (title, bullets, questions) format used by the exercise."""
        return (self.title, list(self.bullets), [q.to_tuple() for q in self.questions])

    @classmethod
    def from_dict(cls, d: dict) -> Slide:
        return cls(
            title=d["title"],
            bullets=list(d["bullets"]),
            questions=[SlideQuestion.from_dict(q) for q in d.get("questions", [])],
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "bullets": self.bullets,
            "questions": [q.to_dict() for q in self.questions],
        }


@dataclass
class SlideSet:
    name: str
    category: str = "custom"
    slides: list[Slide] = field(default_factory=list)
    filename: str = ""  # set on load/save

    @classmethod
    def from_dict(cls, d: dict, filename: str = "") -> SlideSet:
        return cls(
            name=d["name"],
            category=d.get("category", "custom"),
            slides=[Slide.from_dict(s) for s in d.get("slides", [])],
            filename=filename,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "slides": [s.to_dict() for s in self.slides],
        }

    def to_library_format(self) -> list[tuple]:
        """Convert to the list-of-tuples format used by SLIDE_LIBRARY."""
        return [s.to_tuple() for s in self.slides]


def _safe_filename(name: str) -> str:
    """Convert a slide set name to a safe filename."""
    safe = re.sub(r"[^\w\s-]", "", name.lower())
    safe = re.sub(r"[\s]+", "_", safe.strip())
    return safe or "untitled"


class SlideSetRepository:
    """Manages custom slide sets stored as JSON files."""

    def __init__(self, directory: str = SLIDE_SETS_DIR):
        self._dir = directory

    def _ensure_dir(self) -> None:
        os.makedirs(self._dir, exist_ok=True)

    def list_sets(self) -> list[SlideSet]:
        """Load all slide sets from disk."""
        self._ensure_dir()
        sets: list[SlideSet] = []
        for fname in sorted(os.listdir(self._dir)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(self._dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ss = SlideSet.from_dict(data, filename=fname)
                sets.append(ss)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning("Skipping invalid slide set %s: %s", fname, e)
        return sets

    def save_set(self, slide_set: SlideSet) -> str:
        """Save a slide set to disk. Returns the filename used."""
        self._ensure_dir()
        if not slide_set.filename:
            base = _safe_filename(slide_set.name)
            fname = f"{base}.json"
            # Avoid collisions
            counter = 1
            while os.path.exists(os.path.join(self._dir, fname)):
                fname = f"{base}_{counter}.json"
                counter += 1
            slide_set.filename = fname

        path = os.path.join(self._dir, slide_set.filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(slide_set.to_dict(), f, indent=2, ensure_ascii=False)
        return slide_set.filename

    def delete_set(self, slide_set: SlideSet) -> None:
        """Delete a slide set file from disk."""
        if not slide_set.filename:
            return
        path = os.path.join(self._dir, slide_set.filename)
        if os.path.exists(path):
            os.remove(path)

    def import_file(self, file_path: str) -> SlideSet:
        """Import a slide set from an external JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ss = SlideSet.from_dict(data)
        ss.filename = ""  # force new filename on save
        self.save_set(ss)
        return ss

    def export_file(self, slide_set: SlideSet, dest_path: str) -> None:
        """Export a slide set to an external JSON file."""
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(slide_set.to_dict(), f, indent=2, ensure_ascii=False)
