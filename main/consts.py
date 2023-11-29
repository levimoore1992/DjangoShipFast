from enum import Enum


class ContactStatus(Enum):
    """
    Enum representing different statuses of contact requests.
    """

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

    @classmethod
    def choices(cls) -> list:
        """
        Return choices for model field.

        Returns:
            A list of tuple containing the enum's items.
        """
        return [(key.value, key.value) for key in cls]


class ContactType(Enum):
    """
    Enum representing different types of contact requests.
    """

    GENERAL = "General"
    BUG_REPORT = "Bug Report"
    FEATURE_REQUEST = "Feature Request"
    SUPPORT = "Support"
    OTHER = "Other"

    @classmethod
    def choices(cls) -> list:
        """
        Return choices for model field.

        Returns:
            A list of tuple containing the enum's items.
        """
        return [(key.value, key.value) for key in cls]
