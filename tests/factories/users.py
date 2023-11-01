import factory
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    A factory for creating users
    """

    class Meta:
        model = User

    # Using a sequence to ensure unique emails
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
