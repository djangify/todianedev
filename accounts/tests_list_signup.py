from unittest import mock

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

User = get_user_model()


@override_settings(BREVO_API_KEY="k", BREVO_LIST_ID=4)
class ListSignupTests(TestCase):
    def _user(self, subscribed):
        user = User.objects.create_user(email="a@example.com", password="x")
        user.first_name = "Ann"
        user.save()
        user.profile.is_subscribed = subscribed
        user.profile.save()
        return user, EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )

    @mock.patch("accounts.services.brevo.requests.post")
    def test_ticked_and_confirmed_joins_list_4(self, post):
        post.return_value.raise_for_status = lambda: None
        user, ea = self._user(True)
        email_confirmed.send(sender=EmailAddress, request=None, email_address=ea)
        self.assertTrue(post.called)
        self.assertEqual(post.call_args.kwargs["json"]["listIds"], [4])
        self.assertEqual(post.call_args.kwargs["json"]["email"], "a@example.com")

    @mock.patch("accounts.services.brevo.requests.post")
    def test_not_ticked_is_never_added(self, post):
        user, ea = self._user(False)
        email_confirmed.send(sender=EmailAddress, request=None, email_address=ea)
        self.assertFalse(post.called)

    @mock.patch("accounts.services.brevo.requests.post", side_effect=Exception("boom"))
    def test_brevo_failure_does_not_break_confirmation(self, post):
        user, ea = self._user(True)
        email_confirmed.send(sender=EmailAddress, request=None, email_address=ea)
