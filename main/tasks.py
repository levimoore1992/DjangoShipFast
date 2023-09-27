from celery import shared_task


@shared_task
def add(x: int, y: int) -> int:
    """A simple task that adds two numbers."""
    return x + y
