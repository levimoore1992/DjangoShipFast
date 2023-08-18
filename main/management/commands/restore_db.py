import logging
import os
import subprocess

from django.conf import settings
from django.core.management import BaseCommand

host_names = {
    "": os.environ.get("DB_HOST"),
    "local": os.environ.get("DB_HOST"),
    "test": os.environ.get("TEST_DB_HOST"),
    "develop": os.environ.get("DEV_DB_HOST"),
    "production": os.environ.get("PROD_DB_HOST")
}

db_names = {
    "local": os.environ.get("DB_NAME"),
    "test": os.environ.get("TEST_DB_NAME"),
    "develop": os.environ.get("DEV_DB_NAME"),
    "production": os.environ.get("PROD_DB_NAME"),
}

usernames = {
    "local": os.environ.get("DB_USER"),
    "test": os.environ.get("TEST_DB_USER"),
    "develop": os.environ.get("DEV_DB_USER"),
    "production": os.environ.get("PROD_DB_USER"),
}

logger = logging.getLogger("management")


class Command(BaseCommand):

    help = """This command is purely for local development because on a clean database these options wont exist"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            help="Indicates what database you want to get the dump file from, "
            "options are local, test-1, test-2, develop, production. If no "
            "source is given, it will first try to use an existing dump. "
            "If no dump is found, one will be created from develop.",
            default="",
        )

        parser.add_argument(
            "-t",
            "--target",
            type=str,
            help="Indicates what database you want to load the dump file to, "
            "options are local, test-1, test-2, qa1, qa2, develop",
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

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            logger.error("Running the `restore_local_db` command on a live server")
            exit()

        # Get arguments or set defaults
        source = kwargs["source"]
        target = kwargs["target"]
        file_name = kwargs["file_name"]

        # ======================================================================
        # Validating command line arguments
        # ======================================================================
        if target == "production":
            print("You cannot dump into production")
            exit()

        if target not in host_names.keys():
            print(
                f"{target} is not a valid name please choose from {', '.join(host_names.keys())}"
            )
            exit()
        if source not in host_names.keys():
            print(
                f"{source} is not a valid name please choose from {', '.join(host_names.keys())}"
            )
            exit()

        if not (source or os.path.exists(file_name)):
            print(
                "Must specify either a --source database or a --file-name that exists"
            )
            print('Try "python manage.py restore_db --source develop"')
            exit()

        # ======================================================================
        # Create "source" commands
        # source commands use the "source" env dictionary, and a ran first.
        # ======================================================================
        source_commands = []
        # Download the file
        if kwargs["source"]:
            if os.path.exists(file_name):
                prompt = f"The file {file_name} already exists do you want to override it? Type 'y' or 'n' "
                if input(prompt) != "y":
                    print(f"Not overriding {file_name}, stopping now.")
                    exit()

            source_commands.append(
                f"pg_dump -Fc -v --host={host_names[source]} --username={usernames[source]} --dbname={db_names[source]} -f {file_name}"
            )

        # Configure postgres passwords and create environments.
        source_password = (
            os.environ.get("DB_PASS")
            if kwargs["source"] in ("local", "")
            else input(f"Enter the password for {source} database ")
        )
        source_env = os.environ.copy()
        source_env["PGPASSWORD"] = source_password

        target_password = (
            os.environ.get("DB_PASS")
            if target == "local"
            else input(f"Enter the password for {target} database ")
        )
        target_env = os.environ.copy()
        target_env["PGPASSWORD"] = target_password


        # ======================================================================
        # Create "target" commands
        # "target_commands" use the "target" env dictionary and a ran after
        # source commands.
        # ======================================================================
        target_commands = []

        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Dropping tables on target database
        if kwargs["drop"] and kwargs["restore"]:
            drop_table_path = os.path.join(current_directory, "sql/drop_tables.sql")

            target_commands.append(
                f"psql --host={host_names[target]} --port=5432 --username={usernames[target]} --dbname={db_names[target]} -f {drop_table_path}"
            )

        # Restoring target database.
        if kwargs["restore"]:
            setup_path = os.path.join(current_directory, "sql/setup.sql")

            target_commands.append(
                f"psql --host={host_names[target]} --port=5432 --username={usernames[target]} --dbname={db_names[target]} -f {setup_path}"
            )
            target_commands.append(
                f"pg_restore -v  --no-owner --host={host_names[target]} --port=5432 --username={usernames[target]} --dbname={db_names[target]} {file_name}"
            )

        # ======================================================================
        # Run commands.
        # ======================================================================
        if len(source_commands + target_commands) == 0:
            print("No commands to be ran")
            exit()

        print("\nThe following commands will be ran:")
        for command in source_commands + target_commands:
            print(f"\t- {command}")

        if kwargs["copy_media"]:
            print(f"\t- Copy media files from production to {target}")

        if not kwargs["no_input"]:
            if input("Would you like to continue? Type 'y' or 'n' ") != "y":
                print("Exiting now")
                exit()

        for command in source_commands:
            subprocess.check_call(command, env=source_env, shell=True)

        for command in target_commands:
            subprocess.check_call(command, env=target_env, shell=True)

