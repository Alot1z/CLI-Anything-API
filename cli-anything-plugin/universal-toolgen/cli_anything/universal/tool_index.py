"""Token-efficient tool discovery index."""

from __future__ import annotations

from collections import defaultdict

from .schema import ToolSchema


class ToolIndex:
    def __init__(self, tools: list[ToolSchema]) -> None:
        self.tools = tools
        self._inverted: dict[str, set[int]] = defaultdict(set)
        for i, tool in enumerate(tools):
            for token in self._tokenize(f"{tool.name} {tool.description}"):
                self._inverted[token].add(i)

    def search(self, query: str, limit: int = 10) -> list[ToolSchema]:
        scores: dict[int, int] = defaultdict(int)
        for token in self._tokenize(query):
            for idx in self._inverted.get(token, set()):
                scores[idx] += 1

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [self.tools[idx] for idx, _ in ranked[:limit]]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [p for p in text.lower().replace(".", " ").replace("_", " ").split() if p]
