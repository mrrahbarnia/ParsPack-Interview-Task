from dataclasses import dataclass


@dataclass
class DBLock:
    is_active: bool = False
    timeout_second: int = 1
    skip_locked: bool = False
