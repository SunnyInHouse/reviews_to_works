from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_kwargs):
        if not email:
            raise ValueError("Укажите e-mail для создания пользователя.")
        if not username:
            raise ValueError("Укажите username для создания пользователя")
        extra_kwargs.setdefault("role", "user")
        extra_kwargs.setdefault("is_staff", False)
        extra_kwargs.setdefault("is_active", False)
        extra_kwargs.setdefault("is_superuser", False)
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_kwargs):
        if password is None:
            raise TypeError("Superusers must have a password.")
        extra_kwargs.setdefault("role", "admin")
        extra_kwargs.setdefault("is_staff", True)
        extra_kwargs.setdefault("is_active", True)
        extra_kwargs.setdefault("is_superuser", True)

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user
        # extra_fields.setdefault("is_staff", True)
        # extra_fields.setdefault("is_superuser", True)

        # if extra_fields.get("is_staff") is not True:
        #     raise ValueError("Значение поля is_staff должно быть True.")
        # if extra_fields.get("is_superuser") is not True:
        #     raise ValueError("Значение поля is_superuser должно быть True.")

        # return self.create_user(username, email, password, **extra_fields)
