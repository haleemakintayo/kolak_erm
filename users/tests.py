from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from users.models import Role, Department, Permission

User = get_user_model()


class AuthAndUserAdminTests(APITestCase):

    def setUp(self):
        self.role_admin = Role.objects.create(name="Hospital Admin", code="HOSPITAL_ADMIN")
        self.role_doctor = Role.objects.create(name="Doctor", code="DOCTOR")
        self.department = Department.objects.create(name="General Medicine")

        self.user_password = "SecurePassword123!"
        self.user = User.objects.create_user(
            username="staff_jane",
            email="jane.doe@kolak.com",
            password=self.user_password,
            first_name="Jane",
            last_name="Doe",
            role=self.role_admin,
            department=self.department,
            is_active=True
        )

    def test_login_with_username_success(self):
        url = reverse('auth_login')
        data = {
            "username": "staff_jane",
            "password": self.user_password,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'jane.doe@kolak.com')

    def test_login_with_email_success(self):
        url = reverse('auth_login')
        data = {
            "username": "jane.doe@kolak.com",
            "password": self.user_password,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_password_fails(self):
        url = reverse('auth_login')
        data = {
            "username": "staff_jane",
            "password": "WrongPassword",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_and_logout(self):
        # 1. Login to obtain refresh token
        login_url = reverse('auth_login')
        login_resp = self.client.post(login_url, {"username": "staff_jane", "password": self.user_password})
        refresh_token = login_resp.data['refresh']

        # 2. Refresh access token (rotates refresh token)
        refresh_url = reverse('token_refresh')
        refresh_resp = self.client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_resp.data)

        # 3. Logout using the rotated refresh token
        new_refresh_token = refresh_resp.data.get('refresh', refresh_token)
        logout_url = reverse('token_blacklist')
        logout_resp = self.client.post(logout_url, {"refresh": new_refresh_token})
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

    def test_get_user_profile_me(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('auth_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'staff_jane')

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('auth_change_password')
        data = {
            "old_password": self.user_password,
            "new_password": "NewSecretPassword123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Re-authenticate with new password
        self.client.logout()
        login_url = reverse('auth_login')
        login_resp = self.client.post(login_url, {"username": "staff_jane", "password": "NewSecretPassword123!"})
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    def test_user_staff_crud(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-list')

        # Create staff user
        create_data = {
            "username": "dr_john",
            "email": "john.smith@kolak.com",
            "password": "DoctorPassword123!",
            "first_name": "John",
            "last_name": "Smith",
            "role": str(self.role_doctor.id),
            "department": str(self.department.id),
        }
        response = self.client.post(url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['employee_id'].startswith('EMP-'))

        # Toggle status
        user_id = response.data['id']
        toggle_url = reverse('user-toggle-status', kwargs={'pk': user_id})
        toggle_resp = self.client.post(toggle_url)
        self.assertEqual(toggle_resp.status_code, status.HTTP_200_OK)
        self.assertFalse(toggle_resp.data['data']['is_active'])

    def test_role_and_department_crud(self):
        self.client.force_authenticate(user=self.user)

        # Create Department
        dept_url = reverse('department-list')
        dept_resp = self.client.post(dept_url, {"name": "ICU", "description": "Intensive Care Unit"})
        self.assertEqual(dept_resp.status_code, status.HTTP_201_CREATED)

        # Create Role
        role_url = reverse('role-list')
        role_resp = self.client.post(role_url, {"name": "Surgeon", "code": "SURGEON"})
        self.assertEqual(role_resp.status_code, status.HTTP_201_CREATED)
