from django.db import models


class User(models.Model):
    User_UPI = models.CharField(max_length=20, verbose_name='UPI', unique=True, null=False, primary_key=True)
    User_password = models.CharField(max_length=20, verbose_name='Password', null=False)
    User_email = models.EmailField(verbose_name='Email')
    User_first_name = models.CharField(max_length=20, verbose_name='First Name')
    User_last_name = models.CharField(max_length=20, verbose_name='Last Name')
    User_create_at = models.DateTimeField(auto_now_add=True, verbose_name='Create Time')
    User_modify_at = models.DateTimeField(auto_now=False, verbose_name='Modify Time')

    def __str__(self):
        return "{} {}".format(self.User_first_name, self.User_last_name)

    class Meta:
        db_table = 'User'
        verbose_name = 'User Management System'
        # verbose_name_plural = 'User Management System'


class Role(models.Model):
    Role_choices = (
        (0, 'Admin'),
        (1, 'Lecturer'),
        (2, 'student'),
        (3, 'Tutor'),
        (4, 'Marker'),
    )

    Role_id = models.BigAutoField(primary_key=True)

    Role_name = models.IntegerField( choices=Role_choices)
    Role_create_at = models.DateTimeField(auto_now_add=True, verbose_name='Create Time')
    Role_modify_at = models.DateTimeField(auto_now=False, verbose_name='Modify Time')

    def __str__(self):
        return self.Role_name

    class Meta:
        db_table = 'Role'
        verbose_name = 'Role Management System'
        # verbose_name_plural = 'Role Management System'


class Users_roles(models.Model):
    Users_roles_id = models.BigAutoField(primary_key=True, auto_created=False)
    Users_roles_UPI = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    User_role_Role_id = models.ForeignKey(Role, on_delete=models.CASCADE, null=False)
