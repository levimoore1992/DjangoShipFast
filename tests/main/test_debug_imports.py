"""Ensure production execution does not depend on local development code."""

import os
import subprocess
import sys
import textwrap

from django.test import SimpleTestCase


class TestSettingsDebugIsolationTests(SimpleTestCase):
    """Keep toolbar tests independent of a developer's local settings file."""

    def test_toolbar_tests_import_without_local_settings(self):
        """Register toolbar models before collecting tests in a clean CI process."""
        script = textwrap.dedent(
            """
            import sys
            from unittest.mock import patch

            with patch.dict(sys.modules, {'core.settings.local': None}):
                import django
                django.setup()

                from django.apps import apps
                from tests.main import test_email_debug

                assert apps.is_installed('debug_toolbar')
                assert test_email_debug.EmailDestinationsPanel
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            env={
                **os.environ,
                "DJANGO_SETTINGS_MODULE": "tests.settings",
                "ENABLE_SENTRY": "FALSE",
            },
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ProductionDebugIsolationTests(SimpleTestCase):
    """Exercise startup and email delivery with debug modules unavailable."""

    def test_production_starts_and_sends_without_the_debug_package(self):
        """Keep development-only imports out of web and worker execution."""
        script = textwrap.dedent(
            """
            import sys
            from unittest.mock import patch

            with patch.dict(sys.modules, {
                'core.settings.local': None,
                'core.debug': None,
                'debug_toolbar': None,
            }):
                import django
                django.setup()

                from django.conf import settings
                from django.core.mail import EmailMessage
                from django.urls import get_resolver
                from apps.main.backends import ResendEmailBackend
                from apps.main.tasks import queue_email, send_email_task

                assert get_resolver().url_patterns
                settings.RESEND_API_KEY = 'test-key'
                message = EmailMessage('Subject', 'Body', to=['real@example.com'])
                with patch('resend.Emails.send', return_value={'id': 'test-id'}) as send:
                    assert ResendEmailBackend().send_messages([message]) == 1
                    assert send.call_args.args[0]['to'] == ['real@example.com']

                with patch('apps.main.tasks.send_mail', return_value=1):
                    assert send_email_task(
                        'Subject', 'Body', 'sender@example.com', ['real@example.com'],
                        debug_destinations=['bounced@resend.dev'],
                    )

                with patch('apps.main.tasks.send_email_task.defer') as defer:
                    queue_email('Subject', 'Body', 'sender@example.com', ['real@example.com'])
                    assert 'debug_destinations' not in defer.call_args.kwargs

                assert sys.modules['core.debug'] is None
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            env={
                **os.environ,
                "DJANGO_SETTINGS_MODULE": "core.settings",
                "DEBUG": "FALSE",
                "ENABLE_SENTRY": "FALSE",
            },
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
