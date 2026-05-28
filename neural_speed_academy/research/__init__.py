"""
Research data standards and export utilities for Neural Speed Academy.

This module provides tools for standardizing exercise data, anonymizing
user information, and exporting datasets for research partnerships.

Key components:
- schemas: Pydantic models for research-grade data validation
- exporters: CSV, JSON export with validation
- anonymizer: UUID generation, age binning, consent tracking
- consent_manager: Research opt-in tracking and withdrawal
"""

__version__ = "1.0.0"

from .schemas import (
    ResearchMetadata,
    ParticipantInfo,
    SessionMetadata,
    ExerciseResult,
    ResearchDataset,
)
from .anonymizer import AnonymityManager
from .consent_manager import ConsentManager

__all__ = [
    "ResearchMetadata",
    "ParticipantInfo",
    "SessionMetadata",
    "ExerciseResult",
    "ResearchDataset",
    "AnonymityManager",
    "ConsentManager",
]
