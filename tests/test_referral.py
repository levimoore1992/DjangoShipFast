from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class ReferralSourceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.url = reverse("update_referral_source")

    def test_update_referral_source(self):
        self.client.login(email="test@example.com", password="password")
        data = {"referral_source": "Google"}
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.referral_source, "Google")

    def test_update_referral_source_custom(self):
        self.client.login(email="test@example.com", password="password")
        data = {"referral_source": "Custom Value"}
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.referral_source, "Custom Value")

    def test_update_referral_source_unauthenticated(self):
        data = {"referral_source": "Google"}
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertNotEqual(response.status_code, 200)  # Should redirect or 403
