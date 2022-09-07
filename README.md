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


## Application information category
* `userProfile` Basic user information, including userID, name, email. Students and teachers are required to fill in.
* `studentPersonalDetail` Student personal information required for the application. 
Personal details include:
  1. **Academic record** (pdf-file) -submit in another API
  2. **CV** (pdf-file) -submit in another API
  3. **Name**
  4. **UPI**
  5. **AUID**
  6. **Preferred email**
  7. **Currently overseas** (y/n) – if yes, will come arrive back in NZ?
  8. **Citizen or permanent resident** (y/n) – if not, does applicant have a valid work visa?
  9. **Enrolment details for the semester** (degree / year - e.g. 2nd year BSc, 1st year PhD, etc.)
  10. **Undergraduate or postgraduate student** (add note that “postgraduate” means that student has already completed a degree)
  11. **Any other TA/GTA contracts for that semester** (yes/no – if yes, text field for description of contracts)
  12. **Maximum number of hours/week they want to work** (integer – minimum 5)
* `course` Courses the student wishes to apply for in this application.  
course include:
  1. The grade they got when doing the course themselves
  2. If applicant hasn’t done course before, e.g. overseas students, an explanation why they are qualified (text field)
  3. Relevant previous experience (e.g. has marked/tutored that course before or a similar course overseas – text field)


