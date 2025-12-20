# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to save first_name during registration.
    """

    def save_user(self, request, user, form, commit=True):
        """
        Save the user with first_name from signup form.
        """
        user = super().save_user(request, user, form, commit=False)

        # Get first_name from the form data
        first_name = form.cleaned_data.get("first_name", "")
        if first_name:
            user.first_name = first_name

        if commit:
            user.save()

        return user
