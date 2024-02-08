import subprocess
from io import StringIO
from unittest import mock

from django.test import TestCase, override_settings
from django.core.management import call_command
from apps.main.management.commands.restore_db import Command, NO_COMMANDS_MESSAGE


@override_settings(DEBUG=True)
class RestoreDbCommandTest(TestCase):
    """
    Test suite for the restore_db command.
    """

    def setUp(self):
        """
        Set up the test suite.
        :return: None
        """
        self.command = Command()

    @mock.patch("apps.main.management.commands.restore_db.sys.exit")
    def test_validate_arguments_target_production(self, mock_exit):
        """
        Test that validate_arguments exits when target is production.
        :param mock_exit:
        :return: None
        """
        self.command.validate_arguments(
            source="test", target="production", file_name="file.dump"
        )
        mock_exit.assert_called_once_with(1)

    @mock.patch("apps.main.management.commands.restore_db.sys.exit")
    def test_validate_arguments_target_not_in_db(self, mock_exit):
        """
        Test that validate_arguments exits when target is not in the database.
        :param mock_exit:
        :return:
        """
        self.command.validate_arguments(
            source="test", target="invalid", file_name="file.dump"
        )
        mock_exit.assert_called_once_with(1)

    @mock.patch("apps.main.management.commands.restore_db.sys.exit")
    def test_validate_arguments_source_not_in_db(self, mock_exit):
        """
        Test that validate_arguments exits when source is not in the database.
        :param mock_exit:
        :return:
        """
        self.command.validate_arguments(
            source="invalid", target="local", file_name="file.dump"
        )
        mock_exit.assert_called_once_with(1)

    @mock.patch("apps.main.management.commands.restore_db.sys.exit")
    def test_validate_arguments_same_source_target(self, mock_exit):
        """
        Test that validate_arguments exits when source and target are the same.
        :param mock_exit:
        :return:
        """
        self.command.validate_arguments(
            source="local", target="local", file_name="file.dump"
        )
        mock_exit.assert_called_once_with(0)

    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=False
    )
    @mock.patch("apps.main.management.commands.restore_db.sys.exit")
    def test_validate_arguments_file_missing(self, mock_exit, mock_exists):
        """
        Test that validate_arguments exits when file is missing.
        :param mock_exit:
        :param mock_exists:
        :return:
        """
        self.command.validate_arguments(
            source=None, target="local", file_name="missing.dump"
        )
        mock_exit.assert_called_once_with(1)

    @mock.patch("apps.main.management.commands.restore_db.subprocess.check_call")
    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    def test_command_execution_success(self, mock_exists, mock_subprocess):
        """
        Test that the command executes successfully.
        :param mock_exists:
        :param mock_subprocess:
        :return:
        """
        with mock.patch(
            "apps.main.management.commands.restore_db.input", return_value="y"
        ):
            call_command(
                "restore_db", source="local", target="test", file_name="test.dump"
            )
            mock_subprocess.assert_called()

    @mock.patch("apps.main.management.commands.restore_db.subprocess.check_call")
    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    def test_same_source_target_error(self, mock_exists, mock_subprocess):
        """
        Test that the command exits when source and target are the same.
        :param mock_exists:
        :param mock_subprocess:
        :return:
        """
        with self.assertRaises(SystemExit):
            call_command(
                "restore_db", source="local", target="local", file_name="test.dump"
            )

    @mock.patch("apps.main.management.commands.restore_db.subprocess.check_call")
    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    def test_production_target_error(self, mock_exists, mock_subprocess):
        """
        Test that the command exits when target is production.
        :param mock_exists:
        :param mock_subprocess:
        :return:
        """
        with self.assertRaises(SystemExit):
            call_command(
                "restore_db", source="local", target="production", file_name="test.dump"
            )

    @mock.patch(
        "apps.main.management.commands.restore_db.subprocess.check_call",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    )
    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    def test_command_execution_failure(self, mock_exists, mock_subprocess):
        """
        Test that the command exits when the command fails.
        :param mock_exists:
        :param mock_subprocess:
        :return:
        """
        with mock.patch(
            "apps.main.management.commands.restore_db.input", return_value="n"
        ):
            with self.assertRaises(SystemExit):
                call_command(
                    "restore_db", source="local", target="test", file_name="test.dump"
                )

    @mock.patch("apps.main.management.commands.restore_db.subprocess.check_call")
    def test_run_commands_success(self, mock_check_call):
        """Test that run_commands executes without errors."""
        commands = ['echo "Test Command"']
        env = {"TEST": "environment"}

        self.command.run_commands(commands, env)

        mock_check_call.assert_called_with(commands[0], env=env, shell=True)

    @mock.patch(
        "subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "cmd")
    )
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_run_commands_failure(self, mock_stdout, mock_check_call):
        """Test that run_commands handles a failed command."""
        command = Command()
        commands = ["invalid_command"]
        env = {"TEST": "environment"}

        command.run_commands(commands, env)
        self.assertIn("Command failed with error:", mock_stdout.getvalue())

    @override_settings(DEBUG=False)
    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    @mock.patch("sys.exit")
    @mock.patch("apps.main.management.commands.restore_db.input", return_value="y")
    def test_handle_with_debug_false(self, mock_input, mock_exit, mock_exists):
        """
        Test that the handle method exits when DEBUG is set to False.
        """
        call_command("restore_db")
        mock_exit.assert_called_once_with(1)

    @mock.patch("sys.exit")
    @mock.patch(
        "apps.main.management.commands.restore_db.Command.generate_source_commands",
        return_value=[],
    )
    @mock.patch(
        "apps.main.management.commands.restore_db.Command.generate_target_commands",
        return_value=[],
    )
    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch("apps.main.management.commands.restore_db.input", return_value="y")
    def test_handle_no_commands(
        self,
        mock_input,
        mock_stdout,
        mock_target_commands,
        mock_source_commands,
        mock_exit,
    ):  # pylint: disable=too-many-arguments
        """
        Test that the handle method exits with no commands message when no commands are available.
        """
        call_command("restore_db", source="test", target="local")
        self.assertIn(NO_COMMANDS_MESSAGE, mock_stdout.getvalue())
        mock_exit.assert_called_once_with(0)

    def test_generate_source_commands_local_source(self):
        """Test with 'local' source which should not generate commands."""
        commands = self.command.generate_source_commands("local", "file.dump")
        self.assertEqual(commands, [])

    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=True
    )
    @mock.patch("apps.main.management.commands.restore_db.input", return_value="n")
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_generate_source_commands_file_exists_user_declines(
        self, mock_stdout, mock_input, mock_exists
    ):
        """Test file exists and user declines to override."""
        with mock.patch("sys.exit") as mock_exit:
            command = Command()
            command.generate_source_commands("test", "file.dump")
            mock_exit.assert_called_once_with(0)
            self.assertIn("Not overriding file.dump. Exiting.", mock_stdout.getvalue())

    @mock.patch(
        "apps.main.management.commands.restore_db.os.path.exists", return_value=False
    )
    def test_generate_source_commands_file_does_not_exist(self, mock_exists):
        """Test file does not exist, should generate command."""
        commands = self.command.generate_source_commands("test", "file.dump")
        self.assertEqual(len(commands), 1)
        self.assertIn("pg_dump -Fc -v --host=", commands[0])
