eConnect Backend
==========

The backend for eConnect is a Python Flask app that creates an API for the iOS app to use.
It's database uses sqlite3 and has 2 tables, 'users' and 'interactions'.
The backend also implements an administration panel that is served by Flask. The admin panel can start and stop the service aswell as clear the database.

##Installation
###Clone this repository using your ISID
```
git clone https://<ISID>@stash.merck.com/scm/ec/econnect_backend.git
```
###sqlite3
Make sure the \*nix enviroment you are installing on has the latest version of sqlite3.
###Flask (Taken from Flask documentation)
1. Before we install Flask, we need to make sure virtualenv is installed. (User whichever package manager is availbile)
```
sudo easy_install virtualenv
```
Then init a virtual environment
```
$ mkdir myproject
$ cd myproject
$ virtualenv venv
New python executable in venv/bin/python
Installing distribute............done.
```
And activate it
```
$ . venv/bin/activate
```
2. Using pip, install the latest version of Flask
```
pip install Flask
```
###Other python dependencies
1. Using pip, install other python dependencies
```
+Flask-Bcrypt==0.6.2
+Flask-Login==0.2.11
+Flask-WTF==0.12
+gunicorn==19.3.0
+itsdangerous==0.24
+Jinja2==2.7.3
+MarkupSafe==0.23
+python-bcrypt==0.3.1
+Werkzeug==0.10.4
+wheel==0.24.0
+WTForms==2.0.2
```
##Running and other configuration changes
###DEBUG
By default, the DEBUG flag is turned on. This is good for development, but needs to be off when running in a production environment for security reasons.
```python
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'database.db'),
    DEBUG = True
))
```
Changes to
```python
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'database.db'),
    DEBUG = False
))
```
in server.py
###Running
To start the service, invoke 'gunicorn server:app' in the root of the project. The output should tell you where the service can be reached.
