from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class ReadOnlyInline(admin.TabularInline):
    """
    A base inline admin class to make fields read-only and provide a link to the actual instance.
    """

    def view_link(self, obj):
        """
        Generates a hyperlink to the admin page for the given object.

        :param obj: The instance for which the link is generated.
        :return: HTML anchor tag as a string.
        """
        if obj.pk:  # Checking if the object has been saved and has a primary key
            app_label = obj._meta.app_label
            model_name = obj._meta.model_name
            url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
            return format_html(f'<a href="{url}">View</a>')
        return ""  # Return empty string if obj is not saved

    view_link.short_description = "View Details"  # Text for the column header

    def get_readonly_fields(self, request, obj=None):
        """
        Marks all fields as read-only and includes the 'view_link' method.

        :param request: HttpRequest object.
        :param obj: The current object instance being edited.
        :return: A tuple containing all fields as read-only plus the 'view_link' method.
        """
        fields = [field.name for field in self.model._meta.fields]
        fields.append("view_link")  # Adding 'view_link' to the fields list
        return fields

    readonly_fields = (
        "view_link",
    )  # Ensuring 'view_link' is treated as a read-only field
