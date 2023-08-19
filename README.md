# Django-Template
A Python Django Application to get started quickly

## Setup
The application assumes you will have a main or core piece of the application
the default name for that is main but you can of course change it to whatever you want. 
Just be sure to change it in the settings and app files 

The template assumes you have 3 branches for the deployment process.
<ul>
<li>test</li>
<li>develop</li>
<li>production</li>
</ul>

Its made this way for github actions to work on each push to those branches

To start the docker container with the application you only need 1 command


```
docker compose up --build
```

## Things you may consider replacing

<ul>
<li>The name of the root django project is called "DjangoTemplate". You would need to change it in settings.py file as well</li>
<li>The container name for the app is called djangoTemplate. You may want to change that as well</li>
<li>The first django "app" is main if you want to change that you'll need to change it in settings</li>
</ul>


## How to Use `restore_local_db` Management Command

The `restore_local_db` management command allows developers to handle database dumps conveniently for local development. With this command, you can manage and control various database options such as source and target environments, filename, drop and restore flags, copy media, and more.

### Usage

```bash
python manage.py restore_local_db [options]
```

### Options

- `-s`, `--source`: Indicates the source database for the dump file. Options are `local`, `test`, `develop`, `production`. If no source is given, it will try to use an existing dump.
- `-t`, `--target`: Indicates the target database for loading the dump file. Options are `local`, `test`, `develop`.
- `-f`, `--file-name`: Specifies the name of the dump file. Default is `restore.dump`.
- `-nd`, `--no-drop`: Use this flag if you don't want to drop the database.
- `-nr`, `--no-restore`: Use this flag if you don't want to restore the database.
- `-cp`, `--copy-media`: Use this flag if you want to copy media to the destination.
- `--no-input`: Use this flag to skip user prompts.

### Examples

1. **Creating a Dump from Develop Environment and Restoring to Local**
   ```bash
   python manage.py restore_local_db --source develop --target local
   ```

2. **Restoring from an Existing Dump File without Dropping the Database**
   ```bash
   python manage.py restore_local_db --file-name existing_dump.dump --no-drop
   ```

3. **Creating a Dump from Production and Restoring to Test with Media Copy**
   ```bash
   python manage.py restore_local_db --source production --target test --copy-media
   ```

### When to Use

This command is highly beneficial in the following scenarios:

- **Development Setup**: Quickly clone the production or any other environment database to your local setup for development and testing.
- **Testing Environment Sync**: Keep your testing environments up-to-date with the production data by creating and restoring dumps.
- **Backup Management**: Create dumps of your databases periodically for backup purposes.

**Note**: This command is intended for local development, and precautions should be taken not to run it on live servers. The code includes checks to prevent misuse.

By leveraging this command, you can maintain consistent and up-to-date data across various environments, facilitating a smooth development and testing process.