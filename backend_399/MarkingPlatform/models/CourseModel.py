from django.db import models

# from MarkingPlatform.models.SemesterModel import Semester


class Course(models.Model):
    '''
        :parameter
            Semester choice field:
                0 : Summer Semester
                1 : First Semester
                2 : Second Semester
                -1 : Not Selected, default value
    '''

    Semester_CHOICES = (
        (0, 'Summer Semester'),
        (1, 'Semester One'),
        (2, 'Semester Two'),
        (-1, 'null'),
    )

    Course_id = models.BigAutoField(primary_key=True)
    Course_code = models.CharField(max_length=30, verbose_name='Course Code', unique=True, null=False)
    Course_name = models.CharField(max_length=30, unique=True)
    #Course_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=False) #级联删除
    Course_semester = models.IntegerField(choices=Semester_CHOICES, default=-1)


    # View in admin panel (management panel)
    def __str__(self):
        return '{} | {} | Semester:{}'.format(self.Course_code, self.Course_name, self.Semester_CHOICES[self.Course_semester][1])

    class Meta:
        db_table = 'Course'