from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from materials.models import Course, Lesson, Subscription


class BaseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            phone='+79001112233',
            city='Москва',
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='password123',
        )
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='password123',
        )
        group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            title='Test Course',
            description='Description',
            owner=self.user,
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson',
            description='Lesson desc',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            owner=self.user,
        )


# ─── Courses ────────────────────────────────────────────────────────

class CourseCRUDTests(BaseTestCase):
    def test_list_courses_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(len(results) >= 1)

    def test_list_courses_unauthenticated(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_course(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Course', 'description': 'New desc'}
        response = self.client.post(reverse('course-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)
        self.assertIn('lessons_count', response.data)
        self.assertIn('is_subscribed', response.data)

    def test_retrieve_course(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')
        self.assertIn('lessons', response.data)
        self.assertIn('lessons_count', response.data)

    def test_update_course_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('course-detail', args=[self.course.id]),
            {'title': 'Updated Course'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')

    def test_delete_course_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_other_user_cannot_see_foreign_course(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderator_can_list_all_and_update(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            reverse('course-detail', args=[self.course.id]),
            {'title': 'By Moder'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_cannot_create(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(
            reverse('course-list'),
            {'title': 'Moder Course'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ─── Lessons ────────────────────────────────────────────────────────

class LessonCRUDTests(BaseTestCase):
    def test_create_lesson_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'course': self.course.id,
            'title': 'New Lesson',
            'description': 'Desc',
            'video_url': 'https://youtube.com/watch?v=abc123',
        }
        response = self.client.post(reverse('lesson-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_create_lesson_invalid_url(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'course': self.course.id,
            'title': 'Bad URL',
            'video_url': 'https://vimeo.com/12345',
        }
        response = self.client.post(reverse('lesson-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_create_lesson_youtube_ok(self):
        self.client.force_authenticate(user=self.user)
        for url in (
            'https://www.youtube.com/watch?v=abc',
            'https://youtu.be/abc',
            'https://youtube.com/watch?v=xyz',
        ):
            response = self.client.post(reverse('lesson-list-create'), {
                'course': self.course.id,
                'title': f'L {url}',
                'video_url': url,
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=url)

    def test_list_lessons(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lesson-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(len(results) >= 1)

    def test_retrieve_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Lesson')

    def test_update_lesson_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('lesson-detail', args=[self.lesson.id]),
            {'title': 'Updated'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated')

    def test_delete_lesson_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_other_user_cannot_see_foreign_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse('lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderator_can_update_not_create_or_delete(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.patch(
            reverse('lesson-detail', args=[self.lesson.id]),
            {'title': 'By Moder'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('lesson-list-create'), {
            'course': self.course.id,
            'title': 'Moder Lesson',
            'video_url': 'https://youtube.com/watch?v=x',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(reverse('lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_denied(self):
        response = self.client.get(reverse('lesson-list-create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── Subscriptions ──────────────────────────────────────────────────

class SubscriptionTests(BaseTestCase):
    def test_subscribe(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            reverse('subscription-toggle'),
            {'course_id': self.course.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(user=self.other_user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.other_user, course=self.course)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            reverse('subscription-toggle'),
            {'course_id': self.course.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(user=self.other_user, course=self.course).exists()
        )

    def test_is_subscribed_true(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_subscribed_false(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_subscribe_missing_course_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('subscription-toggle'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_unauthenticated(self):
        response = self.client.post(
            reverse('subscription-toggle'),
            {'course_id': self.course.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unique_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        with self.assertRaises(Exception):
            Subscription.objects.create(user=self.user, course=self.course)


# ─── Pagination ─────────────────────────────────────────────────────

class PaginationTests(BaseTestCase):
    def test_courses_paginated(self):
        for i in range(6):
            Course.objects.create(title=f'Course {i}', owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertLessEqual(len(response.data['results']), 5)

    def test_lessons_paginated(self):
        for i in range(6):
            Lesson.objects.create(
                course=self.course,
                title=f'Lesson {i}',
                video_url='https://youtube.com/watch?v=x',
                owner=self.user,
            )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lesson-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_page_size_query_param(self):
        for i in range(6):
            Course.objects.create(title=f'C{i}', owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('course-list'), {'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 2)
