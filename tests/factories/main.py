import io

import factory
from PIL import Image
from django.core.files.base import ContentFile
from django.utils import timezone

from main.consts import ContactStatus
from main.models import Notification, Contact, SocialMediaLink
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


class SocialMediaLinkFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the SocialMedia model for testing.
    """

    class Meta:
        model = SocialMediaLink

    platform_name = factory.Faker("word")
    profile_url = factory.Faker("url")

    # For image, we're generating a simple dummy image
    @factory.lazy_attribute
    def image(self):
        """
        Create a dummy image (1x1 pixel, black) and return it as a ContentFile.
        :return: ContentFile
        """
        file = io.BytesIO()
        image = Image.new("RGB", size=(1, 1), color=(0, 0, 0))
        image.save(file, "JPEG")
        file.name = "test.jpg"
        file.seek(0)

        return ContentFile(file.read(), "test.jpg")


class FAQFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the FAQ model for testing.
    """

    class Meta:
        model = "main.FAQ"

    question = factory.Faker("sentence")
    answer = factory.Faker("paragraph")
