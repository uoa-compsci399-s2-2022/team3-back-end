from  django.urls import path, include
from MarkingPlatform.Views import views_student




urlpatterns = [
    path('uploadStudent/', views_student.Upload_A_Student.as_view()),
    path('getAllStudents/', views_student.Get_All_Students.as_view()),
]