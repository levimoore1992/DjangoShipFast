from django.test import TestCase
from main.tasks import add


class TestTask(TestCase):
    """A test task to test celery tasks."""

    def test_my_task(self):
        """Test my_task()"""

        result = add.apply_async((1, 2), serializer="json").get()
        self.assertEqual(result, 3)
