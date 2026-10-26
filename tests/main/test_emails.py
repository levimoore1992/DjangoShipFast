import base64
import json
from email.headerregistry import Address
from email.message import MIMEPart
from types import SimpleNamespace
from unittest.mock import Mock, patch

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.test import SimpleTestCase, override_settings
from resend.exceptions import ResendError

from apps.main.backends import ResendEmailBackend

RESEND_BACKEND = "apps.main.backends.ResendEmailBackend"


def api_error():
    """Build a provider error without calling Resend."""
    return ResendError(
        code=429,
        error_type="rate_limit_exceeded",
        message="Too many requests",
        suggested_action="Try again later.",
    )


@override_settings(
    RESEND_API_KEY="test_api_key",
    DEFAULT_FROM_EMAIL="sender@example.com",
    DEBUG=False,
    MAILERS={"default": {"BACKEND": RESEND_BACKEND}},
)
class ResendEmailBackendTests(SimpleTestCase):
    """Exercise Django mail delivery, sandboxing, and backend overrides."""

    def setUp(self):
        patcher = patch(
            "apps.main.backends.resend.Emails.send", return_value={"id": "email-id"}
        )
        self.send = patcher.start()
        self.addCleanup(patcher.stop)
        self.backend = ResendEmailBackend()
        self.message = EmailMessage(
            "Subject", "Plain body", to=["recipient@example.com"]
        )

    def test_django_send_mail_uses_resend(self):
        """Route the standard Django entry point through Resend."""
        sent = send_mail("Subject", "Plain body", None, ["recipient@example.com"])

        self.assertEqual(sent, 1)
        self.send.assert_called_once_with(
            {
                "from": "sender@example.com",
                "to": ["recipient@example.com"],
                "subject": "Subject",
                "text": "Plain body",
            }
        )

    def test_text_and_html_alternatives_are_preserved(self):
        """Keep both bodies of a multipart alternative message."""
        message = EmailMultiAlternatives(
            "Subject", "Plain body", to=["recipient@example.com"]
        )
        message.attach_alternative("<p>HTML body</p>", "text/html")

        self.assertEqual(self.backend.send_messages([message]), 1)
        payload = self.send.call_args.args[0]
        self.assertEqual(payload["text"], "Plain body")
        self.assertEqual(payload["html"], "<p>HTML body</p>")

    @override_settings(ACCOUNT_EMAIL_SUBJECT_PREFIX="")
    def test_allauth_password_reset_uses_resend_and_preserves_link(self):
        """Deliver the existing authentication template with its reset URL."""
        reset_url = "https://example.com/accounts/password/reset/key/test/"
        message = DefaultAccountAdapter().render_mail(
            "account/email/password_reset_key",
            "recipient@example.com",
            {
                "password_reset_url": reset_url,
                "current_site": SimpleNamespace(name="Example", domain="example.com"),
            },
        )

        self.assertEqual(message.send(), 1)

        payload = self.send.call_args.args[0]
        self.assertEqual(payload["to"], ["recipient@example.com"])
        self.assertIn(reset_url, payload["text"])

    def test_html_only_message(self):
        """Preserve messages whose main body is HTML."""
        self.message.body = "<p>HTML body</p>"
        self.message.content_subtype = "html"

        self.backend.send_messages([self.message])

        payload = self.send.call_args.args[0]
        self.assertEqual(payload["html"], "<p>HTML body</p>")
        self.assertNotIn("text", payload)

    def test_recipients_reply_to_sender_and_custom_headers(self):
        """Retain addressing and headers for production messages."""
        message = EmailMessage(
            "Subject",
            "Body",
            "Sender <sender@example.com>",
            ["first@example.com", "second@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            reply_to=["Support <support@example.com>", "other@example.com"],
            headers={"X-Tracking-ID": "tracking-id"},
        )

        self.backend.send_messages([message])

        payload = self.send.call_args.args[0]
        self.assertEqual(payload["from"], "Sender <sender@example.com>")
        self.assertEqual(payload["to"], message.to)
        self.assertEqual(payload["cc"], message.cc)
        self.assertEqual(payload["bcc"], message.bcc)
        self.assertEqual(payload["reply_to"], message.reply_to)
        self.assertEqual(payload["headers"], {"X-Tracking-ID": "tracking-id"})

    def test_text_binary_and_forwarded_message_attachments(self):
        """Encode supported attachment formats without changing their contents."""
        forwarded = MIMEPart()
        forwarded.set_content("Forwarded body")
        self.message.attach("notes.txt", "Café", "text/plain")
        self.message.attach("image.png", b"\x89PNG\r\n", "image/png")
        self.message.attach("forwarded.eml", forwarded, "message/rfc822")

        self.backend.send_messages([self.message])

        attachments = self.send.call_args.args[0]["attachments"]
        self.assertEqual(attachments[0]["filename"], "notes.txt")
        self.assertEqual(attachments[0]["content_type"], "text/plain")
        self.assertEqual(base64.b64decode(attachments[0]["content"]), "Café".encode())
        self.assertEqual(base64.b64decode(attachments[1]["content"]), b"\x89PNG\r\n")
        self.assertEqual(
            base64.b64decode(attachments[2]["content"]), forwarded.as_bytes()
        )

    def test_inline_mime_attachment(self):
        """Keep the content ID used by inline images."""
        image = MIMEPart()
        image.set_content(
            b"image-data",
            maintype="image",
            subtype="png",
            disposition="inline",
            filename="logo.png",
            cid="<logo>",
        )
        self.message.attach(image)

        self.backend.send_messages([self.message])

        attachment = self.send.call_args.args[0]["attachments"][0]
        self.assertEqual(attachment["content_id"], "logo")
        self.assertEqual(attachment["filename"], "logo.png")
        self.assertEqual(base64.b64decode(attachment["content"]), b"image-data")

    @override_settings(DEBUG=True)
    def test_debug_redirects_all_recipients_without_mutating_message(self):
        """Prevent development messages from reaching any real recipient."""
        self.message.cc = ["real-cc@example.com"]
        self.message.bcc = ["real-bcc@example.com"]
        self.message.extra_headers = {
            "To": "override@example.com",
            "Cc": "override-cc@example.com",
            "X-Tracking-ID": "tracking-id",
        }

        self.backend.send_messages([self.message])

        payload = self.send.call_args.args[0]
        self.assertEqual(payload["to"], ["delivered@resend.dev"])
        self.assertNotIn("cc", payload)
        self.assertNotIn("bcc", payload)
        self.assertEqual(payload["headers"], {"X-Tracking-ID": "tracking-id"})
        self.assertEqual(self.message.to, ["recipient@example.com"])
        self.assertEqual(self.message.cc, ["real-cc@example.com"])
        self.assertEqual(self.message.bcc, ["real-bcc@example.com"])

    def test_bcc_only_message_keeps_bcc_private(self):
        """Allow blind recipients without exposing them in the To field."""
        self.message.to = []
        self.message.bcc = ["private@example.com"]

        self.assertEqual(self.backend.send_messages([self.message]), 1)

        payload = self.send.call_args.args[0]
        self.assertEqual(payload["to"], [])
        self.assertEqual(payload["bcc"], ["private@example.com"])

    def test_empty_batch_or_no_recipients_sends_nothing(self):
        """Avoid provider requests when there is nobody to receive a message."""
        self.message.to = []

        for messages in ([], None, [self.message]):
            with self.subTest(messages=messages):
                self.assertEqual(self.backend.send_messages(messages), 0)
        self.send.assert_not_called()

    def test_success_count_ignores_messages_without_recipients(self):
        """Count delivered messages rather than input messages."""
        empty = EmailMessage("Subject", "Body")

        self.assertEqual(
            self.backend.send_messages([self.message, empty, self.message]), 2
        )
        self.assertEqual(self.send.call_count, 2)

    def test_api_failure_propagates(self):
        """Expose provider failures to callers by default."""
        self.send.side_effect = api_error()

        with self.assertRaises(ResendError):
            self.backend.send_messages([self.message])

    def test_silent_failure_continues_and_counts_successes(self):
        """Continue a batch after a suppressed provider failure."""
        self.send.side_effect = [api_error(), {"id": "second-id"}]

        sent = ResendEmailBackend(fail_silently=True).send_messages(
            [self.message, self.message]
        )

        self.assertEqual(sent, 1)
        self.assertEqual(self.send.call_count, 2)

    def test_invalid_response_is_not_counted_as_sent(self):
        """Require the provider's message ID before reporting success."""
        self.send.return_value = {}

        with self.assertRaises(ResendError):
            self.backend.send_messages([self.message])
        self.assertEqual(
            ResendEmailBackend(fail_silently=True).send_messages([self.message]), 0
        )

    @override_settings(RESEND_API_KEY="")
    def test_missing_key_is_a_configuration_error(self):
        """Report missing credentials before attempting delivery."""
        with self.assertRaisesMessage(ImproperlyConfigured, "RESEND_API_KEY"):
            self.backend.send_messages([self.message])
        self.send.assert_not_called()

    def test_header_injection_is_rejected_before_delivery(self):
        """Keep Django's protection against injected message headers."""
        self.message.subject = "Subject\nBcc: attacker@example.com"

        with self.assertRaises(ValueError):
            self.backend.send_messages([self.message])
        self.send.assert_not_called()

    def test_unsupported_alternative_is_rejected(self):
        """Fail explicitly instead of discarding unsupported message bodies."""
        message = EmailMultiAlternatives("Subject", "Body", to=["to@example.com"])
        message.attach_alternative("calendar-data", "text/calendar")

        with self.assertRaisesMessage(ValueError, "text/calendar"):
            self.backend.send_messages([message])
        self.send.assert_not_called()

    def test_backend_override_can_disable_delivery(self):
        """Allow disabling delivery through Django's dummy backend."""
        backend = "django.core.mail.backends.dummy.EmailBackend"
        with override_settings(MAILERS={"default": {"BACKEND": backend}}):
            send_mail("Subject", "Body", None, self.message.to)
        self.send.assert_not_called()

    def test_backend_override_can_capture_delivery_in_memory(self):
        """Allow capturing email without contacting the provider."""
        backend = "django.core.mail.backends.locmem.EmailBackend"
        with override_settings(MAILERS={"default": {"BACKEND": backend}}):
            self.assertEqual(send_mail("Subject", "Body", None, self.message.to), 1)
            self.assertEqual(mail.outbox[-1].to, self.message.to)
        self.send.assert_not_called()


@override_settings(RESEND_API_KEY="test_api_key", DEBUG=False)
class ResendMIMEAttachmentTests(SimpleTestCase):
    """Cover forwarded MIME messages and unsupported nested attachments."""

    def setUp(self):
        self.backend = ResendEmailBackend()
        self.message = EmailMessage("Subject", "Body", to=["recipient@example.com"])

    @patch("apps.main.backends.resend.Emails.send", return_value={"id": "email-id"})
    def test_forwarded_mime_attachment(self, send):
        """Preserve a forwarded message supplied as a complete MIME attachment."""
        forwarded = MIMEPart()
        forwarded.set_content("Forwarded body")
        attachment = MIMEPart()
        attachment.set_content(forwarded)
        attachment.add_header(
            "Content-Disposition", "attachment", filename="forwarded.eml"
        )
        self.message.attach(attachment)

        self.assertEqual(self.backend.send_messages([self.message]), 1)

        result = send.call_args.args[0]["attachments"][0]
        self.assertEqual(result["filename"], "forwarded.eml")
        self.assertEqual(result["content_type"], "message/rfc822")
        self.assertEqual(base64.b64decode(result["content"]), forwarded.as_bytes())

    @patch("apps.main.backends.resend.Emails.send", return_value={"id": "email-id"})
    def test_multipart_mime_attachment_is_rejected_before_delivery(self, send):
        """Reject a multipart attachment rather than sending incomplete contents."""
        attachment = MIMEPart()
        attachment.make_mixed()
        part = MIMEPart()
        part.set_content("Nested body")
        attachment.attach(part)
        self.message.attach(attachment)

        with self.assertRaisesMessage(ValueError, "multipart MIME attachments"):
            self.backend.send_messages([self.message])
        send.assert_not_called()


@override_settings(RESEND_API_KEY="sdk-test-key", DEBUG=False)
class ResendSDKIntegrationTests(SimpleTestCase):
    """Exercise the real SDK while replacing its HTTP transport."""

    @patch("requests.sessions.Session.send")
    def test_address_objects_are_serialized_in_each_recipient_field(self, send):
        """Serialize mixed Address and string recipients through the real SDK."""
        send.return_value = Mock(
            content=b'{"id": "email-id"}',
            status_code=200,
            headers={"content-type": "application/json"},
        )
        address = Address("Recipient, José", addr_spec="recipient@example.com")
        recipients = [address, "other@example.com"]

        for field in ("to", "cc", "bcc"):
            with self.subTest(field=field):
                fields = {"to": ["primary@example.com"], field: recipients}
                message = EmailMessage("Subject", "Body", **fields)

                self.assertEqual(ResendEmailBackend().send_messages([message]), 1)

                send.assert_called_once()
                payload = json.loads(send.call_args.args[0].body)
                self.assertEqual(payload[field], [str(address), "other@example.com"])
                self.assertEqual(getattr(message, field), recipients)
                self.assertIs(getattr(message, field)[0], address)
                send.reset_mock()

    @patch("resend.default_http_client.request")
    def test_sdk_receives_current_key_and_payload(self, request):
        """Read credentials at send time and build an authenticated API request."""
        request.return_value = (
            b'{"id": "email-id"}',
            200,
            {"content-type": "application/json"},
        )
        message = EmailMessage("Subject", "Body", to=["to@example.com"])

        self.assertEqual(ResendEmailBackend().send_messages([message]), 1)

        kwargs = request.call_args.kwargs
        self.assertEqual(kwargs["url"], "https://api.resend.com/emails")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer sdk-test-key")
        self.assertEqual(kwargs["json"]["from"], settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(kwargs["json"]["text"], "Body")

    @patch("resend.default_http_client.request", side_effect=TimeoutError("Timed out"))
    def test_sdk_transport_failure_propagates_as_resend_error(self, request):
        """Expose connection failures using the provider's exception type."""
        message = EmailMessage("Subject", "Body", to=["to@example.com"])

        with self.assertRaises(ResendError):
            ResendEmailBackend().send_messages([message])
        request.assert_called_once()
