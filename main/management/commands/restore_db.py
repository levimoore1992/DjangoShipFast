import os
import subprocess
from typing import Dict, List

from django.conf import settings
from django.core.management import BaseCommand


def create_command(db_config: Dict[str, str], command_template: str, *args) -> str:
    """
    Create a command based on the command template and given arguments.

    Args:
        db_config (Dict[str, str]): Database configuration.
        command_template (str): Command template.
        *args: Additional arguments for the command template.

    Returns:
        str: Formatted command.
    """
    return command_template.format(
        db_config["host"], db_config["username"], db_config["dbname"], *args
    )


ERROR_CANNOT_DUMP_PROD = "Cannot dump into production."
ERROR_DB_NOT_VALID = "{} is not a valid {}. Available options: {}"
ERROR_SAME_DB = "Source and target databases are the same. Exiting."
ERROR_BACKUP_FILE_MISSING = "The backup file '{}' does not exist. Exiting."
WARNING_ON_LIVE_SERVER = "Running the `restore_local_db` command on a live server."
NO_COMMANDS_MESSAGE = "No commands to be run. Exiting."
CONFIRM_RUN_COMMANDS = "\nThe following commands will be run:"


class Command(BaseCommand):
    help = (
        "A management command to restore the database from a source database to a targeted database excluding "
        "production."
    )

    DATABASE_CONFIG: Dict[str, Dict[str, str]] = {
        "local": {
            "host": os.environ.get("DB_HOST"),
            "dbname": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASS"),
        },
        "test": {
            "host": os.environ.get("TEST_DB_HOST"),
            "dbname": os.environ.get("TEST_DB_NAME"),
            "username": os.environ.get("TEST_DB_USER"),
            "password": os.environ.get("TEST_DB_PASSWORD"),
        },
        "develop": {
            "host": os.environ.get("DEV_DB_HOST"),
            "dbname": os.environ.get("DEV_DB_NAME"),
            "username": os.environ.get("DEV_DB_USER"),
            "password": os.environ.get("DEV_DB_PASSWORD"),
        },
        "production": {
            "host": os.environ.get("PROD_DB_HOST"),
            "dbname": os.environ.get("PROD_DB_NAME"),
            "username": os.environ.get("PROD_DB_USER"),
            "password": os.environ.get("PROD_DB_PASSWORD"),
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            required=False,
            help="Indicates what database you want to get the dump file from, "
            "options are local, test, develop, production.",
            default=None,
        )

        parser.add_argument(
            "-t",
            "--target",
            type=str,
            help="Indicates what database you want to load the dump file to, "
            "options are local, test, develop",
            default="local",
        )

        parser.add_argument(
            "-f",
            "--file-name",
            type=str,
            help="Name of the dumpfile",
            default="restore.dump",
        )
        parser.add_argument(
            "-nd",
            "--no-drop",
            help="Flag if you dont want to drop the db",
            dest="drop",
            action="store_false",
        )
        parser.add_argument(
            "-nr",
            "--no-restore",
            help="Flag if you dont want to restore the db",
            dest="restore",
            action="store_false",
        )

        parser.add_argument(
            "-cp",
            "--copy-media",
            help="Flag if you also want to copy media to your destination.",
            action="store_true",
        )

        parser.add_argument(
            "--no-input",
            help="Skip user prompts. Does not skip entering passwords for non local databases.",
            action="store_true",
        )

    def validate_arguments(self, source: str, target: str, file_name: str) -> None:
        """
        Validate the provided command arguments and exit if they are not valid.
        """
        available_dbs = self.DATABASE_CONFIG.keys()

        if target == "production":
            self.stdout.write(ERROR_CANNOT_DUMP_PROD)
            exit(1)

        if target not in available_dbs:
            self.stdout.write(
                ERROR_DB_NOT_VALID.format(target, "target", ", ".join(available_dbs))
            )
            exit(1)

        if source:
            if source not in available_dbs:
                self.stdout.write(
                    ERROR_DB_NOT_VALID.format(
                        source, "source", ", ".join(available_dbs)
                    )
                )
                exit(1)
            if source == target:
                self.stdout.write(ERROR_SAME_DB)
                exit(0)
        else:
            if not os.path.exists(file_name):
                self.stdout.write(ERROR_BACKUP_FILE_MISSING.format(file_name))
                exit(1)

    def run_commands(self, commands: List[str], env: Dict) -> None:
        """
        Execute the given commands.
        """
        for command in commands:
            try:
                subprocess.check_call(command, env=env, shell=True)
            except subprocess.CalledProcessError as e:
                self.stdout.write(f"Command failed with error: {e}")

    def handle(self, *args, **kwargs):
        """
        Handle the management command.
        """
        if not settings.DEBUG:
            self.stdout.write(WARNING_ON_LIVE_SERVER)
            exit(1)

        source = kwargs["source"]
        target = kwargs["target"]
        file_name = kwargs["file_name"]

        self.validate_arguments(source, target, file_name)

        source_commands = self.generate_source_commands(source, file_name)
        target_commands = self.generate_target_commands(target, kwargs, file_name)

        all_commands = source_commands + target_commands
        if not all_commands:
            self.stdout.write(NO_COMMANDS_MESSAGE)
            exit(0)

        self.stdout.write(CONFIRM_RUN_COMMANDS)
        for command in all_commands:
            self.stdout.write(f"\t- {command}")

        if (
            not kwargs["no_input"]
            and input("Would you like to continue? (y/n) ").lower() != "y"
        ):
            self.stdout.write("Exiting.")
            exit(0)
        if source:
            self.run_commands(source_commands, self.get_env_for_db(source))
        self.run_commands(target_commands, self.get_env_for_db(target))

    def generate_source_commands(self, source: str, file_name: str) -> List[str]:
        """
        Generate the source commands based on the provided source and file_name.
        """
        source_commands = []
        if source and source != "local":
            if os.path.exists(file_name):
                prompt = f"Do you want to override {file_name}? (y/n) "
                if input(prompt).lower() != "y":
                    self.stdout.write(f"Not overriding {file_name}. Exiting.")
                    exit(0)

            command_template = (
                "pg_dump -Fc -v --host={} --username={} --dbname={} -f {}"
            )
            source_commands.append(
                create_command(
                    self.DATABASE_CONFIG[source], command_template, file_name
                )
            )
        return source_commands

    def generate_target_commands(
        self, target: str, kwargs: Dict, file_name: str
    ) -> List[str]:
        """
        Generate the target commands based on the provided target, kwargs, and file_name.
        """
        target_commands = []
        if kwargs["drop"] and kwargs["restore"]:
            command_template = (
                "psql --host={} --port=5432 --username={} --dbname={} -f {}"
            )
            drop_table_path = os.path.join(
                settings.BASE_DIR, "main/management/commands/sql/drop_tables.sql"
            )
            target_commands.append(
                create_command(
                    self.DATABASE_CONFIG[target], command_template, drop_table_path
                )
            )

        if kwargs["restore"]:
            command_template = (
                "psql --host={} --port=5432 --username={} --dbname={} -f {}"
            )
            setup_path = os.path.join(
                settings.BASE_DIR, "main/management/commands/sql/setup.sql"
            )
            target_commands.append(
                create_command(
                    self.DATABASE_CONFIG[target], command_template, setup_path
                )
            )

            command_template = "pg_restore -v  --no-owner --host={} --port=5432 --username={} --dbname={} {}"
            target_commands.append(
                create_command(
                    self.DATABASE_CONFIG[target], command_template, file_name
                )
            )

        return target_commands

    def get_env_for_db(self, db_name: str) -> Dict:
        """
        Get the environment for the provided database name.
        """
        env = os.environ.copy()
        env["PGPASSWORD"] = self.DATABASE_CONFIG[db_name]["password"]
        return env
