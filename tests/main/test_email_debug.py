"""Regression coverage for browser-scoped email simulations."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from debug_toolbar.middleware import show_toolbar_func_or_path
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.urls import include, path

from apps.main.backends import ResendEmailBackend
from apps.main.tasks import queue_email, send_email_task
from core.debug.dev_utils import EmailDestinationsPanel
from core.debug.email import (
    DEBUG_EMAIL_SESSION_KEY,
    get_debug_email_destinations,
    normalize_debug_email_destinations,
    override_debug_email_destinations,
)
from core.debug.middleware import debug_email_middleware
from tests.factories.dummy import DummyFactory
from tests.factories.users import UserFactory


def show_email_toolbar(request):
    """Allow the toolbar in tests, including anonymous authentication pages."""
    return True


def email_context_view(request):
    """Expose request context and issue a CSRF token for endpoint tests."""
    return JsonResponse(
        {
            "destinations": get_debug_email_destinations(),
            "csrf_token": get_token(request),
        }
    )


urlpatterns = [
    path(
        "__debug__/",
        include((EmailDestinationsPanel.get_urls(), "djdt"), namespace="djdt"),
    ),
    path("__debug__/email-context/", email_context_view),
]


@override_settings(DEBUG=True)
class DebugEmailContextTests(SimpleTestCase):
    """Keep selections isolated and restricted to official test addresses."""

    def test_default_and_invalid_state_use_delivered(self):
        """Missing or invalid state cannot redirect email to a real recipient."""
        self.assertEqual(get_debug_email_destinations(), ["delivered@resend.dev"])
        for value in (None, [], "bounced@resend.dev", ["real@example.com"]):
            with self.subTest(value=value):
                self.assertEqual(
                    normalize_debug_email_destinations(value),
                    ["delivered@resend.dev"],
                )

    def test_normalization_removes_duplicates_and_unknown_addresses(self):
        """Resolve safe destinations in a consistent order."""
        self.assertEqual(
            normalize_debug_email_destinations(
                ["bounced@resend.dev", "real@example.com", "bounced@resend.dev"]
            ),
            ["bounced@resend.dev"],
        )

    def test_nested_context_is_restored_after_an_error(self):
        """A failed request or task cannot leak its selection into the next one."""
        with override_debug_email_destinations(["bounced@resend.dev"]):
            with (
                self.assertRaises(ValueError),
                override_debug_email_destinations(["suppressed@resend.dev"]),
            ):
                raise ValueError("Failed request")
            self.assertEqual(get_debug_email_destinations(), ["bounced@resend.dev"])
        self.assertEqual(get_debug_email_destinations(), ["delivered@resend.dev"])

    def test_middleware_uses_each_requests_session(self):
        """Sequential requests retain their own browser selection."""
        middleware = debug_email_middleware(
            lambda request: JsonResponse(
                {"destinations": get_debug_email_destinations()}
            )
        )
        for destinations in (["bounced@resend.dev"], ["complained@resend.dev"]):
            with self.subTest(destinations=destinations):
                request = RequestFactory().get("/")
                request.session = {DEBUG_EMAIL_SESSION_KEY: destinations}
                response = middleware(request)
                self.assertEqual(
                    json.loads(response.content)["destinations"], destinations
                )
                self.assertEqual(
                    get_debug_email_destinations(), ["delivered@resend.dev"]
                )

    @override_settings(DEBUG=False)
    def test_production_middleware_does_not_read_sessions(self):
        """The middleware bypasses development selection outside DEBUG."""
        request = RequestFactory().get("/")
        middleware = debug_email_middleware(lambda request: HttpResponse("OK"))
        with override_debug_email_destinations(["bounced@resend.dev"]):
            self.assertEqual(middleware(request).status_code, 200)


@override_settings(DEBUG=True, RESEND_API_KEY="test-key")
class DebugEmailDeliveryTests(SimpleTestCase):
    """Apply selected outcomes to synchronous and queued Django messages."""

    @patch("resend.Emails.send", return_value={"id": "email-id"})
    def test_multiple_outcomes_use_one_send_and_remove_real_recipients(self, send):
        """Send one message to all selected test destinations without leaking Cc/Bcc."""
        message = EmailMessage(
            "Subject",
            "Body",
            to=["real@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )
        destinations = ["bounced@resend.dev", "complained@resend.dev"]
        with override_debug_email_destinations(destinations):
            self.assertEqual(ResendEmailBackend().send_messages([message]), 1)
        send.assert_called_once()
        payload = send.call_args.args[0]
        self.assertEqual(payload["to"], destinations)
        self.assertNotIn("cc", payload)
        self.assertNotIn("bcc", payload)
        self.assertEqual(message.to, ["real@example.com"])
        self.assertEqual(message.cc, ["cc@example.com"])
        self.assertEqual(message.bcc, ["bcc@example.com"])

    @override_settings(DEBUG=False)
    @patch("resend.Emails.send", return_value={"id": "email-id"})
    def test_production_keeps_intended_recipients(self, send):
        """Saved development settings cannot affect production delivery."""
        message = EmailMessage("Subject", "Body", to=["real@example.com"])
        with override_debug_email_destinations(["bounced@resend.dev"]):
            self.assertEqual(ResendEmailBackend().send_messages([message]), 1)
        self.assertEqual(send.call_args.args[0]["to"], ["real@example.com"])

    @override_settings(
        MAILERS={"default": {"BACKEND": "apps.main.backends.ResendEmailBackend"}}
    )
    @patch("resend.Emails.send", return_value={"id": "email-id"})
    @patch("apps.main.tasks.send_email_task.defer")
    def test_queued_email_keeps_its_selection_after_browser_changes(self, defer, send):
        """Capture producer context and restore the worker's previous state afterward."""
        with override_debug_email_destinations(["bounced@resend.dev"]):
            queue_email("Subject", "Body", "sender@example.com", ["real@example.com"])
        queued_kwargs = defer.call_args.kwargs
        self.assertEqual(queued_kwargs["debug_destinations"], ["bounced@resend.dev"])

        with override_debug_email_destinations(["suppressed@resend.dev"]):
            self.assertTrue(send_email_task(**queued_kwargs))
            self.assertEqual(get_debug_email_destinations(), ["suppressed@resend.dev"])
        send.assert_called_once()
        self.assertEqual(send.call_args.args[0]["to"], ["bounced@resend.dev"])


