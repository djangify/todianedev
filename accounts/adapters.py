# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Ensure the user's first_name is saved during registration.

    The custom signup template posts first_name directly, so if allauth's own
    signup fields didn't capture it we copy it across from the POST data before
    saving.
    """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        if not user.first_name:
            first_name = request.POST.get("first_name", "").strip()
            if first_name:
                user.first_name = first_name

        if commit:
            user.save()

        return user
