from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, face_data, password=None):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, face_data=face_data)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, username, face_data, password=None):
        user = self.create_user(username, face_data, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)  
    face_data = models.JSONField()  


    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = []  
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)  
    date_joined = models.DateTimeField(auto_now_add=True)  

    objects = UserManager() 

    def save_face_encoding(self, face_encoding):
        self.face_data = face_encoding
        self.save()

    def __str__(self):
        return self.username



class UserData(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_data")
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
