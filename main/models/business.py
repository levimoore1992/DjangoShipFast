from django.db import models


class TermsAndConditions(models.Model):
    terms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Terms And Conditions created at {self.created_at}"

    class Meta:
        verbose_name = "Terms and Conditions"
        verbose_name_plural = "Terms and Conditions"
