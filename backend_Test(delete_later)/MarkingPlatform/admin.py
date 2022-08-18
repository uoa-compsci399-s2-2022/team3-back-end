from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models.StudentModel import Student
#from .models.SemesterModel import Semester
from .models.CourseModel import Course

admin.site.register(Student)
#admin.site.register(Semester)
admin.site.register(Course)