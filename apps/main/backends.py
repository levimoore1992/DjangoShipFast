"""Django email delivery through Resend."""

import base64
from email.message import Message
from email.utils import formataddr, getaddresses

import resend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from resend.exceptions import ResendError


class ResendEmailBackend(BaseEmailBackend):
    """Send Django messages with the Resend SDK, sandboxing recipients in DEBUG."""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(**kwargs)
        self.fail_silently = fail_silently

    def send_messages(self, email_messages):
        """Send a batch and count only messages accepted by Resend."""
        sent = 0
        for email_message in email_messages or []:
            if not email_message.recipients():
                continue
            if self._send_message(email_message):
                sent += 1
        return sent

    def _send_message(self, email_message):
        """Deliver one message using the configured failure policy."""
        if not settings.RESEND_API_KEY:
            raise ImproperlyConfigured(
                "RESEND_API_KEY must be set to use the Resend email backend."
            )

        payload = self._build_payload(email_message)
        resend.api_key = settings.RESEND_API_KEY
        try:
            self._validate_response(resend.Emails.send(payload))
        except ResendError:
            if not self.fail_silently:
                raise
            return False
        return True

    @staticmethod
    def _validate_response(response):
        """Require a provider message ID before treating delivery as successful."""
        if not response.get("id"):
            raise ResendError(
                code=502,
                error_type="InvalidResponse",
                message="Resend did not return an email ID.",
                suggested_action="Check the Resend API response.",
            )

    def _build_payload(self, email_message):
        """Assemble the Resend request from the Django message."""
        # Build the MIME message to retain Django's header validation.
        message = email_message.message()
        payload = {
            "from": str(message["From"]),
            "subject": str(message["Subject"]),
        }
        payload.update(self._build_body_fields(email_message))
        payload.update(self._build_recipient_fields(email_message, message))
        if headers := self._build_custom_headers(email_message):
            payload["headers"] = headers
        if attachments := self._build_attachments(email_message):
            payload["attachments"] = attachments
        self._apply_debug_recipients(payload)
        return payload

    @staticmethod
    def _build_body_fields(email_message):
        """Map plain text and HTML bodies to Resend's content fields."""
        payload = {}
        bodies = [(email_message.body, f"text/{email_message.content_subtype}")]
        bodies.extend(getattr(email_message, "alternatives", []))
        for content, mimetype in bodies:
            if mimetype not in {"text/plain", "text/html"}:
                raise ValueError(f"Resend does not support {mimetype} email bodies.")
            payload["html" if mimetype == "text/html" else "text"] = str(content)
        return payload

    @staticmethod
    def _build_recipient_fields(email_message, message):
        """Collect To, Cc, Bcc, and Reply-To addresses."""
        payload = {"to": [str(recipient) for recipient in email_message.to]}
        for field in ("cc", "bcc"):
            if recipients := getattr(email_message, field):
                payload[field] = [str(recipient) for recipient in recipients]
        if reply_to := message["Reply-To"]:
            payload["reply_to"] = [
                formataddr(address) for address in getaddresses([str(reply_to)])
            ]
        return payload

    @staticmethod
    def _build_custom_headers(email_message):
        """Keep extra headers separate from fields managed by the backend."""
        return {
            name: str(value)
            for name, value in email_message.extra_headers.items()
            if name.lower() not in {"from", "to", "cc", "bcc", "reply-to", "subject"}
        }

    def _build_attachments(self, email_message):
        """Serialize every attachment for the Resend request."""
        return [
            self._serialize_attachment(attachment, email_message.encoding)
            for attachment in email_message.attachments
        ]

    @staticmethod
    def _apply_debug_recipients(payload):
        """Limit development delivery to Resend's test inbox."""
        if settings.DEBUG:
            payload["to"] = ["delivered@resend.dev"]
            payload.pop("cc", None)
            payload.pop("bcc", None)

    def _serialize_attachment(self, attachment, encoding):
        """Build one attachment with its filename, contents, and content ID."""
        content_id = None
        if isinstance(attachment, Message):
            filename, content, mimetype, content_id = self._read_mime_attachment(
                attachment
            )
        else:
            filename, content, mimetype = attachment

        result = {
            "filename": filename or "attachment",
            "content": self._encode_attachment_content(content, encoding),
            "content_type": mimetype,
        }
        if content_id:
            result["content_id"] = str(content_id).strip("<>")
        return result

    @staticmethod
    def _read_mime_attachment(attachment):
        """Extract MIME attachment contents, including forwarded messages."""
        mimetype = attachment.get_content_type()
        content = attachment.get_payload(decode=True)
        if mimetype == "message/rfc822":
            content = attachment.get_payload()[0].as_bytes()
        if content is None:
            raise ValueError("Resend does not support multipart MIME attachments.")
        return (
            attachment.get_filename(),
            content,
            mimetype,
            attachment.get("Content-ID"),
        )

    @staticmethod
    def _encode_attachment_content(content, encoding):
        """Convert text, messages, or binary contents into Base64."""
        if isinstance(content, Message):
            content = content.as_bytes()
        elif isinstance(content, str):
            content = content.encode(encoding or settings.DEFAULT_CHARSET)
        return base64.b64encode(content).decode("ascii")
