"""String searching algorithms used in the social network."""

from __future__ import annotations

from typing import Iterable, List


def build_kmp_table(pattern: str) -> List[int]:
    """Build the partial match table for the KMP algorithm."""

    table = [0] * len(pattern)
    prefix_len = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[prefix_len]:
            prefix_len += 1
            table[i] = prefix_len
            i += 1
        else:
            if prefix_len != 0:
                prefix_len = table[prefix_len - 1]
            else:
                table[i] = 0
                i += 1
    return table


def kmp_search(text: str, pattern: str) -> bool:
    """Return True if *pattern* is found in *text* using KMP search."""

    if pattern == "":
        return True
    table = build_kmp_table(pattern)
    text_index = 0
    pattern_index = 0
    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1
            if pattern_index == len(pattern):
                return True
        else:
            if pattern_index != 0:
                pattern_index = table[pattern_index - 1]
            else:
                text_index += 1
    return False


def search_collection(collection: Iterable[str], pattern: str) -> list[str]:
    pattern = pattern.lower().strip()
    if not pattern:
        return list(collection)
    results: list[str] = []
    for value in collection:
        if kmp_search(value.lower(), pattern):
            results.append(value)
    return results
