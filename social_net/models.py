"""Data models for the social network."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Set

from .data_structures import LinkedList


@dataclass
class Comment:
    author: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def short(self) -> str:
        return f"{self.author}: {self.content[:30]}" + ("..." if len(self.content) > 30 else "")


@dataclass
class Post:
    post_id: int
    author: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    likes: Set[str] = field(default_factory=set)
    comments: List[Comment] = field(default_factory=list)

    @property
    def priority(self) -> int:
        """Score used for the priority queue (likes are weighted more)."""

        return len(self.likes) * 3 + len(self.comments)

    def summary(self) -> str:
        snippet = self.content[:70] + ("..." if len(self.content) > 70 else "")
        return f"{self.author}: {snippet}"


@dataclass
class User:
    username: str
    full_name: str
    bio: str = ""
    friends: Set[str] = field(default_factory=set)
    posts: LinkedList[Post] = field(default_factory=LinkedList)
    notifications: Deque[str] = field(default_factory=deque)
    liked_posts: Set[int] = field(default_factory=set)

    def add_notification(self, message: str) -> None:
        self.notifications.append(message)

    def pop_notifications(self) -> List[str]:
        messages = list(self.notifications)
        self.notifications.clear()
        return messages
