from dataclasses import dataclass

from ..types import JobID


@dataclass
class Job:
    id: JobID
    text: str

    def count_words(self) -> int:
        return len(self.text.split())

    def count_unique_words(self) -> int:
        return len(set(self.text.lower().split()))
