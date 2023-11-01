import factory

from main.models import Notification
from tests.factories.users import UserFactory


class NotificationFactory(factory.django.DjangoModelFactory):
    """
    A factory for creating notifications
    """

    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    message = factory.Faker("paragraph")
    link = factory.Faker("url")
    is_read = False
    type = "info"
