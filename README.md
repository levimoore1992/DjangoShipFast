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
<li>The name of the root django project is called "django_template". You would need to change it in settings.py file as well</li>
<li>The container name for the app is called django_template. You may want to change that as well</li>
<li>The first django "app" is main if you want to change that you'll need to change it in settings</li>
<li>In the github actions the variable to see changed files is called template_diff. You may want to change that based on your app but it isnt required</li>
<li>If you want to change the branch style of your deployment then you would need to change the name of the workflows files to match the branch you want</li>
<li>In the footer change "Your App Name" to its value</li>
<li>Change the colors in source_css/css/base/_colors.scss to be colors reflecting your brand</li>
<li>Change the redis project name in docker-compose.yml</li>
</ul>

### Linters

Before committing your code it is the best practice to run the linters locally, so they
pass code inspection in Github Actions. To do that follow these steps
* In your local machine terminal type 
```
pip3 install black==21.7
pip3 install flake8==4.0.1
```


#### Black

* To run black make sure it is installed locally and from the root directory type
```
black .
```
* To edit on save follow these instructions if your using pycharm
```
https://black.readthedocs.io/en/stable/integrations/editors.html
```
* and here for if your using VScode
```
https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00
```

#### Flake8

* To run flake8 make sure it is installed locally and from the root directory type

```
flake8 --ignore=E501,F405,W503
```
If the above fails you may also try 
```
python3 -m flake8 --ignore=E501,F405,W503
```

After black lints your code, and you make any changes needed from flake 8 it is then ok
to push your code and create a PR

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

You may also need to edit some sql files depending on the setup of your database. Because you may need to change the role name from 'web' to a more appropriate name


## Using Pylint in Our Django Project
### Local Execution:
To lint your Django apps and other relevant Python directories, run the following command:

```
docker exec -it django_template pylint django_template main tests users
```
This command explicitly specifies which directories should be linted.

### GitHub Actions:
Our GitHub Action for linting also uses a similar command. If you add a new Django app or a directory containing Python files that should be linted, remember to update the GitHub Action configuration.



### Important Note:
After creating your app, update the pylint command to include your new app:

```
docker exec -it django_template pylint django_template main tests users your_app_name
```
Also, make sure to update the GitHub Action configuration  and this documentation with the name of the new app.