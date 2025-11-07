"""Custom data structures used by the social network app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar


T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """Node for a singly linked list."""

    value: T
    next: Optional["Node[T]"] = None


class LinkedList(Generic[T]):
    """Simple singly linked list with append and iteration support."""

    def __init__(self, values: Optional[Iterable[T]] = None) -> None:
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None
        self._length = 0
        if values is not None:
            for value in values:
                self.append(value)

    def append(self, value: T) -> None:
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._length += 1

    def __len__(self) -> int:  # pragma: no cover - trivial
        return self._length

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self._length = 0

    def to_list(self) -> list[T]:
        return list(iter(self))