@override_settings(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    DEBUG_TOOLBAR_CONFIG={"SHOW_TOOLBAR_CALLBACK": show_email_toolbar},
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "core.debug.middleware.debug_email_middleware",
        "django.middleware.csrf.CsrfViewMiddleware",
    ],
    TEMPLATES=[
        {
            **settings.TEMPLATES[0],
            "DIRS": [
                settings.BASE_DIR / "debug" / "templates",
                settings.ROOT_DIR / "templates",
            ],
        }
    ],
)
class EmailDestinationsPanelTests(TestCase):
    """Exercise the panel and its session mutation endpoint through Django."""

    url = "/__debug__/email-destinations/"

    def setUp(self):
        show_toolbar_func_or_path.cache_clear()
        self.addCleanup(show_toolbar_func_or_path.cache_clear)

    def test_selection_is_saved_only_for_the_current_browser(self):
        """Anonymous browsers can select outcomes without sharing session state."""
        destinations = ["bounced@resend.dev", "suppressed@resend.dev"]
        return_url = "/__debug__/email-context/?example=1"
        response = self.client.post(
            self.url, {"destinations": destinations, "next": return_url}
        )
        self.assertRedirects(response, return_url, fetch_redirect_response=False)
        self.assertEqual(
            self.client.get("/__debug__/email-context/").json()["destinations"],
            destinations,
        )
        self.assertEqual(
            Client().get("/__debug__/email-context/").json()["destinations"],
            ["delivered@resend.dev"],
        )

    def test_empty_or_unknown_choices_do_not_overwrite_the_selection(self):
        """Reject missing choices and attempts to introduce real email addresses."""
        self.client.post(self.url, {"destinations": ["bounced@resend.dev"]})
        for destinations in ([], ["real@example.com"], ["bounced@resend.dev", "bad"]):
            with self.subTest(destinations=destinations):
                response = self.client.post(self.url, {"destinations": destinations})
                self.assertEqual(response.status_code, 400)
                self.assertContains(response, 'role="alert"', status_code=400)
                self.assertContains(
                    response, 'name="destinations"', count=4, status_code=400
                )
                self.assertEqual(
                    self.client.session[DEBUG_EMAIL_SESSION_KEY], ["bounced@resend.dev"]
                )

    def test_get_cannot_change_destinations(self):
        """Only a POST can update the browser's selection."""
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_external_return_urls_are_rejected(self):
        """A posted return URL cannot redirect the browser to another site."""
        for return_url in ("https://other.example/", "//other.example/"):
            with self.subTest(return_url=return_url):
                response = self.client.post(
                    self.url,
                    {"destinations": ["bounced@resend.dev"], "next": return_url},
                )
                self.assertRedirects(response, "/", fetch_redirect_response=False)

    @override_settings(DEBUG=False)
    def test_endpoint_is_unavailable_outside_debug(self):
        """Even a registered endpoint cannot change production behavior."""
        self.assertEqual(self.client.post(self.url).status_code, 404)

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={"SHOW_TOOLBAR_CALLBACK": lambda request: False}
    )
    def test_endpoint_requires_toolbar_visibility(self):
        """Honor the toolbar's visibility policy before accepting changes."""
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_csrf_is_required_and_valid_token_allows_saving(self):
        """Require CSRF protection even on anonymous development pages."""
        client = Client(enforce_csrf_checks=True)
        destinations = {"destinations": ["bounced@resend.dev"]}
        self.assertEqual(client.post(self.url, destinations).status_code, 403)
        token = client.get("/__debug__/email-context/").json()["csrf_token"]
        response = client.post(self.url, {**destinations, "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)

    def test_panel_renders_choices_with_saved_selection(self):
        """Render four labeled choices and keep recorded panel data serializable."""
        request = RequestFactory().get("/")
        request.session = {DEBUG_EMAIL_SESSION_KEY: ["bounced@resend.dev"]}
        toolbar = SimpleNamespace(stats={}, store=Mock(), request_id="test-request")
        panel = EmailDestinationsPanel(toolbar, lambda request: HttpResponse())
        panel.generate_stats(request, HttpResponse())

        self.assertEqual(panel.nav_subtitle, "Bounced")
        self.assertEqual(panel.content.count('name="destinations"'), 4)
        self.assertEqual(panel.content.count("checked"), 1)
        self.assertIn('name="next" value="/"', panel.content)
        self.assertEqual(panel.scripts, [])
        self.assertIn('value="bounced@resend.dev"', panel.content)
        json.dumps(panel.get_stats())


@override_settings(DEBUG=True)
class ReportDebugEmailTests(TestCase):
    """Verify the application's report workflow captures the browser selection."""

    @patch("apps.main.tasks.send_email_task.defer")
    def test_report_receipt_keeps_selected_test_destinations(self, defer):
        """Pass the active selection from the report lifecycle hook into the job."""
        reporter = UserFactory()
        reportable = DummyFactory()
        with override_debug_email_destinations(["suppressed@resend.dev"]):
            reportable.report(reporter, "Test report")

        defer.assert_called_once()
        self.assertEqual(
            defer.call_args.kwargs["debug_destinations"], ["suppressed@resend.dev"]
        )
        self.assertEqual(defer.call_args.kwargs["recipient_list"], [reporter.email])
