from django.contrib import admin
from .models import User_Model
# Register your models here.
admin.site.register(User_Model.User)
admin.site.register(User_Model.Users_roles)
admin.site.register(User_Model.Role)