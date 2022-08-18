from django.db import models

class Student(models.Model):
    Student_first_name = models.CharField(max_length=30, verbose_name='First Name') # verbose_name is used to display the name of the field in the admin panel.
    #Student_middle_name = models.CharField(max_length=30, null=True,requried=False, verbose_name="Middle Name")
    Student_last_name = models.CharField(max_length=30, verbose_name='Last Name')
    Student_UPI = models.CharField(max_length=10,  verbose_name='UPI')
    Student_email = models.EmailField(max_length=254, verbose_name='Email')

    def __str__(self):
        return "{} {}".format(self.Student_first_name, self.Student_last_name)


    class Meta:
        db_table = 'Student'
        verbose_name = 'Student Management System'


