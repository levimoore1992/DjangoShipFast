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
<li>In django_template.dev_utils line 99 replace the url in the code with your actual production url for media</li>
<li>Change the value in 'meta_tags.html' to reflect what you want for you application</li>
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

You may also need to edit some sql files depending on the setup of your database. Because you may need to change the role name from 'web' to a more appropriate name

### Google Captcha
To use google captcha you will need to create a google captcha account at google.com/recaptcha and get a secret key and site key.
Once you have those keys you will need to add them to the .env file.

### Codecov
To use codecov you will need to create a codecov account at codecov.io and get a secret key.
Once you have that key you will need to add it to the github repo in secrets

You will also need to create an account at codecov.io and add the repo to your account
In the code coverage commands be sure to add any new apps you create to the command


## Using Pylint in Our Django Project
### Local Execution:
To lint your Django apps and other relevant Python directories, run the following command:

```
make lint
```
This command explicitly specifies which directories should be linted.

### GitHub Actions:
Our GitHub Action for linting also uses a similar command. 
If you add a new Django app or a directory containing Python files that should be linted, remember to update the GitHub Action configuration.

### Google Admin SSO
For admin login we use admin sso library to make sure an attacker cant just get in with a password list. To enable it locally follow these instructions

## Getting Credentials for Django Admin SSO from the Google Developer Console

### Create a Project in Google Developer Console

1. Go to the [Google Developer Console](https://console.developers.google.com/).
2. Click on "Select a project" and then "New Project".
3. Enter the project name and create it.

### Enable the Google+ API

1. Once the project is created, go to the "Library" tab.
2. Search for "Google+ API" and enable it.

### Create OAuth 2.0 Credentials

1. Go to the "Credentials" tab.
2. Click on "Create Credentials" and select "OAuth 2.0 Client ID".
3. You might be prompted to configure the consent screen. Fill out the required fields such as application name, support email, etc.
4. For the application type, select "Web application".
5. Set the authorized redirect URIs. This should be your Django application's URL where you handle the OAuth callback, e.g., `http://localhost:8000/accounts/google/login/callback/`.

### Important Note:
After creating your app, you dont need to update the app as long as you place your app in the apps directory


### Features
- [x] Dockerized
- [x] Django 5.0
- [x] Python 3.12
- [x] Tailwind CSS
- [x] Business Pages such as Contact, Privacy Policy, Terms of Service, FAQs
- [x] User Blocking and Tracking with IP address and device agent
- [x] All apps moved to an apps folder
- [x] Makefile for easy commands
- [x] Meta Tags in meta_tags.html
- [x] django-celery-beat for periodic tasks
- [x] User Login Create and Logout Features
- [x] Custom User Model with Avatar field for profile pictures
- [x] User Tracking IP Address and devices
- [x] Built in linters with black and flake8 as well as commands in makefile
- [x] django-auto-prefetching for better performance
- [x] django-htmx for better user experience
- [x] Media Library Mixin to save images automatically
- [x] Comment Model easy to attach to other models
- [x] Pagination component easily attachable to a list view
- [x] Path to have icon show on apple devices and tab icon set up





