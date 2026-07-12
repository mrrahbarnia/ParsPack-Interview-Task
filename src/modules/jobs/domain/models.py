from dataclasses import dataclass

from ..types import JobID, JobResult, JobStatus

from src.shared.const import DomainError


class InvalidJobStatus(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class Job:
    id: JobID
    text: str
    status: JobStatus
    result: JobResult | None = None

    def count_words(self) -> int:
        if self.status != JobStatus.PROCESSING:
            raise InvalidJobStatus(
                message=f"Cannot countig words from job in state {self.status}"
            )

        # Simulating a CPU intensive task
        count = 0
        for _ in range(1_000_000_000):
            count += 1

        return len(self.text.split())

    def count_unique_words(self) -> int:
        if self.status != JobStatus.PROCESSING:
            raise InvalidJobStatus(
                message=f"Cannot countig unique words from job in state {self.status}"
            )

        # Simulating a CPU intensive task
        count = 0
        for _ in range(1_000_000_000):
            count += 1

        return len(set(self.text.lower().split()))
