import pytest
from core.models.user import User


@pytest.mark.django_db()
class TestAccountsModelCase:
    def test_user_model(self, user_data: dict):
        user = User.objects.create_user(**user_data)
        assert user.email == user_data["email"]
        assert user.check_password(user_data["password"])
        assert user.password != user_data["password"]
        assert user.is_active is False
        assert user.is_superuser is False
        assert user.is_staff is False

    def test_super_user_model(self, super_user_data: dict):
        superuser = User.objects.create_superuser(**super_user_data)
        assert superuser.email == super_user_data["email"]
        assert superuser.check_password(super_user_data["password"])
        assert superuser.password != super_user_data["password"]
        assert superuser.is_active is True
        assert superuser.is_superuser is True
        assert superuser.is_staff is True
