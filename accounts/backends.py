from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    """Resolve an exact username first, then an unambiguous email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            # Django's default User does not require emails to be unique.
            matches = list(User._default_manager.filter(email__iexact=username)[:2]) if username else []
            if len(matches) != 1:
                # Match Django's password-hashing work for unknown identities.
                User().set_password(password)
                return None
            user = matches[0]

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
