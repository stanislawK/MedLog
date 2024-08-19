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

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable()
