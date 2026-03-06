"""
Abstract base classes for repository pattern.
Enables swapping storage backends (JSON, SQLite, cloud) without changing application code.
"""

from abc import ABC, abstractmethod
from typing import Optional

from neural_speed_academy.state import UserProfile


class UserRepositoryInterface(ABC):
    """Interface for user data persistence."""

    @abstractmethod
    def get(self, name: str) -> Optional[UserProfile]:
        """
        Retrieve a user profile by name.
        Returns None if user doesn't exist.
        """
        pass

    @abstractmethod
    def save(self, user: UserProfile) -> None:
        """Save or update a user profile."""
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if a user exists."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """
        Delete a user profile.
        Returns True if deleted, False if user didn't exist.
        """
        pass

    @abstractmethod
    def list_users(self) -> list[str]:
        """Return a list of all user names."""
        pass
