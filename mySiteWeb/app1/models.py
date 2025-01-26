from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.CharField(max_length=100)
    participants = models.IntegerField()
    participant1 = models.EmailField(default='default@example.com')
    participant2 = models.EmailField(default='default@example.com')
    participant3 = models.EmailField(blank=True, null=True)
    participant4 = models.EmailField(blank=True, null=True)
    terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.room} - {self.start_time}"
    


class AdminManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Les administrateurs doivent avoir un nom d\'utilisateur')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Admin(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = AdminManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin