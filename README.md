# MTMS Backend
Marker & Tutor Management System - One COMPSCI399 Project

The University of Auckland

---

## Setup Development Environment
### Installation

**Installation via requirements.txt**

#### Linux
```shell
$ virtualenv venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```
#### MacOS
```shell
$ virtualenv venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```
#### Windows Powershell
```shell
$ virtualenv venv
$ .\\venv\Scripts\activate
$ pip install -r requirements.txt
```

When using PyCharm for requirements installation, set the virtual environment using 'File'->'Settings' and select your project from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment. 

### Start Dev Server
```shell
$ flask run
```

### Default Admin User
You can use the admin account to access all modules of the system
```plain
username: admin
password: admin
```

---
## API Documentation
We use swagger as the API documentation, you can log in to http://127.0.0.1:5000/apidocs/ to view after running the development server.


---

## Database Migration
Official documentation: https://alembic.sqlalchemy.org/en/latest/
* set migration
```shell
alembic revision --autogenerate -m "Your Commit Text" 
```
* upgrade database
```shell
alembic upgrade head
```
* downgrade database
```shell
alembic downgrade head
```

---

## Config SMTP Server
You need to run the server first, it will automatically create a .env file in the project root directory. You can edit the .env file to set the SMTP server.
You can find the following configuration items in .env, enter your smtp server related information, and restart the server.
```plain
EMAIL_ACCOUNT=''
EMAIL_PASSWORD=''
EMAIL_SENDER_ADDRESS=''
EMAIL_SERVER_HOST=''
EMAIL_SERVER_PORT=587
EMAIL_SERVER_SSL_PORT=465
EMAIL_SENDER_NAME=""
```

---

## Config Sentry
Sentry is Application Monitoring and Error Tracking Software.
Official documentation: https://docs.sentry.io/platforms/python/flask/

You need to run the server first, it will automatically create a .env file in the project root directory. You can edit the .env file to set the Sentry.
You can find the following configuration items in .env, enter your Sentry DSN, and restart the server.
```plain
SENTRY_DSN=''
```

---

## Config uWSGI
uWSGI is a fast, self-healing, developer-friendly WSGI server for Python applications. It is used to deploy the application to the production environment.

We have created the uWSGI configuration file, `mtms.ini` in the project root directory.

If you wish to deploy on **linux** you can use uWSGI. Official documentation: https://uwsgi-docs.readthedocs.io/en/latest/

For detailed deployment tutorials, please check: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

---
## Config Database
Our project uses sqlite as the database by default, and sqlite is automatically created when the server is started for the first time. If you wish to deploy this project on a server, we strongly recommend that you use mySQL.

You need to run the server first, it will automatically create a .env file in the project root directory. You can edit the .env file to set database.
You can find the following configuration items in .env, enter your database URL, and restart the server.
```plain
SQLALCHEMY_DATABASE_URI = 'sqlite:///MTMS.db'  
```

