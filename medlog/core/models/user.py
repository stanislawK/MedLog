from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(
        self,
        *,
        email: str,
        password: str,
        is_active: bool,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ) -> "User":
        if not email:
            raise ValueError(_("The email must be set"))
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email: str, password: str, **extra_fields) -> "User":
        return self._create_user(
            email=email,
            password=password,
            is_active=False,
            is_staff=False,
            is_superuser=False,
            **extra_fields,
        )

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        return self._create_user(
            email=email,
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
