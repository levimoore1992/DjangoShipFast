from django.test import TestCase

from tests.factories.users import UserFactory


class BaseTestCase(TestCase):
    """
    The base test for all tests. This is to setup the database and create
    users.
    """

    databases = "__all__"

    def setUp(self):
        super().setUp()
        # Create a regular user
        self.regular_user = UserFactory()

        # Create a superuser
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
