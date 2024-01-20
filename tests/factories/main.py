import factory
from django.utils import timezone

from main.consts import ContactStatus
from main.models import Notification, Contact
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


class ContactFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Contact model for testing.
    """

    class Meta:
        model = Contact

    name = factory.Faker("name")
    email = factory.Faker("email")
    subject = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("text")
    contact_date = factory.LazyFunction(timezone.now)
    status = ContactStatus.PENDING.value
    type = factory.Faker("word")
    admin_notes = factory.Faker("text")
