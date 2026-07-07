from ....infra import JobRepo


def get_repo() -> JobRepo:
    return JobRepo()
