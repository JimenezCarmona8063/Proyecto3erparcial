"""Core logic for the social network."""

from __future__ import annotations

import heapq
from datetime import datetime
from typing import Dict, List

from .data_structures import LinkedList
from .models import Comment, Post, User
from .search import kmp_search, search_collection


class SocialNetwork:
    """High level API to manage users, posts and interactions."""

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.posts_by_id: Dict[int, Post] = {}
        self._post_sequence = 1
        self._post_heap: list[tuple[int, int]] = []  # (-priority, post_id)

    # -- User management -------------------------------------------------

    def add_user(self, username: str, full_name: str, bio: str = "") -> User:
        if username in self.users:
            raise ValueError(f"El usuario '{username}' ya existe")
        user = User(username=username, full_name=full_name, bio=bio)
        self.users[username] = user
        return user

    def search_users(self, term: str) -> list[User]:
        return [self.users[name] for name in search_collection(self.users.keys(), term)]

    # -- Friend connections ----------------------------------------------

    def add_friend(self, username: str, friend_username: str) -> None:
        user = self._require_user(username)
        friend = self._require_user(friend_username)
        if username == friend_username:
            raise ValueError("No puedes agregarte a ti mismo como amigo")
        if friend_username in user.friends:
            raise ValueError(f"{friend_username} ya es amigo de {username}")
        user.friends.add(friend_username)
        friend.friends.add(username)
        friend.add_notification(f"{user.full_name} te agregó como amigo")

    # -- Posts -----------------------------------------------------------

    def create_post(self, username: str, content: str) -> Post:
        user = self._require_user(username)
        post = Post(post_id=self._post_sequence, author=username, content=content)
        self._post_sequence += 1
        user.posts.append(post)
        self.posts_by_id[post.post_id] = post
        self._push_post(post)
        self._notify_friends(user, f"{user.full_name} publicó algo nuevo")
        return post

    def like_post(self, username: str, post_id: int) -> None:
        user = self._require_user(username)
        post = self._require_post(post_id)
        if post_id in user.liked_posts:
            raise ValueError("Ya marcaste 'me gusta' en esta publicación")
        post.likes.add(username)
        user.liked_posts.add(post_id)
        self._push_post(post)
        self._notify_user(post.author, f"A {user.full_name} le gustó tu publicación #{post_id}")

    def comment_post(self, username: str, post_id: int, content: str) -> Comment:
        user = self._require_user(username)
        post = self._require_post(post_id)
        comment = Comment(author=username, content=content, timestamp=datetime.utcnow())
        post.comments.append(comment)
        self._push_post(post)
        self._notify_user(post.author, f"{user.full_name} comentó tu publicación #{post_id}")
        return comment

    def get_user_posts(self, username: str) -> LinkedList[Post]:
        return self._require_user(username).posts

    def get_top_posts(self, limit: int = 5) -> List[Post]:
        seen = set()
        result: List[Post] = []
        temp: list[tuple[int, int]] = []
        while self._post_heap and len(result) < limit:
            priority, post_id = heapq.heappop(self._post_heap)
            if post_id in seen:
                continue
            post = self.posts_by_id.get(post_id)
            if not post:
                continue
            # Reinsert to maintain heap updated with new priority
            heapq.heappush(temp, (priority, post_id))
            result.append(post)
            seen.add(post_id)
        for item in temp:
            heapq.heappush(self._post_heap, item)
        return result

    def search_posts(self, term: str) -> List[Post]:
        ids = search_collection((str(post_id) for post_id in self.posts_by_id), term)
        matches = [self.posts_by_id[int(post_id)] for post_id in ids if int(post_id) in self.posts_by_id]
        lowered = term.lower()
        content_matches = [post for post in self.posts_by_id.values() if kmp_search(post.content.lower(), lowered)]
        result = {post.post_id: post for post in matches + content_matches}
        return list(result.values())

    # -- Notifications ---------------------------------------------------

    def pop_notifications(self, username: str) -> List[str]:
        user = self._require_user(username)
        return user.pop_notifications()

    # -- Internal helpers ------------------------------------------------

    def _require_user(self, username: str) -> User:
        if username not in self.users:
            raise ValueError(f"Usuario desconocido: {username}")
        return self.users[username]

    def _require_post(self, post_id: int) -> Post:
        if post_id not in self.posts_by_id:
            raise ValueError(f"Publicación desconocida: {post_id}")
        return self.posts_by_id[post_id]

    def _notify_friends(self, user: User, message: str) -> None:
        for friend_username in user.friends:
            friend = self.users.get(friend_username)
            if friend is not None:
                friend.add_notification(message)

    def _notify_user(self, username: str, message: str) -> None:
        user = self.users.get(username)
        if user is not None:
            user.add_notification(message)

    def _push_post(self, post: Post) -> None:
        heapq.heappush(self._post_heap, (-post.priority, post.post_id))

    # -- Sample data -----------------------------------------------------

    def seed_demo_data(self) -> None:
        """Populate the network with demo users and posts."""

        if self.users:
            return
        alice = self.add_user("alice", "Alicia Ramírez", "Apasionada de la fotografía")
        bob = self.add_user("bob", "Roberto Díaz", "Explorador urbano")
        carol = self.add_user("carol", "Carolina López", "Chef experimental")

        self.add_friend("alice", "bob")
        self.add_friend("alice", "carol")
        self.add_friend("bob", "carol")

        self.create_post("alice", "¡Hola a todos! Esta es mi primera publicación en la red social.")
        post = self.create_post("bob", "Acabo de tomar una foto increíble del atardecer sobre la ciudad.")
        self.create_post("carol", "Nueva receta de tacos veganos con salsa picante.")

        self.like_post("alice", post.post_id)
        self.like_post("carol", post.post_id)
        self.comment_post("carol", post.post_id, "¡Quiero ver esas fotos ya!")
