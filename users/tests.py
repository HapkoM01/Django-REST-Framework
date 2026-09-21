from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User, Payment
from materials.models import Course, Lesson


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            phone='+79001112233',
            city='Москва',
        )
        self.other = User.objects.create_user(
            email='other@test.com',
            password='password123',
            city='Казань',
        )
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='password123',
        )
        group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            title='DRF Course', description='desc', owner=self.user
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Lesson 1',
            video_url='https://www.youtube.com/watch?v=abc',
            owner=self.user,
        )


# ─── Auth ───────────────────────────────────────────────────────────

class AuthRegisterTests(BaseAPITestCase):
    def test_register_success(self):
        url = reverse('register')
        data = {
            'email': 'new@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'phone': '+79009998877',
            'city': 'СПб',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            'email': 'new2@test.com',
            'password': 'password123',
            'password_confirm': 'otherpass1',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        url = reverse('register')
        data = {
            'email': 'user@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_no_auth_required(self):
        url = reverse('register')
        data = {
            'email': 'free@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthTokenTests(BaseAPITestCase):
    def test_obtain_token(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'user@test.com',
            'password': 'password123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_wrong_password(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'user@test.com',
            'password': 'wrong',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        obtain = self.client.post(reverse('token_obtain_pair'), {
            'email': 'user@test.com',
            'password': 'password123',
        }, format='json')
        refresh = obtain.data['refresh']
        response = self.client.post(reverse('token_refresh'), {
            'refresh': refresh,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


# ─── Users ──────────────────────────────────────────────────────────

class UserEndpointTests(BaseAPITestCase):
    def test_list_users_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # публичные данные — без payments
        first = response.data[0] if isinstance(response.data, list) else response.data['results'][0]
        self.assertNotIn('payments', first)

    def test_list_users_unauthenticated(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_profile_has_payments(self):
        Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=Decimal('1000.00'),
            payment_method=Payment.CASH,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('payments', response.data)

    def test_retrieve_other_profile_public(self):
        Payment.objects.create(
            user=self.other,
            paid_course=self.course,
            amount=Decimal('500.00'),
            payment_method=Payment.TRANSFER,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('user-detail', args=[self.other.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('payments', response.data)

    def test_update_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('user-detail', args=[self.user.id]),
            {'city': 'Новосибирск'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, 'Новосибирск')

    def test_update_other_profile_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('user-detail', args=[self.other.id]),
            {'city': 'Hack'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_other_profile_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('user-detail', args=[self.other.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ─── Payments ───────────────────────────────────────────────────────

class PaymentEndpointTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=Decimal('5000.00'),
            payment_method=Payment.TRANSFER,
        )
        self.payment2 = Payment.objects.create(
            user=self.other,
            paid_lesson=self.lesson,
            amount=Decimal('300.00'),
            payment_method=Payment.CASH,
        )

    def test_list_payments(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_payments_unauthenticated(self):
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_payment(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'user': self.user.id,
            'paid_course': self.course.id,
            'amount': '1500.00',
            'payment_method': 'cash',
        }
        response = self.client.post(reverse('payment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-detail', args=[self.payment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '5000.00')

    def test_update_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('payment-detail', args=[self.payment.id]),
            {'amount': '6000.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('payment-detail', args=[self.payment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_by_course(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-list'), {'paid_course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        for item in results:
            self.assertEqual(item['paid_course'], self.course.id)

    def test_filter_by_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-list'), {'paid_lesson': self.lesson.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_payment_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-list'), {'payment_method': 'cash'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        for item in results:
            self.assertEqual(item['payment_method'], 'cash')

    def test_ordering_by_payment_date(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('payment-list'), {'ordering': 'payment_date'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_desc = self.client.get(reverse('payment-list'), {'ordering': '-payment_date'})
        self.assertEqual(response_desc.status_code, status.HTTP_200_OK)
