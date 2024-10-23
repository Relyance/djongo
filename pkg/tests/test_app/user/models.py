from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        #
        if not email:
            raise ValueError("Users must have an email address")
        email = email.lower()
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        #extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email               = models.EmailField(verbose_name='email address', max_length=254, unique=True)
    first_name          = models.CharField(verbose_name='first name', max_length=30, blank=True)
    last_name           = models.CharField(verbose_name='last name', max_length=30, blank=True)
    username            = models.CharField(max_length=50, blank=True)
    user_type           = models.CharField(max_length=50, blank=True, default="")

    last_login          = models.DateTimeField(verbose_name='last login', auto_now_add=True)

    is_active           = models.BooleanField(default=True)
    is_staff            = models.BooleanField(default=False)
    is_superuser        = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        permissions = [
            ("can_view", "can view"),
            ("can_edit", "can edit"),
            ("can_admin", "can admin"),
        ]
