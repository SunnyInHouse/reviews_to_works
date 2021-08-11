from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("Укажите e-mail для создания пользователя.")
        if not username:
            raise ValueError("Укажите username для создания пользователя")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else: 
            user.make_random_password(length=10,
                allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Значение поля is_staff должно быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Значение поля is_superuser должно быть True.")

        return self.create_user(username, email, password, **extra_fields)
