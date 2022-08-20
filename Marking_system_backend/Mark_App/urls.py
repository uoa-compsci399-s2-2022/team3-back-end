from  django.urls import path, include
from Mark_App.Views import views_user

urlpatterns = [
    path('uploadUser/', views_user.Upload_A_User.as_view()),
    path('getAllUsers/', views_user.Get_All_Users.as_view()),
]