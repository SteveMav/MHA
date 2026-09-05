from io import StringIO
import logging
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Profile


@override_settings(DEBUG=False)
class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'Test-only-password-839!'
        cls.admin = User.objects.create_superuser(
            username='coach', email='coach@example.com', password=cls.password,
        )

    def sign_in(self, identifier, password=None):
        return self.client.post(reverse('login'), {
            'username': identifier,
            'password': password or self.password,
        }, follow=True)

    def test_superadmin_without_profile_can_log_in_with_username(self):
        self.assertFalse(Profile.objects.filter(user=self.admin).exists())
        response = self.sign_in('coach')
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(Profile.objects.filter(user=self.admin).count(), 1)

    def test_superadmin_can_log_in_with_email(self):
        response = self.sign_in('COACH@example.com')
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin.pk)

    def test_invalid_credentials_are_rejected(self):
        for identifier in ['coach', 'coach@example.com', 'unknown@example.com']:
            with self.subTest(identifier=identifier):
                response = self.sign_in(identifier, 'wrong-password')
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
                self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_account_is_rejected(self):
        self.admin.is_active = False
        self.admin.save()
        for identifier in ['coach', 'coach@example.com']:
            with self.subTest(identifier=identifier):
                self.sign_in(identifier)
                self.assertNotIn('_auth_user_id', self.client.session)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user('other', email='COACH@example.com', password=self.password)
        response = self.sign_in('coach@example.com')
        self.assertTrue(response.context['form'].errors)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_exact_username_takes_precedence_over_another_users_email(self):
        owner = User.objects.create_user('coach@example.com', password='Owner-password-839!')
        self.sign_in('coach@example.com')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.sign_in('coach@example.com', 'Owner-password-839!')
        self.assertEqual(int(self.client.session['_auth_user_id']), owner.pk)

    def test_existing_profile_is_preserved(self):
        profile = Profile.objects.create(user=self.admin, telephone='+243123456789')
        self.sign_in('coach')
        self.client.get(reverse('profile'))
        profile.refresh_from_db()
        self.assertEqual(profile.telephone, '+243123456789')
        self.assertEqual(Profile.objects.filter(user=self.admin).count(), 1)

    def test_unrecognized_profile_post_does_not_crash(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('profile'), {})
        self.assertEqual(response.status_code, 400)

    def test_anonymous_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('profile'))

    def test_member_registration_still_creates_one_profile(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Test', 'last_name': 'Member',
            'email': 'member@example.com', 'password': self.password,
            'confirm_password': self.password, 'date_naissance': '2000-01-01',
            'telephone': '+243123456789',
        })
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)
        member = User.objects.get(username='member@example.com')
        self.assertEqual(Profile.objects.filter(user=member).count(), 1)
        self.client.logout()
        self.assertRedirects(self.sign_in('member@example.com'), reverse('profile'))

    def test_non_staff_cannot_access_admin(self):
        member = User.objects.create_user('member', password=self.password)
        self.client.force_login(member)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('admin:login')))

    def test_superadmin_can_access_admin(self):
        self.sign_in('coach')
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 200)

    def test_admin_login_accepts_email(self):
        response = self.client.post(reverse('admin:login'), {
            'username': 'coach@example.com', 'password': self.password,
            'next': reverse('admin:index'),
        }, follow=True)
        self.assertRedirects(response, reverse('admin:index'))

    def test_profile_update_creates_only_the_current_users_profile(self):
        other = User.objects.create_user('other')
        self.client.force_login(self.admin)
        response = self.client.post(reverse('profile'), {
            'update_profile': '1', 'first_name': 'Coach', 'last_name': 'Magic',
            'email': 'coach@example.com', 'telephone': '+243123456789',
            'user': other.pk,
        })
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(Profile.objects.get(user=self.admin).telephone, '+243123456789')
        self.assertFalse(Profile.objects.filter(user=other).exists())

    def test_server_error_is_logged_without_exposing_debug_page(self):
        self.client.force_login(self.admin)
        self.client.raise_request_exception = False
        stream = StringIO()
        handler = logging.getLogger('django').handlers[0]
        with patch.object(handler, 'stream', stream), patch(
            'accounts.views.Profile.objects.get_or_create',
            side_effect=RuntimeError('test diagnostic marker'),
        ):
            response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 500)
        self.assertNotContains(response, 'test diagnostic marker', status_code=500)
        self.assertIn('Traceback', stream.getvalue())
        self.assertIn('test diagnostic marker', stream.getvalue())
