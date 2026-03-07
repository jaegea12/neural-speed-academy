"""
JSON file-based implementation of UserRepository.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

from neural_speed_academy.config import USER_DATA_CONFIG
from neural_speed_academy.state import UserProfile
from neural_speed_academy.repositories.base import UserRepositoryInterface

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass


class DataCorruptionError(RepositoryError):
    """Raised when stored data cannot be parsed."""
    pass


class StorageError(RepositoryError):
    """Raised when file operations fail."""
    pass


class JsonUserRepository(UserRepositoryInterface):
    """
    Persists user profiles to a JSON file.
    Each user is stored as a key in the root object.
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or USER_DATA_CONFIG["file_name"]

    def _load_all(self) -> dict:
        """Load all data from the JSON file."""
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.error(f"Invalid data format in {self.file_path}: expected dict")
                    raise DataCorruptionError(f"Invalid data format: expected dict, got {type(data)}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in {self.file_path}: {e}")
            # Attempt recovery by backing up corrupted file
            self._backup_corrupted_file()
            return {}
        except IOError as e:
            logger.error(f"Failed to read {self.file_path}: {e}")
            raise StorageError(f"Cannot read user data: {e}") from e

    def _save_all(self, data: dict) -> None:
        """Save all data to the JSON file."""
        try:
            # Write to temp file first, then rename for atomicity
            temp_path = f"{self.file_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(temp_path, self.file_path)
        except IOError as e:
            logger.error(f"Failed to save user data: {e}")
            raise StorageError(f"Cannot save user data: {e}") from e

    def _backup_corrupted_file(self) -> None:
        """Backup a corrupted data file for recovery."""
        if os.path.exists(self.file_path):
            backup_path = f"{self.file_path}.corrupted"
            try:
                os.rename(self.file_path, backup_path)
                logger.info(f"Backed up corrupted file to {backup_path}")
            except IOError as e:
                logger.warning(f"Could not backup corrupted file: {e}")

    def get(self, name: str) -> Optional[UserProfile]:
        """Retrieve a user profile by name."""
        data = self._load_all()
        if name not in data:
            return None
        return UserProfile.from_dict(data[name])

    def save(self, user: UserProfile) -> None:
        """Save or update a user profile."""
        data = self._load_all()
        data[user.name] = user.to_dict()
        self._save_all(data)

    def exists(self, name: str) -> bool:
        """Check if a user exists."""
        data = self._load_all()
        return name in data

    def delete(self, name: str) -> bool:
        """Delete a user profile."""
        data = self._load_all()
        if name not in data:
            return False
        del data[name]
        self._save_all(data)
        return True

    def list_users(self) -> list[str]:
        """Return a list of all user names."""
        data = self._load_all()
        return list(data.keys())

    def get_or_create(self, name: str) -> UserProfile:
        """
        Get existing user or create a new one.
        Convenience method for login flow.
        """
        user = self.get(name)
        if user is None:
            user = UserProfile(name=name)
            self.save(user)
        return user

    def add_history(self, name: str, exercise: str, result: str) -> None:
        """
        Add a history entry for a user.
        Convenience method that handles load/save cycle.
        """
        user = self.get(name)
        if user is None:
            logger.warning(f"Cannot add history: user '{name}' not found")
            return
        user.add_history(
            exercise=exercise,
            result=result,
            max_entries=USER_DATA_CONFIG["max_history_entries"],
        )
        self.save(user)

    def add_xp(self, name: str, amount: int) -> None:
        """
        Add XP to a user.
        Convenience method that handles load/save cycle.
        """
        user = self.get(name)
        if user is None:
            logger.warning(f"Cannot add XP: user '{name}' not found")
            return
        user.add_xp(amount)
        self.save(user)
