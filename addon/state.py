"""Small revision gate: stale asynchronous snapshots must never overwrite newer data."""

from dataclasses import dataclass


@dataclass
class RevisionGate:
    revision: int = 0
    epoch: int = 0

    def request(self) -> tuple[int, int]:
        self.revision += 1
        return self.token

    @property
    def token(self) -> tuple[int, int]:
        return self.epoch, self.revision

    def accepts(self, token: tuple[int, int]) -> bool:
        return token == self.token

    def invalidate(self) -> None:
        self.epoch += 1
        self.revision = 0
