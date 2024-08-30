import logging

from medlog.settings import *  # noqa: F403, F401

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "MIGRATE": False,
        },
    }
}

SECRET_KEY = "test_secret_key"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable()
