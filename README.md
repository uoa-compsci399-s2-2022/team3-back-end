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
$ source ./venv/Scripts/activate
$ pip install -r requirements.txt
```
#### MacOS
```shell
$ virtualenv venv
$ source ./venv/Scripts/activate
$ pip install -r requirements.txt
```
#### Windows Powershell
```shell
$ virtualenv venv
$ .\\venv\Scripts\activate
$ pip install -r requirements.txt
```

When using PyCharm for requirements installation, set the virtual environment using 'File'->'Settings' and select your project from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment. 

## Application procedure
1. After the user clicks to start an application, the `/api/newApplication` need to be called.
2. The current application can be saved via `/api/saveApplication/{application_id}` API.
3. The application can be submitted via `/api/submitApplication/{application_id}` API. The backend server will check whether the content submitted by this application meets the requirements
